# Usage guide

## Choose an installation method

For most users, the recommended path is to create a virtual environment and install directly from GitHub:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/ebzych/amphimixis.git
```

This is the recommended path if you only want to run `amixis` and do not want to install anything into the system Python environment.

If you are developing Amphimixis itself, clone the repository and install dependencies with `uv`:

```bash
git clone https://github.com/ebzych/amphimixis.git
cd amphimixis
uv sync
```

If you specifically want to build a wheel locally and test the packaged artifact, you can do that too:

```bash
python3 -m venv .venv
source .venv/bin/activate
uv build
pip install dist/*.whl
```

## Prepare a workspace

Run Amphimixis from a working directory that contains your configuration and any generated artifacts. Before starting, create an `input.yml` file there.

Make sure the required system tools are available before you run the pipeline:

### Install dependencies

- `rsync` on the machine where Amphimixis runs
- `perf` in `PATH`
- `perf archive` on each `run_machine`
- `sshpass` if your remote connections use passwords

```bash
sudo apt install rsync sshpass linux-tools-common linux-tools
```

### Create configuration file

- Configuration reference: [config_instruction.md](./config_instruction.md)
- Example file: [input.yml](./input.yml)

### Understand the expected configuration

At minimum, `input.yml` should describe:

- the build system and runner
- the target platforms
- the build recipes
- the builds that connect platforms and recipes

In `builds`, you can optionally specify an `executables` list for each build. Each path must be relative to that build's output directory, for example `bin/my_app`. If `executables` is omitted, Amphimixis profiles the first executable file it finds in the build directory.

If your configuration uses remote machines authenticated with SSH keys, start `ssh-agent` in the current shell and add the required keys before running the tool:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_remote_machine
```

## Run the main workflow

To analyze, build, and profile a project in one command:

```bash
amixis /path/to/project
```

The full pipeline:

1. analyzes the project
1. builds it using the selected configuration
1. profiles the resulting executables
1. prints profiling results in the console

## Run individual commands

Analyze only:

```bash
amixis --analyze /path/to/project
```

Build only:

```bash
amixis --build /path/to/project
```

Profile only:

```bash
amixis --profile /path/to/project
```

Validate a configuration file:

```bash
amixis --validate ./input.yml
```

Use a custom configuration file:

```bash
amixis --config ./my_input.yml /path/to/project
```

## Work with perf events

To record only selected `perf` events in the full pipeline:

```bash
amixis /path/to/project --events cycles cache-misses
```

The same flag works with profiling-only mode:

```bash
amixis --profile /path/to/project --events cycles cache-misses
```

With the main pipeline or `--profile`, `--events` tells `perf record` which events to collect.

## Compare profiling outputs

To compare two collected `.scriptout` files:

```bash
amixis --compare build1.scriptout build2.scriptout
```

To limit how many symbols with the largest delta are shown for each event:

```bash
amixis --compare build1.scriptout build2.scriptout --max-rows 10
```

To compare only selected events:

```bash
amixis --compare build1.scriptout build2.scriptout --events cycles cache-misses
```

With `--compare`, `--events` filters the output to the listed events.
