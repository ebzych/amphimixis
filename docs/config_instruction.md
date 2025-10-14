# Configuration file guide

This guide explains how to create and configure your project’s build file. 

See an example configuration file [here](./config_example.md).

## General structure

The YAML configuration file consists of the following **top-level fields**:

| Field | Type | Description |
|:-------:|:------:|-------------|
| build_system<sup><a href="#note1">1</a></sup> | string | Name of build system |
| runner<sup><a href="#note2">2</a></sup> | string | Name of runner (low-level build system) |
| platforms | list of dictionary| Describes the platforms, which the user uses |
| recipes | list of dictionary| Build configuration parameters |
| builds | list of dictionary | Description of builds |
---

<p id="note1">
1. Only <code>CMake</code> is supported.
</p>
<p id="note2">
2. Only <code>Make</code> is supported.
</p>

```Yaml
build_system: CMake
runner: Make
platforms: [{}]
recipes: [{}]
builds: [{}]
```

### Platforms

The **platforms** section describes the machines on which the project will be built and run.  

| Field | Type | Description |
|:-------:|:------:|-------------|
| id | integer | Unique identificator of platform |
| ip | string | IP-address or domen |
| arch | string | Architecture (e.g., x86, riscv)
| username | string | Username of the remote machine |
| port<sup><a href="note3">3</a></sup>| integer | port of the remote machine |
| password<sup><a href="note4">4</a></sup> | integer | Password for the remote machine |
---

<p id="note3">
3. Optional, standart value "22".
</p>
<p id="note4">
4. Otional.
</p>


> **<u>Note:</u>**  
> - If the `ip` field is not specified, the local machine is assumed.  
> - For a local machine, `username`, `password`, and `port` do not need to be specified.  
> - If an `ip` is specified, the machine is treated as remote, and the fields `username`, `password`, and `port` must be provided.



