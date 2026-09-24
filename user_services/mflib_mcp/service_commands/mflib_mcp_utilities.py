import json
import os
import secrets
import subprocess

this_service_dir = os.path.dirname(os.path.realpath(__file__))
services_dir = os.path.join(os.path.expanduser("~"), "services")

# mfportal drops the token it will use to talk to this service here before
# create.py runs -- same pattern as meas_node_server's mflib_api_token (see
# meas_node_server_utilities.TOKEN_FILE_PATH). Only ever written by
# _write_portal_registration_json() in claude-mflib-portal's
# _run_create_meas_node_slice(), which only runs as part of the portal's
# automated meas-node creation flow -- so this file's presence is also what
# distinguishes a self-start-created node from a hand-created one, though
# create.py below still works (with a locally-generated token) if it's absent.
TOKEN_FILE_PATH = "/home/mfuser/mflib_mcp_token"

REPO_URL = "https://github.com/fabric-testbed/mflib_portal_mcp.git"
REPO_DIR = os.path.join(services_dir, "mflib_mcp", "mflib_portal_mcp")

# Must match the fabric_experiment Ansible role's defaults/main.yml
# (install_name / docker_network_name) -- see
# instrumentize/prometheus/ansible/roles/fabric_experiment/defaults/main.yml.
# Hardcoded rather than discovered because mflib_portal_mcp's own shipped
# defaults (GRAFANA_CONTAINER, MONITORING_NETWORK) already hardcode the same
# assumption -- a deployment that overrides install_name would need to
# override both anyway.
INSTALL_NAME = "fabric_prometheus"
BASE_INSTALL_DIR = f"/opt/{INSTALL_NAME}"
NGINX_CONFD_FILE = f"{BASE_INSTALL_DIR}/nginx/conf.d/grafana_with_ssl_only.conf"
NGINX_CONTAINER = f"{INSTALL_NAME}-nginx"
MCP_CONTAINER = f"{INSTALL_NAME}-mflib_mcp"

MCP_LOCATION_MARKER = "# --- mflib_mcp location (managed by user_services/mflib_mcp/create.py) ---"
MCP_LOCATION_END = "# --- end mflib_mcp location ---"


def get_token_from_file():
    try:
        with open(TOKEN_FILE_PATH) as f:
            token = f.read().strip()
        return token or None
    except Exception:
        return None


def write_token_to_file(token):
    # Standalone fallback: lets `mflib.create("mflib_mcp")` work even when
    # called by hand (no portal, no self-start, no pre-dropped token) --
    # generates its own credential so the nginx location still gets a real
    # bearer check instead of silently having none.
    with open(TOKEN_FILE_PATH, "w") as f:
        f.write(token)
    os.chmod(TOKEN_FILE_PATH, 0o600)


def get_json_string(data):
    try:
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"json_error": "Data was unable to be converted to a JSON string",
                            "json_exception": type(e).__name__})


def clone_or_update_repo():
    if os.path.isdir(os.path.join(REPO_DIR, ".git")):
        subprocess.run(
            ["git", "-C", REPO_DIR, "pull", "--ff-only"],
            check=True, capture_output=True, text=True,
        )
    else:
        os.makedirs(os.path.dirname(REPO_DIR), exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, REPO_DIR],
            check=True, capture_output=True, text=True,
        )


def compose_up():
    # mflib_portal_mcp's own shipped docker-compose.yml already joins the
    # external fabric_prometheus network and publishes on loopback only --
    # used completely unmodified. No .env changes needed either: its shipped
    # defaults (GRAFANA_CONTAINER=fabric_prometheus-grafana,
    # MONITORING_NETWORK=fabric_prometheus) already match this role's naming.
    #
    # sudo: mfuser is never added to the `docker` group anywhere in this
    # repo's bootstrap (geerlingguy.docker's docker_users isn't set) --
    # every other docker invocation from a service_commands script in this
    # codebase (e.g. grafanaUtilities.set_grafana_csrf_trusted_origin())
    # goes through sudo for the same reason.
    subprocess.run(
        ["sudo", "docker", "compose", "up", "-d", "--build"],
        cwd=REPO_DIR, check=True, capture_output=True, text=True,
    )


def compose_down():
    subprocess.run(
        ["sudo", "docker", "compose", "down"],
        cwd=REPO_DIR, check=True, capture_output=True, text=True,
    )


def is_mcp_container_running():
    result = subprocess.run(
        ["sudo", "docker", "inspect", "-f", "{{.State.Running}}", MCP_CONTAINER],
        capture_output=True, text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def _location_block(token: str) -> str:
    return "\n".join([
        MCP_LOCATION_MARKER,
        "location /mcp {",
        f'    if ($http_authorization != "Bearer {token}") {{ return 401; }}',
        f"    proxy_pass http://{MCP_CONTAINER}:8000;",
        "    proxy_http_version 1.1;",
        "    proxy_set_header Host $host;",
        "    proxy_buffering off;",
        "    proxy_read_timeout 300s;",
        "    proxy_send_timeout 300s;",
        "    chunked_transfer_encoding on;",
        "}",
        MCP_LOCATION_END,
        "",
    ]) + "\n"


def _strip_existing_block(content: str) -> str:
    if MCP_LOCATION_MARKER not in content:
        return content
    start = content.index(MCP_LOCATION_MARKER)
    end = content.index(MCP_LOCATION_END) + len(MCP_LOCATION_END)
    # also eat one trailing newline so re-inserting doesn't accumulate blank lines
    while end < len(content) and content[end] == "\n":
        end += 1
    return content[:start] + content[end:]


def _read_confd_file() -> str:
    # Owned by prom_user_name (fab-prom), not mfuser -- ansible's template
    # task doesn't pin an explicit mode, so this is normally still
    # group/world-readable (0644-ish) and a plain open() works. Falls back
    # to a sudo read for a deployment where that assumption doesn't hold.
    try:
        with open(NGINX_CONFD_FILE) as f:
            return f.read()
    except PermissionError:
        result = subprocess.run(
            ["sudo", "cat", NGINX_CONFD_FILE],
            check=True, capture_output=True, text=True,
        )
        return result.stdout


def install_nginx_location(token: str):
    """Idempotently insert the /mcp location into the currently-active confd
    file (grafana_with_ssl_only.conf -- the one this role's
    fabric_experiment_install_tasks.yml actually enables today), just before
    its server block's closing brace, then reload nginx.

    Safe to re-run: replaces any previously-installed block (e.g. if the
    token changed) rather than duplicating it. Reads directly (the file is
    group/world-readable, per config_nginx_tasks.yml's template task) but
    writes via sudo, since it's owned by prom_user_name (fab-prom), not
    mfuser.
    """
    content = _read_confd_file()

    content = _strip_existing_block(content)

    last_brace = content.rstrip().rfind("}")
    if last_brace == -1:
        raise RuntimeError(f"{NGINX_CONFD_FILE}: no closing '}}' found -- refusing to guess where to insert")

    new_content = content[:last_brace] + _location_block(token) + content[last_brace:]

    tmp_path = f"/tmp/{os.path.basename(NGINX_CONFD_FILE)}.mflib_mcp.tmp"
    with open(tmp_path, "w") as f:
        f.write(new_content)

    subprocess.run(["sudo", "cp", tmp_path, NGINX_CONFD_FILE], check=True, capture_output=True, text=True)
    os.remove(tmp_path)

    # Validate before restarting so a bad config doesn't take the whole
    # proxy down -- if this fails, NGINX_CONFD_FILE has already been
    # overwritten but the running nginx process is untouched.
    subprocess.run(
        ["sudo", "docker", "exec", NGINX_CONTAINER, "nginx", "-t"],
        check=True, capture_output=True, text=True, timeout=15,
    )
    # docker restart, not `nginx -s reload` via exec, to match this
    # codebase's existing precedent for applying nginx config changes
    # (grafanaUtilities.set_grafana_csrf_trusted_origin()) -- WITH a
    # timeout this time (that precedent's missing timeout was flagged as a
    # real bug: a hang there blocks create.py forever with no error).
    subprocess.run(
        ["sudo", "docker", "restart", NGINX_CONTAINER],
        check=True, capture_output=True, text=True, timeout=30,
    )


def remove_nginx_location():
    """Reverse of install_nginx_location() -- strips the managed block if
    present and reloads nginx. A no-op (no error) if the file doesn't exist
    or never had the block."""
    if not os.path.exists(NGINX_CONFD_FILE):
        return
    content = _read_confd_file()
    new_content = _strip_existing_block(content)
    if new_content == content:
        return  # nothing to remove

    tmp_path = f"/tmp/{os.path.basename(NGINX_CONFD_FILE)}.mflib_mcp.tmp"
    with open(tmp_path, "w") as f:
        f.write(new_content)
    subprocess.run(["sudo", "cp", tmp_path, NGINX_CONFD_FILE], check=True, capture_output=True, text=True)
    os.remove(tmp_path)
    subprocess.run(
        ["sudo", "docker", "exec", NGINX_CONTAINER, "nginx", "-t"],
        check=True, capture_output=True, text=True, timeout=15,
    )
    subprocess.run(
        ["sudo", "docker", "restart", NGINX_CONTAINER],
        check=True, capture_output=True, text=True, timeout=30,
    )


def generate_token() -> str:
    return secrets.token_urlsafe(32)
