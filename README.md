[![CI](https://github.com/ebzych/amphimixis/actions/workflows/ci.yml/badge.svg)](https://github.com/ebzych/amphimixis/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-available-blue)](https://github.com/ebzych/amphimixis/tree/main/docs)
[![License](https://img.shields.io/github/license/ebzych/amphimixis?color=8A2BE2)](https://github.com/ebzych/amphimixis/blob/main/LICENSE)

<p align="center">
  <img src="docs/logo.jpg" alt="Amphimixis Logo" width="800"><br>
</p>

# Amphimixis

Amphimixis is a tool that automates project builds and helps to analyze application performance. It is designed to simplify the build process and compare results across different platforms.

!!!Amphimixis in the pre-pre-pre-pre-pre-alpha version!!!

- [Quick start](docs/quick_start.md)
- [Config instruction](docs/config_instruction.md)

Amphimixis can:

- Analyze a project for the presence of:

   - CI
   - Tests
   - Benchmarks
   - Builds system
   - Dependencies

- Automatically compile the project with various specified configurations. Amphimixis supports the following build systems:

   - CMake
   - Make

- Using known profiling methods such as perf, flamegraph, collect data on:

   - Functions that take the most time to execute
   - Measure the execution time
