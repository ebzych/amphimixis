from general import general
from builder import builder


project = general.Project(
    "/home/bzych/tinyxml2",
    [
        general.Build(
            general.MachineInfo(
                general.Arch.X86,
                "xxxx.xxxx.xxxx.xxxx",
                general.MachineAuthenticationInfo("bzych", "1234", 8000),
            ),
            "/home/bzych/tinyxml2_build",
            False,
            "",
            "",
            "",
        )
    ],
    general.CMake,
    general.Make,
)

builder.Builder.build_for_linux(project, project.builds[0])
