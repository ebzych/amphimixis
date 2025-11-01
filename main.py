"""Temporary main for demonstrating and testing"""

import sys
import amph

try:
    analyzer_ = amph.analyzer.Analyzer(sys.argv[1])

    analyzer_.analyze()
except FileNotFoundError as e:
    print(f"{e}")
    exit(-1)

project = amph.general.Project(
    sys.argv[1],
    [],
    amph.general.build_systems_dict["make"],
    amph.general.build_systems_dict["cmake"],
)

amph.configurator.parse_config(project)

amph.builder.Builder.process(project)

profiler_ = amph.profiler.Profiler(project.builds[0])

profiler_.execution_time()

print(profiler_.stats)
