# Configuration file guide

This guide explains how to create and configure your project’s build file.

See an example configuration file [here](./input.yml).

## General structure

The YAML configuration file consists of the following **top-level fields**:

|                     Field                     |         Type         | Description                                 |
| :-------------------------------------------: | :------------------: | ------------------------------------------- |
| build_system<sup><a href="#note1">1</a></sup> |        string        | Name of the build system                    |
|    runner<sup><a href="#note2">2</a></sup>    |        string        | Name of the runner (low-level build system) |
|                   platforms                   | list of dictionaries | Describes the platforms used by the user    |
|                    recipes                    | list of dictionaries | Build configuration parameters              |
|                    builds                     | list of dictionaries | Describes of builds tasks                   |

---

<p id="note1">

1. **Optional field**. Only <code>CMake</code> is supported as the build system. Default value: CMake

</p>
<p id="note2">

2. **Optional field**. Only <code>Make</code> is supported as the runner (low-level build system). Default value: make
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

|                   Field                   |  Type   | Description                     |
| :---------------------------------------: | :-----: | ------------------------------- |
|                    id                     | integer | Unique id of the platform       |
|                  address                  | string  | IP-address or domain name       |
|                   arch                    | string  | Architecture (e.g. x86, riscv)  |
|                 username                  | string  | Username of the remote machine  |
|   port<sup><a href="#note3">3</a></sup>   | integer | Port of the remote machine      |
| password<sup><a href="#note4">4</a></sup> | string  | Password for the remote machine |

---

<p id="note3">

3. **Optional field**. Default value: "22". The `port` must be within the range 1-65535.  

</p>
<p id="note4">

4. If the user has an SSH agent, then the password does not need to be provided. **Please note that passwords are passed to SSH through sshpass, which is not secure.**

</p>


> **<u>Note:</u>**
>
> - If the `address` field is not specified, the local machine is assumed.
> - For a local machine, `username`, `password`, and `port` do not need to be specified.
> - If an `address` is specified, the machine is treated as remote, and the fields `username`, `password`, and `port` must be provided.

### Recipes

The **recipes** section describes the build configuration and compiler flags.

|                  Field                  |  Type   | Description                                  |
| :-------------------------------------: | :-----: | -------------------------------------------- |
|                   id                    | integer | Unique id of the recipes                     |
|              config_flags               | string  | Build configuration options                  |
|             compiler_flags              | string  | Compiler flags used during the build process |
| script<sup><a href="#note5">5</a></sup> | string  | Custom build script                          |

---

<p id="note6">

5. **Optional field**.

</p>

### Builds

The **builds** section links platforms and recipes, defining which configurations should be built on which machines.

|     Field     |  Type   | Description                                                                |
| :-----------: | :-----: | -------------------------------------------------------------------------- |
| build_machine | integer | `platform_id` of the machine where the project will be built               |
|   toolchain   | string  | Path to the toolchain used for building the project                        |
|    sysroot    | string  | Path to the folder with system headers and libraries used by the toolchain |
|  run_machine  | integer | `platform_id` of the machine where the built project will be executed      |
|   recipe_id   | integer | Id of the `recipe`                                                         |

---
