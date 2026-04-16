# Configuration file guide

This guide explains how to create and configure your project’s configuration file.

See an example configuration file [here](./input.yml).

## General structure

The YAML configuration file consists of the following **top-level fields**:

|                     Field                     |         Type         | Description                                                          |
| :-------------------------------------------: | :------------------: | -------------------------------------------------------------------- |
| build_system<sup><a href="#note1">1</a></sup> |        string        | (**Optional**) Name of the build system                              |
|    runner<sup><a href="#note2">2</a></sup>    |        string        | (**Optional**) Name of the runner (low-level build system)           |
|                   platforms                   | list of dictionaries | Describes the platforms used for building and running the project    |
|                    recipes                    | list of dictionaries | Build configuration parameters                                       |
|                    builds                     | list of dictionaries | Describes builds tasks                                               |

---

<p id="note1">

1. <code>CMake</code> and <code>Make</code> are supported as build systems. If not specified, it is automatically selected from the set of build systems supported by the project.

</p>
<p id="note2">

2. <code>Make</code> and <code>Ninja</code> are supported as runners (low-level build system). If not specified, it is automatically selected from the supported runners of the selected build system.

</p>

```yaml
build_system: CMake
runner: Make
platforms: [{}]
recipes: [{}]
builds: [{}]
```

### Platforms

The **platforms** section describes the machines on which the project will be built and run.

|                   Field                   |  Type   | Description                                    |
| :---------------------------------------: | :-----: | ---------------------------------------------- |
|                    id                     | integer | Unique id of the platform                      |
|                   arch                    | string  | Architecture (e.g. x86, riscv)                 |
|                  address                  | string  | (**Optional**) IP address or domain name       |
|                 username                  | string  | (**Optional**) Username of the remote machine  |
|   port<sup><a href="#note3">3</a></sup>   | integer | (**Optional**) Port of the remote machine      |
| password<sup><a href="#note4">4</a></sup> | string  | (**Optional**) Password for the remote machine |

---

<p id="note3">

3. Default value: 22. The `port` must be within the range 1-65535.

</p>
<p id="note4">

4. If the user uses SSH keys, start `ssh-agent` in the current shell and add the required keys for each remote machine manually with `ssh-add` before running Amphimixis. In this case, the password does not need to be provided. **Please note that passwords are passed to SSH through sshpass, which is not secure.**

</p>

> **<u>Note:</u>**
>
> - If the `address` field is not specified, the local machine is assumed.
> - For a local machine, `username`, `password`, and `port` do not need to be specified.
> - If an `address` is specified, the machine is treated as remote, and the fields `username`, `password`, and `port` must be provided.
> - If you connect with SSH keys instead of a password, run `eval "$(ssh-agent -s)"` and then add the keys for the target machines manually, for example `ssh-add ~/.ssh/id_remote_machine`, before starting Amphimixis.

### Recipes

The **recipes** section describes the build configuration and compiler flags.

|                  Field                          |  Type   | Description                                                                               |
| :---------------------------------------------: | :-----: | ----------------------------------------------------------------------------------------- |
| id                                              | integer | Unique ID of the recipe                                                                   |
| config_flags                                    | string  | (**Optional**) Build configuration options                                                |
| compiler_flags<sup><a href="#note5">5</a></sup> | dict    | (**Optional**) Compiler flags used during the build process                               |
| toolchain<sup><a href="#note6">6</a></sup>      |  dict   | (**Optional**) Path to the toolchain used for building the project                        |
| sysroot                                         | string  | (**Optional**) Path to the folder with system headers and libraries used by the toolchain |
| jobs                                            | integer | (**Optional**) Number of parallel jobs used by the build system                           |

<p id="note5">

<details>
<summary>5. Possible attributes:</summary>

- c_flags
- cxx_flags
- csharp_flags
- cuda_flags
- objc_flags
- objcxx_flags
- fortran_flags
- hip_flags
- ispc_flags
- swift_flags
- asm_flags
- asm_nasm_flags
- asm_marmasm_flags
- asm_masm_flags
- asm_att_flags

</details>

</p>

<p id="note6">

<details>
<summary>6. Possible attributes of a toolchain:</summary>

- ar
- as
- ld
- nm
- objcopy
- objdump
- ranlib
- readelf
- strip
- c_compiler
- cxx_compiler
- csharp_compiler
- cuda_compiler
- objc_compiler
- objcxx_compiler
- fortran_compiler
- hip_compiler
- ispc_compiler
- swift_compiler
- asm_compiler
- asm_nasm_compiler
- asm_marmasm_compiler
- asm_masm_compiler
- asm_att_compiler

</details>

<details>
<summary>You can also specify flags to the toolchain:</summary>

- c_flags
- cxx_flags
- csharp_flags
- cuda_flags
- objc_flags
- objcxx_flags
- fortran_flags
- hip_flags
- ispc_flags
- swift_flags
- asm_flags
- asm_nasm_flags
- asm_marmasm_flags
- asm_masm_flags
- asm_att_flags

</details>

</p>

### Builds

The **builds** section links platforms and recipes, defining which configurations should be built on which machines.

|     Field                                      |  Type   | Description                                                                |
| :--------------------------------------------: | :-----: | -------------------------------------------------------------------------- |
| build_machine                                  | integer | `platform_id` of the machine where the project will be built               |
| run_machine                                    | integer | `platform_id` of the machine where the built project will be executed      |
| recipe_id                                      | integer | ID of the `recipe`                                                         |
| executables<sup><a href="#note7">7</a></sup>   |  list   | (**Optional**) List of executables to profile for this build               |

---

<p id="note7">

7. Each path in `executables` must be specified relative to the build directory created for this build. For example, use `bin/app` rather than an absolute path. If `executables` is not specified, Amphimixis will profile the first executable file it finds in the build directory.

</p>

Example:

```yaml
builds:
  - build_machine: 1
    run_machine: 1
    recipe_id: 1
    executables:
      - bin/my_app
      - tests/my_benchmark
```

Example:

```yaml
# Define a reusable list of executables
executables: &my_executables
  - bin/my_app
  - tests/my_benchmark

builds:
  - build_machine: 1
    run_machine: 1
    recipe_id: 1
    executables: *my_executables   # reference the list above
```

> **<u>Note:</u>**
>
> - YAML references (& and *) let you reuse the same `executables` list across multiple builds, reducing duplication.
