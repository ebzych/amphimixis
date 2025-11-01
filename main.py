"""Temporary main for demonstrating and testing"""

import sys
import amphimixis


project = amphimixis.general.Project(
    sys.argv[1],
    [],
    amphimixis.general.build_systems_dict["make"],
    amphimixis.general.build_systems_dict["cmake"],
)

amphimixis.analyzer.analyze(project)

amphimixis.configurator.parse_config(project)

amphimixis.builder.Builder.process(project)

profiler_ = amphimixis.profiler.Profiler(project.builds[0])

profiler_.execution_time()

print(profiler_.stats)
