"""Temporary main for demonstrating and testing"""

import sys
from amphimixis import (
    general,
    build_systems_dict,
    analyzer,
    configurator,
    builder,
    profiler,
)


project = general.Project(
    sys.argv[1],
    [],
    build_systems_dict["make"],
    build_systems_dict["cmake"],
)

analyzer.analyze(project)

configurator.parse_config(project)

builder.Builder.build(project)

profiler_ = profiler.Profiler(project.builds[0])

profiler_.execution_time()

print(profiler_.stats)
