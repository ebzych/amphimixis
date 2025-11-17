# Example configuration file

This is an example file that describes the project's build and run parameters.
It includes build system settings, a list of platforms (devices or machines), compilation options, and build configurations.

See the instructions to create your own configuration file [here](./config_instruction.md).

```Yaml
build_system: CMake
runner: mAkE
platforms:
- id: 1
  address: 192.168.1.1
  arch: x86
  username: ebzych
  port: 22
  password: 'ilovemarie'
- id: 2
  address: 192.168.1.2
  arch: riscv
  username: fojdjebu
  password: 'iloveriscv'
  port: 22
- id: 3
  address: 192.168.1.3
  arch: x86
  username: enderlay
  password: 'ilovecats'

recipes:
- id: 1
  config_flags: "-DCMAKE_BUILD_TYPE=Release -DYAML_CPP_BUILD_TESTS=ON"
  compiler_flags: "-ftree-vectorize"
- id: 2
  config_flags: "-DCMAKE_BUILD_TYPE=Debug -DYAML_CPP_BUILD_TESTS=ON "
  compiler_flags: "-O0"
- id: 3
  config_flags: "-DCMAKE_BUILD_TYPE=Release"
  compiler_flags: "-ftree-vectorize"

builds:
- build_machine: 1
  toolchain: /path/to/your/target/toolchain
  sysroot: /path/to/your/target/sysroot
  run_machine: 1
  recipe_id: 1
- build_machine: 2
  run_machine: 2
  recipe_id: 3
```
