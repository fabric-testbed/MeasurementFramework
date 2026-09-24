# Report on the mflib_mcp service's current state.

import mflib_mcp_utilities as mu


def main():
    running = mu.is_mcp_container_running()
    ret_val = {
        "success": True,
        "container": mu.MCP_CONTAINER,
        "running": running,
        "mcp_path": "/mcp",
        "has_token_file": mu.get_token_from_file() is not None,
    }
    print(mu.get_json_string(ret_val))


if __name__ == "__main__":
    main()
