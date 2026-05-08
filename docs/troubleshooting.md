# Troubleshooting

This page covers common issues and their solutions when using Amphimixis.

## Table of Contents

- [Installation](#installation)
- [System Dependencies](#system-dependencies)
- [Build Failures](#build-failures)
- [Configuration Failures](#configuration-failures)
- [Profiling Failures](#profiling-failures)

## Installation

### `pip install` fails with a Python version error

Amphimixis requires **Python 3.12 or later**. Check your version:

```bash
python3 --version
```

If your system Python is older, install a newer version or use `uv` to manage Python versions:

```bash
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate
pip install git+https://github.com/ebzych/amphimixis.git@stable
```

### The `amixis` command is not found after installation

The entry point may not be on your `PATH`. Activate the virtual environment where you installed the package:

```bash
source .venv/bin/activate
amixis --help
```

If you installed with `pip install --user`, ensure `~/.local/bin` is on your `PATH`.

## System Dependencies

### `perf` command not found

`perf` is part of the Linux kernel tools package. Install it **on each machine** where profiling will run:

```bash
apt install linux-tools-common linux-tools-generic
```

### `perf archive` is not available

Some distributions (notably Ubuntu) ship `perf` without `perf archive`. This script is required to resolve build IDs after profiling. Fix it by downloading the script from the Linux kernel repository:

```bash
sudo mkdir -p /usr/libexec/perf-core
curl -s https://raw.githubusercontent.com/torvalds/linux/master/tools/perf/perf-archive.sh | sudo tee /usr/libexec/perf-core/perf-archive
sudo chmod +x /usr/libexec/perf-core/perf-archive
```

See the [original discussion](https://linux-perf-users.vger.kernel.narkive.com/gjAAds7D/perf-archive-is-not-a-perf-command).

### `rsync` not found on remote machine

`rsync` must be installed **on each machine** referenced in your `input.yml`:

```bash
apt install rsync
```

### `sshpass` not found

`sshpass` is required only when connecting to remote machines with password authentication. Install it on the machine where you run Amphimixis:

```bash
apt install sshpass
```

If your configuration uses remote machines authenticated with SSH keys, start ssh-agent in the current shell and add the required keys before running the tool:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_remote_machine
```

## Build Failures

### Unsupported build system detected

Amphimixis currently supports **CMake** and **Make** as build systems, with **Make** and **Ninja** as runners. If your project uses a different build system (e.g., Meson, Gradle, Bazel), you can still try specifying CMake explicitly in `input.yml` if a `CMakeLists.txt` exists:

```yaml
build_system: CMake
runner: Make
```

### CMake configuration fails

Common causes:

- Missing `CMakeLists.txt` in the project root
- Missing dependencies (libraries, headers) referenced in `CMakeLists.txt`
- Toolchain not available on the build machine

Check the build log in `amphimixis.log` for the exact error.

### Build succeeds but no executable is found

In `builds`, you can optionally specify an `executables` list for each build. Each path must be relative to that build's output directory, for example `bin/my_app`. If `executables` is omitted, Amphimixis profiles the first executable file it finds in the build directory. To ensure the correct binary is profiled, specify it explicitly:

```yaml
builds:
  - build_machine: 1
    run_machine: 1
    recipe_id: 1
    executables:
      - bin/my_app
```

## Configuration Failures

### `input.yml` validation fails

Run the validator to see the exact error:

```bash
amixis validate /path/to/input.yml
```

Common mistakes:

- Missing required fields: `platforms`, `recipes`, `builds` must be non-empty lists
- `build_machine` or `run_machine` references a `platform_id` that does not exist
- `recipe_id` references a recipe that does not exist
- `port` outside the valid range (1-65535)

### What happens if `build_system` or `runner` is omitted

Amphimixis will auto-detect them from the target project. If the project has a `CMakeLists.txt`, CMake is selected. If a `Makefile` is found, Make is used. The runner defaults to Make if the build system is CMake, or to the project's native runner.

### How to reuse the same `executables` list across multiple builds

Use YAML anchors and aliases to avoid duplication:

```yaml
executables: &my_executables
  - bin/my_app
  - tests/my_benchmark

builds:
  - build_machine: 1
    run_machine: 1
    recipe_id: 1
    executables: *my_executables
  - build_machine: 1
    run_machine: 1
    recipe_id: 2
    executables: *my_executables
```

## Profiling Failures

### Empty or minimal profiling output

This can happen if:

- The executable runs too quickly for `perf` to collect meaningful samples
- The perf events specified with `--events` are not supported on the current hardware
- `perf_event_paranoid` is set too high

Check supported events:

```bash
perf list
```

Lower the paranoid level if needed (requires root):

```bash
echo '-1' | sudo tee /proc/sys/kernel/perf_event_paranoid
```

### `perf` reports "Permission denied"

Set the paranoid level to allow user-space profiling:

```bash
echo '-1' | sudo tee /proc/sys/kernel/perf_event_paranoid
```

This setting does not persist across reboots. To make it permanent, add to `/etc/sysctl.conf`:

```
kernel.perf_event_paranoid = -1
```

### Comparing outputs from different machines

The `amixis compare` command works with `.scriptout` files regardless of which machine they were collected on. Ensure both files use the same perf events for meaningful comparison:

```bash
amixis compare build1.scriptout build2.scriptout --max-rows 10
```
