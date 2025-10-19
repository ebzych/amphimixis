"""Enumeration represent architectures of proccessors"""

from enum import Enum


class Arch(str, Enum):
    """Supported architectures"""

    X86 = "x86"
    RISCV = "riscv"
    ARM = "arm"
