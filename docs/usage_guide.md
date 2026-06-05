# Usage guide

## Table of Contents

- [Choose an installation method](#choose-an-installation-method)
- [Prepare a workspace](#prepare-a-workspace)
- [Run the main workflow](#run-the-main-workflow)
- [Run individual commands](#run-individual-commands)
- [Work with perf events](#work-with-perf-events)
- [Compare profiling outputs](#compare-profiling-outputs)
- [Add a toolchain](#add-a-toolchain)
- [Clean build directories](#clean-build-directories)

---

> If you encounter issues while using Amphimixis, see [Troubleshooting](troubleshooting.md) for common problems and solutions.

## Choose an installation method

For most users, the recommended path is to create a virtual environment and install directly from GitHub:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/ebzych/amphimixis.git@stable
```

This is the recommended path if you only want to run `amixis` and do not want to install anything into the system Python environment.

If you are developing Amphimixis itself, clone the repository and install dependencies with `uv`:

```bash
git clone https://github.com/ebzych/amphimixis.git
cd amphimixis
uv sync
```

If you specifically want to build a wheel locally and test the packaged artifact, use:

```bash
python3 -m venv .venv
source .venv/bin/activate
uv build
pip install dist/*.whl
```

## Prepare a workspace

Run Amphimixis from a working directory that contains your configuration and any generated artifacts. Before starting, create an `input.yml` file there.

### Make sure the required system tools are available

Required tools: `rsync` on each machine, `perf` and `perf archive` on each `run_machine`, and optionally `sshpass` for password-based SSH connections.

See [Troubleshooting → System Dependencies](troubleshooting.md) for installation commands and the `perf archive` setup.

### Create a configuration file

- Start using provided config file sample

  ```bash
  amixis init sample-name
  ```

  Available sample name:
  - local
  - distributed
  - distributed-cross

- Or create config with template:

  ```bash
  amixis add input
  ```

- Configuration reference: [config_instruction.md](./config_instruction.md)
- Example file: [input.yml](./input.yml)

### Understand the expected configuration

At minimum, `input.yml` should describe:

- the build system and runner
- the target platforms
- the build recipes
- the builds that connect platforms and recipes

In `builds`, you can optionally specify an `executables` list for each build. Each path must be relative to that build's output directory, for example `bin/my_app`. If `executables` is omitted, Amphimixis profiles the first executable file it finds in the build directory.

### Using SSH keys

You can use Amphimixis with SSH keys. See [Troubleshooting: sshpass not found](troubleshooting.md#sshpass-not-found) for setup.

## Run the main workflow

```bash
amixis run /path/to/project
```

Use `--config` to specify a custom configuration file path:

```bash
amixis run --config ./my_input.yml /path/to/project
```

The full pipeline:

1. analyzes the project
1. builds it using the selected configuration
1. profiles the resulting executables
1. prints profiling results in the console

## Run individual commands

Analyze only:

```bash
amixis analyze /path/to/project
```

Build only:

```bash
amixis build /path/to/project
```

Profile only:

```bash
amixis profile /path/to/project
```

Validate a configuration file:

```bash
amixis validate /path/to/input/config
```

## Work with perf events

The same flag works with profiling-only mode:

```bash
amixis profile /path/to/project --events cycles cache-misses
```

With the main pipeline or `profile`, `--events` tells `perf record` which events to collect.

## Compare profiling outputs

To compare two collected `.scriptout` files:

```bash
amixis compare build1.scriptout build2.scriptout
```

To limit how many symbols with the largest delta are shown for each event:

```bash
amixis compare build1.scriptout build2.scriptout --max-rows 10
```

## Add a toolchain

Add a new toolchain to the global configuration file:

```bash
amixis add toolchain
```

## Clean build directories

If you want to clean up on your build directories from previous builds, use:

```bash
# To interactively select builds to clean
amixis clean

# To clean specific builds by name
amixis clean build-name-1 build-name-2 ...

# To clean all builds
amixis clean --all
```
