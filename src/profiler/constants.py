"""Profiler stats fields enumeration."""

from enum import Enum


class Stats(str, Enum):
    """Profiler stats fields"""

    EXECUTION_TIME_FIELD = "execution_time"
    EXECUTABLE_RUN_SUCCESS = "executable_run_success"


# class Perf(int, Enum):
#     """Perf stat record fields"""

#     VALUE: 0 = "value_field"
#     COUNTER_UNIT: 1 = "unit_counter_field"
#     EVENT: 2 = "event_field"
#     COUNTER_TIME: 3 = "counter_time_field"
#     COUNTER_PERCENTAGE: 4 = "counter_percentage_field"
#     METRIC_VALUE: 5 = "metric_value_field"
#     METRIC_UNIT: 6 = "metric_unit_field"


class Perf(int, Enum):
    """Perf stat record fields"""

    VALUE = 0
    COUNTER_UNIT = 1
    EVENT = 2
    COUNTER_TIME = 3
    COUNTER_PERCENTAGE = 4
    METRIC_VALUE = 5
    METRIC_UNIT = 6


PerfStrings = {
    Perf.VALUE: "value_field",
    Perf.COUNTER_UNIT: "unit_counter_field",
    Perf.EVENT: "event_field",
    Perf.COUNTER_TIME: "counter_time_field",
    Perf.COUNTER_PERCENTAGE: "counter_percentage_field",
    Perf.METRIC_VALUE: "metric_value_field",
    Perf.METRIC_UNIT: "metric_unit_field",
}
