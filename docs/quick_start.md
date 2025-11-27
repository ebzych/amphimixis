# Quick start 

This guide will help you quickly start using **Amphimixis**.

After [installing](./installation.md) Amphimixis and preparing a configuration file according to the [instructions](./config_instruction.md), you can easily start using it to automate builds and profile your projects.

## Prepare the working directory

Amphimixis should be run **from a clean working directory** where all configuration files and build artifacts will be stored. 
Before running Amphimixis, make sure that the directory contains a valid `input.yml` configuration file created following the [instructions](./config_instruction.md).

## Run Amphimixis

To start using Amphimixis, execute the `amixis.py` file (which contains the CLI logic) **from your working directory**, and pass the path to your project as an argument. 

### Basic usage

```bash
../amphimixis/amixis.py /path/to/project
```

This command will perform the full workflow for the specified project directory. Amphimixis will:

- Analyze the project to detect CI systems, tests and etc.

- Generate configuration files based on `input.yml` (or a custom config if provided).

- Build the project according to the generated configuration files.

- Profile the performance of the builds and collect execution statistics.

All of the steps listed above can also be performed individually. Below are examples for each operation.

#### Analyze only

```bash
../amphimixis/amixis.py --analyze /path/to/project
```

#### Generate configuration files

```bash
../amphimixis/amixis.py --configure /path/to/project
```

#### Build project

```bash
../amphimixis/amixis.py --build /path/to/project
```

> **💡:** This command builds the project according to the configuration files. It implicitly runs `--configure` if the configuration files do not yet exist, ensuring the build completes successfully.

#### Profile project

```bash
../amphimixis/amixis.py --profile /path/to/project
```

#### Use a custom configuration file

You can specify a **custom configuration file** (different from `input.yml`) by passing path to the file with the `--config` argument:

```bash
../amphimixis/amixis.py --config=./my_input.yml /path/to/project
```

