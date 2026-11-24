# Measurement Node Binaries

Pre-built `~/.local` and `~/.ansible` bundles for `mfuser`, packaged as tarballs so a fresh meas-node can bootstrap
ansible (and the ansible-driven Docker install) without hitting apt/pip/Ansible Galaxy over the network on every
node's first boot. `install_ansible.sh` extracts one of these straight into `/` to seed `mfuser`'s environment.

## Naming: one tarball per base image

Each tarball is named `meas_node_binaries_<image_name>.tgz`, where `<image_name>` is the exact FABRIC image name it
was built against (e.g. `default_ubuntu_24`).

This matters because the tarball bakes in a `~/.local/lib/python3.X/site-packages/...` path. If a tarball built
against one Python version gets extracted onto a node running a different Python version, `ansible`/`ansible-playbook`
fail with `ModuleNotFoundError: No module named 'ansible'` -- the executable's shebang resolves to the node's
`python3`, but the installed packages only exist under the *build machine's* `python3.X` site-packages directory. Keep
a separate tarball per image rather than trying to share one across image versions.

## (Re)building a tarball

Rebuild whenever a base image's default Ubuntu/Python version changes -- don't assume an existing tarball still
matches after an image update.

- [`build_meas_node_binaries.ipynb`](../build_meas_node_binaries.ipynb) -- provisions a throwaway FABRIC VM on a
  chosen image, sets up `mfuser`, runs the build script, and downloads the resulting tarball. This is the normal way
  to produce one.
- [`build_meas_node_binaries.sh`](../build_meas_node_binaries.sh) -- the actual build steps (apt/pip install of
  `ansible` from `requirements.txt`, `ansible-galaxy` role/collection install from `requirements.yml`, then
  `tar czf` of `~/.local` + `~/.ansible`). Must be run as `mfuser` on a machine matching the target image. Takes the
  image name as an optional argument, which gets tagged onto the output filename.

## Checking what a tarball was built against

Every tarball includes `home/mfuser/.mf_binaries_build_info`, recording the build timestamp, Python version, Ansible
version, and OS release:

```
tar xzf meas_node_binaries_<image_name>.tgz -O home/mfuser/.mf_binaries_build_info
```

(`-O` must come before the member path on Windows' bundled bsdtar, or it's misread as another archive member to
extract and fails with `Not found in archive`.)

Check this before assuming an existing tarball is still valid for a given node image.

## Which tarball actually gets used

`install_ansible.sh` looks for an empty marker file named `os_image_<image_name>` in `mfuser`'s home dir (FABRIC
images drop this to record which base image the node was built from). If `meas_node_binaries_<image_name>.tgz` exists
here, it's used. Otherwise -- no marker file, or no matching tarball -- it falls back to the tarball pinned in the
`MEAS_NODE_BINARIES_TGZ` variable near the bottom of the script. When you build a new tarball for a different (or
updated) image, no script change is needed as long as the marker file's `<image_name>` matches the tarball's; update
`MEAS_NODE_BINARIES_TGZ` only if you also want it to become the new fallback default.

The old flat `../meas_node_binaries.tgz` (parent directory, no image name) was built against Python 3.8 and is stale
-- it's unused now that `install_ansible.sh` points here instead, and should be deleted once nothing references it.
