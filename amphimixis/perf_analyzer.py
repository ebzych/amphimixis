"""Compare two perf output files."""

import os
import sys
from collections import defaultdict

import pandas as pd
from openai import OpenAI


# pylint: disable=too-few-public-methods
class LLMAnalyzer:
    """An OpenAI API wrapper"""

    def __init__(self, api_key=None, base_url=None, model_name=None, project=None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv(
            "LLM_BASE_URL", "https://api.openai.com/v1"
        )
        self.model = model_name or os.getenv("LLM_MODEL", "gpt-4o")
        self.project = project or os.getenv("LLM_PROJECT", "")

        self.client = OpenAI(
            api_key=self.api_key, base_url=self.base_url, project=self.project
        )

    def ask(self, system_prompt, user_prompt, temperature=0.2):
        """
        Send a prompt to the LLM and return the response.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )

        return response.choices[0].message.content


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
LLM_OUTPUT_FILENAME = "perf_llm_output.md"


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

    merged = _get_comparison_data(data_a, data_b, max_rows)

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


def _format_df_to_text(event_name, df):
    text = [f"EVENT: {event_name.upper()}"]
    text.append(f"{'Symbol':<60} | {'A%':>8} | {'B%':>8} | {'Delta%':>8}")
    for _, r in df.iterrows():
        text.append(
            f"{r['symbol'][:60]:<60} | {r['share_a']:8.2f} "
            f"| {r['share_b']:8.2f} | {r['delta']:+8.2f}"
        )
    return "\n".join(text)


def _get_raw_context(perf_file, target_symbols):
    context_raw = []
    with open(perf_file, "r", encoding="UTF-8") as f:
        for line in f:
            if any(sym in line for sym in target_symbols):
                context_raw.append(line.strip())
            if len(context_raw) > 500:
                break
    return "\n".join(context_raw)


def _get_comparison_data(data_a, data_b, max_rows):
    df_a = pd.DataFrame([{"symbol": s, "weight_a": w} for s, w in data_a.items()])
    df_b = pd.DataFrame([{"symbol": s, "weight_b": w} for s, w in data_b.items()])

    if df_a.empty and df_b.empty:
        return pd.DataFrame()

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

    top_changes = merged.reindex(
        merged.delta.abs().sort_values(ascending=False).index
    ).head(max_rows)

    return top_changes


def analyze_with_llm(table, samples_a, samples_b):
    """
    Analyzes performance data using a Large Language Model (LLM) and saves the output to a file.
    """
    analyzer = LLMAnalyzer()
    system_prompt = (
        "Ты — ведущий инженер по производительности систем (Senior Systems Performance Engineer). "
        "Твоя специализация — анализ архитектуры наборов команд (ISA),"
        " микроархитектура процессоров и оптимизация кода на C/C++."
    )

    user_prompt = f"""Проанализируй следующие данные профилирования производительности.
    Используй сборку A (build A) в качестве базовой линии:

    Сводка сравнения сборки A -> сборки B:
    {table}

    Исходные замеры (perf samples) сборки A:
    {samples_a}

    Исходные замеры (perf samples) сборки B:
    {samples_b}

    Задачи:
    1. Выяви основные «горячие точки» (hotspots) в сборке B по сравнению со сборкой A.
    2. Объясни, почему конкретные функции C/C++ могут работать хуже в сборке B 
    (рассмотри вопросы выравнивания данных, атомарные операции или отсутствие специфических инструкций).
    3. Установи корреляцию между промахами кэша (cache-misses) / ошибками предсказания переходов (branch-misses) 
    и деградацией циклов процессора.
    4. Предложи оптимизации на уровне кода или флаги компилятора.
    """

    print("\nАнализ LLM...")
    with open(LLM_OUTPUT_FILENAME, "w", encoding="UTF-8") as f:
        f.write(analyzer.ask(system_prompt, user_prompt))
        print(f"Сохранено в {LLM_OUTPUT_FILENAME}")


def main(
    filename1,
    filename2,
    target_events: None | list[str] = None,
    max_rows=20,
    use_llm=False,
):
    """
    Compares two perf output files and prints the top `max_rows`
    symbols with the most significant changes for specified events.
    """

    stats_a = _get_stats_by_event(filename1)
    stats_b = _get_stats_by_event(filename2)

    if not stats_a or not stats_b:
        return

    all_events = set(stats_a.keys()) | set(stats_b.keys())

    top_regressions = []
    comparison_table_text = ""

    for event in target_events if target_events else all_events:
        print_comparison_table(event, stats_a[event], stats_b[event], max_rows)

        df = _get_comparison_data(stats_a[event], stats_b[event], max_rows)
        comparison_table_text += _format_df_to_text(event, df)
        top_regressions.extend(df[df["delta"] > 0.5]["symbol"].tolist())

    raw_samples_a = _get_raw_context(filename1, top_regressions[:5])
    raw_samples_b = _get_raw_context(filename2, top_regressions[:5])
    if use_llm:
        analyze_with_llm(comparison_table_text, raw_samples_a, raw_samples_b)


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
