"""Compare two perf output files."""

import sys
from collections import defaultdict

import pandas as pd

try:
    from amphimixis import logger

    _logger = logger.setup_logger("PERF_ANALYZER")
except ImportError:
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _logger = logging.getLogger("PERF_ANALYZER")

SYMBOL_LENGTH = 160
COLUMN_LENGTH = 12


def _parse_perf_line(line):
    parts = line.strip().split()
    if len(parts) < 5:
        _logger.warning("Wrong line format:\n%s", line)
        return None

    period = float(parts[1])
    event_type = parts[2].split(":")[0]
    ip_val = parts[3]

    line_after_ip = line.split(ip_val, 1)[1].strip()
    last_paren_idx = line_after_ip.rfind("(")
    symbol = (
        line_after_ip[:last_paren_idx].strip()
        if last_paren_idx != -1
        else line_after_ip.strip()
    )

    return symbol, period, event_type


def _get_stats_by_event(filepath):
    # { 'cycles': { 'func1': 100, 'func2': 200 }, 'cache-misses': { ... } }
    event_data = defaultdict(lambda: defaultdict(float))

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                res = _parse_perf_line(line)
                if res:
                    sym, period, ev = res
                    event_data[ev][sym] += period
    except FileNotFoundError:
        return None

    return event_data


# pylint: disable=too-many-locals
def print_comparison_table(event_name, data_a, data_b, max_rows):
    """Prints statistics comparison for a specific event."""

    df_a = pd.DataFrame([{"symbol": s, "weight_a": w} for s, w in data_a.items()])
    df_b = pd.DataFrame([{"symbol": s, "weight_b": w} for s, w in data_b.items()])

    if df_a.empty and df_b.empty:
        return

    if not df_a.empty:
        df_a["share_a"] = (df_a["weight_a"] / df_a["weight_a"].sum()) * 100
    else:
        df_a = pd.DataFrame(columns=["symbol", "share_a"])

    if not df_b.empty:
        df_b["share_b"] = (df_b["weight_b"] / df_b["weight_b"].sum()) * 100
    else:
        df_b = pd.DataFrame(columns=["symbol", "share_b"])

    merged = pd.merge(
        df_a[["symbol", "share_a"]],
        df_b[["symbol", "share_b"]],
        on="symbol",
        how="outer",
    ).fillna(0)

    merged["delta"] = merged["share_b"] - merged["share_a"]

    result = merged.reindex(merged.delta.abs().sort_values(ascending=False).index).head(
        max_rows
    )

    header_symbol = "Symbol".ljust(SYMBOL_LENGTH)
    header_a = "Build A %".rjust(COLUMN_LENGTH)
    header_b = "Build B %".rjust(COLUMN_LENGTH)
    header_delta = "Delta %".rjust(COLUMN_LENGTH)

    print(f"\n{'='*10} EVENT: {event_name.upper()} {'='*10}")
    print(f"{header_symbol} | {header_a} | {header_b} | {header_delta}")
    print("-" * (SYMBOL_LENGTH + COLUMN_LENGTH * 3 + 10))

    for _, row in result.iterrows():
        sym = row["symbol"]
        display_sym = (
            (sym[: SYMBOL_LENGTH - 3] + "...") if len(sym) > SYMBOL_LENGTH else sym
        )

        val_a = f"{row['share_a']:>{COLUMN_LENGTH}.2f}"
        val_b = f"{row['share_b']:>{COLUMN_LENGTH}.2f}"
        val_d = f"{row['delta']:>+{COLUMN_LENGTH}.2f}"
        print(f"{display_sym.ljust(SYMBOL_LENGTH)} | {val_a} | {val_b} | {val_d}")


def main(filename1, filename2, target_events: None | list[str] = None, max_rows=20):
    """
    Compares two perf output files and prints the top `max_rows`
    symbols with the most significant changes for specified events.
    """

    stats_a = _get_stats_by_event(filename1)
    stats_b = _get_stats_by_event(filename2)

    if not stats_a or not stats_b:
        return

    all_events = set(stats_a.keys()) | set(stats_b.keys())

    if target_events is None:
        for event in all_events:
            print_comparison_table(event, stats_a[event], stats_b[event], max_rows)
    else:
        for event in target_events:
            if event in all_events:
                print_comparison_table(event, stats_a[event], stats_b[event], max_rows)
            else:
                _logger.warning("%s not found in scriptout", event)


if __name__ == "__main__":
    if len(sys.argv) < 3 or "-h" in sys.argv or "--help" in sys.argv:
        print(
            "Usage: python3 compare_perf.py "
            "<file1.scriptout> "
            "<file2.scriptout> "
            "[max rows per event]"
        )

        sys.exit(1)

    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main(sys.argv[1], sys.argv[2], None, int(sys.argv[3]))
