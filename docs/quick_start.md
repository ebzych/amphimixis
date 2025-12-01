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

#### Use a custom configuration file

To use a configuration file other than the default `input.yml`, use the `--config` flag:

```bash
amixis --config=./my_input.yml /path/to/project
```
