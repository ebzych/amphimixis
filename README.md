[![CI](https://github.com/ebzych/amphimixis/actions/workflows/ci.yml/badge.svg)](https://github.com/ebzych/amphimixis/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-available-blue)](https://github.com/ebzych/amphimixis/tree/main/docs)
[![License](https://img.shields.io/github/license/ebzych/amphimixis?color=8A2BE2)](https://github.com/ebzych/amphimixis/blob/main/LICENSE)

<p align="center">
  <img src="docs/logo.jpg" alt="Amphimixis Logo" width="800"><br>
</p>

# Amphimixis

Amphimixis is automated project intelligence and evaluation tool for perfomance and migration readiness. It helps inspect a project for existing infrastructure such as CI, tests, benchmarks, dependencies, and build scripts, then runs builds and collects performance data for further comparison.

> Amphimixis is currently in a very early pre-release state.

## Quick Run

If you want to try Amphimixis right away, create a virtual environment, install the package from GitHub, and run the full pipeline on a target project:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/ebzych/amphimixis.git
amixis /path/to/project
```

Before you run it, make sure your project has an `input.yml` configuration file. The format is described in [docs/config_instruction.md](docs/config_instruction.md).

If your `input.yml` contains remote machines authenticated with SSH keys, start `ssh-agent` in the current shell and add the required keys manually before running `amixis`:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_remote_machine
```

## Installation

### Install from GitHub

```bash
pip install git+https://github.com/ebzych/amphimixis.git
```

### Requirements

- Python 3.12 or newer
- Linux
- `perf` available in `PATH` for profiling
- A supported build setup in the target project: CMake as the build system and Make as the low-level runner

### Install for development

```bash
git clone https://github.com/ebzych/amphimixis.git
cd amphimixis
uv sync
```

## What Amphimixis Does

Amphimixis can:

- analyze a project for CI, tests, benchmarks, build system configuration, and dependencies
- build the project with configured recipes and platforms
- profile executable runs and collect timing and `perf`-based statistics
- compare profiling outputs produced for different builds

## Typical Usage

Prepare a working directory with an `input.yml` configuration file. The configuration format is described in [docs/config_instruction.md](docs/config_instruction.md).

Run the full workflow for a project:

```bash
amixis /path/to/project
```

This command:

1. analyzes the project
1. builds it using the selected configuration
1. profiles the resulting executables
1. prints profiling results in the console

You can also run individual steps:

```bash
amixis --analyze /path/to/project
amixis --build /path/to/project
amixis --profile /path/to/project
amixis --validate ./input.yml
```

To use a custom configuration file:

```bash
amixis --config ./my_input.yml /path/to/project
```

To compare two collected `perf` outputs:

```bash
amixis --compare build1.scriptout build2.scriptout --max-rows 10
```

## Build And Run Notes

The tool is distributed as a Python package with the `amixis` CLI entry point.

For local development and reproducible checks, the repository uses `uv` and GitHub Actions. The CI configuration is available in [.github/workflows/ci.yml](.github/workflows/ci.yml).

Useful commands during development:

```bash
uv run amixis --help
uv run pytest
```

If you want a more step-by-step walkthrough, see [docs/quick_start.md](docs/quick_start.md).

## Project Structure

The repository is organized around a small CLI and several core modules:

- [amixis.py](amixis.py) is the command-line entry point
- [amphimixis/analyzer.py](amphimixis/analyzer.py) inspects a target project
- [amphimixis/builder.py](amphimixis/builder.py) runs configured builds
- [amphimixis/profiler.py](amphimixis/profiler.py) gathers execution and profiling data
- [amphimixis/validator.py](amphimixis/validator.py) validates `input.yml`
- [amphimixis/shell](amphimixis/shell) contains local and remote shell backends
- [docs](docs) contains user-facing documentation

## Documentation

Additional documentation:

- [docs/quick_start.md](docs/quick_start.md)
- [docs/config_instruction.md](docs/config_instruction.md)

## How To Help

Contributions are welcome.

- Report bugs and suggest improvements through GitHub Issues
- Open a Pull Request with a clear description of the problem and the proposed change
- Add or improve tests for new behavior
- Update documentation when changing CLI behavior or configuration format

Before contributing, make sure local checks pass:

```bash
ci/runner.sh
```

## License

The project is distributed under the license in [LICENSE](LICENSE).
