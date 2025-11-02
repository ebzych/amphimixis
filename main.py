"""Temporary main for demonstrating and testing"""

import sys
import amphimixis

<<<<<<< HEAD
=======
try:
    analyzer_ = amphimixis.analyzer.Analyzer(sys.argv[1])

    analyzer_.analyze()
except FileNotFoundError as e:
    print(f"{e}")
    sys.exit(-1)
>>>>>>> 6b4344e (fix: fix ci, fix ci in builder, general, profiler, main.py)

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
