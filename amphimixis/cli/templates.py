CONFIG_TEMPLATE = """# Amphimixis Configuration Template
# Uncomment and configure the fields below:

# Build system (optional, default: CMake)
# build_system: CMake

# Runner / low-level build system (optional, default: Make)
# runner: Make

platforms:
  # - id: 1                        # Unique platform id
  #   address:                     # IP/domain (omit for local machine)
  #   arch: x86                    # Architecture (e.g. x86, riscv64, aarch64)
  #   username: root               # SSH username (required for remote)
  #   password: secret             # SSH password (or use SSH keys)
  #   port: 22                     # SSH port (optional, default: 22)

recipes:
  # - id: 1                        # Unique recipe id
  #   config_flags: "-DCMAKE_BUILD_TYPE=RelWithDebInfo"  # Build configuration options
  #   compiler_flags:              # Compiler flags dictionary
  #     cxx_flags: "-O2"           # C++ compiler flags
  #   toolchain:                   # Toolchain configuration (dict or name)
  #     cxx_compiler: "/usr/bin/g++"
  #   sysroot: "/"                 # Path to system headers/libraries

builds:
  # - build_machine: 1             # platform_id to build on
  #   run_machine: 1                # platform_id to run on
  #   recipe_id: 1                  # recipe_id to use
  #   executables:                  # Executables to profile (relative to build dir)
  #     - test/run-tests
"""

TOOLCHAIN_TEMPLATE = """# Toolchain Configuration Template
# Uncomment and fill in the fields below:

# name: my_toolchain   # Required: unique toolchain name
# platform: riscv64   # Options: x86_64, riscv64, etc.

# Sysroot (optional)
# sysroot: /path/to/sysroot

# Toolchain attributes (uncomment and cpnfigure as needed)
# attributes:
#    # Compilers
#    # c_compiler: /usr/bin/riscv64-unknown-elf-gcc
#    # cxx_compiler: /usr/bin/riscv64-unknown-elf-g++

#    #Tools
#    # ar: /usr/bin/riscv64-unknown-elf-ar
#    # as: /usr/bin/riscv64-unknown-elf-as
#    # ld: /usr/bin/riscv64-unknown-elf-ld
#    # nm: /usr/bin/riscv64-unknown-elf-nm
#    # objcopy: /usr/bin/riscv64-unknown-elf-objcopy
#    # objdump: /usr/bin/riscv64-unknown-elf-objdump
#    # ranlib: /usr/bin/riscv64-unknown-elf-ranlib
#    # readelf: /usr/bin/riscv64-unknown-elf-readelf
#    # strip: /usr/bin/riscv64-unknown-elf-strip

#    # Compiler flags (optional)
#    # cflags: -O2 -march=rv64gc
#    # cxxflags: -O2 -march=rv64gc
"""
