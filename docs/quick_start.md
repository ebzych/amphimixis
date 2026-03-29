# Quick start

This guide will help you quickly start using **Amphimixis**.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ebzych/amphimixis.git
cd amphimixis
```

### 2. Build and install

```bash
uv build
pip install dist/*.whl --break-system-packages
```

## Prepare the working directory

**Amphimixis** requires a clean working directory to store configuration files and build artifacts.

Before running the tool, ensure your directory contains a valid `input.yml` configuration file.

- See the [configuration instructions](./config_instruction.md).

- Refer to the [input.yml example](./input.yml).

If your configuration uses remote machines with SSH keys, start `ssh-agent` in the current shell and add the needed keys manually before running the tool:

Example:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_remote_machine
```

## Run Amphimixis

Run `amixis` from your **working directory** by passing the project path as an argument.

### Basic usage

```bash
amixis /path/to/project
```

This command will perform the full workflow for the specified project directory:

- Analyze the project to detect CI systems, tests and etc.

- Build the project according to the generated configuration files.

- Profile the performance of the builds and collect execution statistics.

____

All of the steps listed above can also be performed individually. Below are examples for each operation.

#### Analyze project

```bash
amixis --analyze /path/to/project
```

#### Build project

```bash
amixis --build /path/to/project
```

#### Profile project

```bash
amixis --profile /path/to/project
```

To collect only specific perf events in the full pipeline, pass them after `--events`:

```bash
amixis /path/to/project --events cycles cache-misses
```

The same flag also works with the profiling-only mode:

```bash
amixis --profile /path/to/project --events cycles cache-misses
```

#### Use a custom configuration file

To use a configuration file other than the default `input.yml`, use the `--config` flag:

```bash
amixis --config=./my_input.yml /path/to/project
```

#### Compare two profiling results

Use `--compare` with two `.scriptout` files:

```bash
amixis --compare build1.scriptout build2.scriptout
```

Use `--max-rows` to limit how many symbols with the biggest delta are shown for each event:

```bash
amixis --compare build1.scriptout build2.scriptout --max-rows 10
```

Use `--events` with `--compare` to display only the selected events:

```bash
amixis --compare build1.scriptout build2.scriptout --events cycles cache-misses
```
