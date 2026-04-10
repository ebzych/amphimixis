"""Configuration and toolchain templates for Amphimixis CLI."""

CONFIG_TEMPLATE = """# Amphimixis Configuration Template
# Uncomment and fill the fields below:

# build_system:                 # Optional
# runner:                       # Low-level build system (optional)

platforms:
- id: 1                         # Unique platform id
  arch:                         # Architecture (e.g. x86, riscv, arm)
#   address:                    # IP/domain address (omit for local machine)
#   username:                   # SSH username (required for remote)
#   password:                   # SSH password (or use SSH keys)
#   port: 22                    # SSH port (optional, default: 22)

recipes:
- id: 1                                              # Unique recipe id
  config_flags: "-DCMAKE_BUILD_TYPE=RelWithDebInfo"  # Build configuration options
#   compiler_flags:                                  # Compiler flags dictionary
#     cxx_flags:                                     # C++ compiler flags
#   toolchain:                                       # Toolchain configuration (dict or name)
#     cxx_compiler:
#   sysroot:                                         # Path to system headers/libraries

builds:
- build_machine: 1              # platform_id to build on
  run_machine: 1                # platform_id to run on
  recipe_id: 1                  # recipe_id to use
#   executables:                # Executables to profile (relative to build dir)
#     - test/run-tests
"""

TOOLCHAIN_TEMPLATE = """# Toolchain Configuration Template
# Uncomment and fill in the fields below:

name:  # Required: unique toolchain name
arch:  # Options: riscv, x86, arm

# Sysroot (optional)
# sysroot:

# Toolchain attributes (optional)
attributes:
#    # Compilers
#    c_compiler: 
#    cxx_compiler:
#    csharp_compiler:
#    cuda_compiler:
#    objc_compiler:
#    objcxx_compiler:
#    fortran_compiler:
#    hip_compiler:
#    ispc_compiler:
#    swift_compiler:
#    asm_compiler:
#    asm_nasm_compiler:
#    asm_marmasm_compiler:
#    asm_masm_compiler:
#    asm_att_compiler:

#    # Tools
#    ar:
#    as:
#    ld:
#    nm:
#    objcopy:
#    objdump:
#    ranlib:
#    readelf:
#    strip:


#    # Compiler flags
#    c_flags:
#    cxx_flags:
#    csharp_flags:
#    cuda_flags:
#    objc_flags:
#    objcxx_flags:
#    fortran_flags:
#    hip_flags:
#    ispc_flags:
#    swift_flags:
#    asm_flags:
#    asm_nasm_flags:
#    asm_marmasm_flags:
#    asm_masm_flags:
#    asm_att_flags:
"""
