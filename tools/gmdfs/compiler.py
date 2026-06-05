r"""gmdfs — Generic Markdown Differentiation-Free Specification compiler.

Compiles a single specification markdown file into multiple target-specific
markdown files by resolving injection markers::

    [target] {body}       → included only when compiling for *target*
    [a, b] {body}         → included when compiling for *a* OR *b*
    \[target] {body}      → escaped, rendered literally as ``[target] {body}``
    \\[target] {body}     → ``\`` followed by normal injection resolution
"""

from __future__ import annotations

import argparse
from enum import Enum, auto
from pathlib import Path
from typing import NamedTuple

import yaml


# ---------------------------------------------------------------------------
# Data model — immutable tokens
# ---------------------------------------------------------------------------


class Text(NamedTuple):
    """A plain-text segment with no injection semantics."""

    content: str


class Injection(NamedTuple):
    """An injection marker ``[targets] {body}`` or ``[targets] rest-of-line``."""

    targets: frozenset[str]
    body: str


Token = Text | Injection


# ---------------------------------------------------------------------------
# FSM states for the tokenizer
# ---------------------------------------------------------------------------


class _State(Enum):
    SCANNING = auto()
    ESCAPED = auto()
    IN_TARGET = auto()
    BODY_GAP = auto()
    IN_BRACE = auto()
    IN_LINE = auto()


# ---------------------------------------------------------------------------
# Front-matter parsing
# ---------------------------------------------------------------------------


def parse_front_matter(text: str) -> tuple[frozenset[str], str]:
    """Extract YAML front matter and return ``(views, body)``.

    The front matter must be a ``---``-delimited block at the very start of
    the file.  Its ``views`` key lists all valid target names.

    Args:
        text: Raw specification file content.

    Returns:
        ``(views, body)`` where *views* is a frozenset of target names and
        *body* is the remainder after the closing ``---``.

    Raises:
        ValueError: If the YAML block cannot be parsed or lacks ``views``.
    """
    if not text.startswith("---"):
        return frozenset(), text

    end = text.find("---", 3)
    if end == -1:
        msg = "Front-matter block ``---`` is never closed"
        raise ValueError(msg)

    raw = text[3:end]
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        msg = f"Invalid YAML in front matter:\n{exc}"
        raise ValueError(msg)

    if not isinstance(data, dict) or "views" not in data:
        msg = "Front matter must contain a ``views`` list"
        raise ValueError(msg)

    views_list = data["views"]
    if not isinstance(views_list, list) or not views_list:
        msg = "``views`` must be a non-empty list"
        raise ValueError(msg)

    views = frozenset(str(v) for v in views_list)
    return views, text[end + 3 :]


def validate_and_strip_views_blank(text: str, body: str) -> str:
    """Require a blank line immediately after the closing ``---``, then strip it.

    Args:
        text: Raw specification text (needed to locate ``---`` position).
        body: The body returned by :func:`parse_front_matter`.

    Returns:
        *body* with the leading blank line removed.

    Raises:
        ValueError: If no blank line follows the closing ``---``.
    """
    end = text.find("---", 3) + 3
    rest = text[end:]
    if rest.startswith("\n"):
        rest = rest[1:]

    if not rest or not rest.startswith("\n"):
        sample = rest.split("\n", 1)[0][:40]
        msg = f"Expected a blank line after ``---``, got: {sample!r}"
        raise ValueError(msg)

    return body.lstrip("\n")


# ---------------------------------------------------------------------------
# Tokenizer  —  finite-state machine
# ---------------------------------------------------------------------------


def tokenize(text: str) -> list[Token]:
    """Produce a flat token list from *text* using a finite-state machine.

    States
        ``SCANNING``   — default, accumulating plain text
        ``ESCAPED``    — after ``\\``; the next character is captured literally
        ``IN_TARGET``  — inside ``[…]``, collecting target names
        ``BODY_GAP``   — skipping horizontal whitespace between ``]`` and ``{``
        ``IN_BRACE``   — inside ``{…}`` with brace-depth tracking
        ``IN_LINE``    — consuming the rest of a line (implicit body)

    Args:
        text: Body content (without front matter).

    Returns:
        Flat list of ``Text`` and ``Injection`` tokens in document order.
    """
    tokens: list[Token] = []
    acc: list[str] = []
    targets: list[str] = []
    body: list[str] = []
    depth: int = 0
    state = _State.SCANNING
    i = 0
    n = len(text)

    def _emit_text() -> None:
        if acc:
            tokens.append(Text("".join(acc)))
            acc.clear()

    def _emit_injection() -> None:
        _emit_text()
        tokens.append(Injection(frozenset(targets), "".join(body)))
        targets.clear()
        body.clear()

    while i < n:
        ch = text[i]

        # -- SCANNING -------------------------------------------------------
        if state is _State.SCANNING:
            if ch == "\\" and i + 1 < n and text[i + 1] in ("[", "\\"):
                state = _State.ESCAPED
            elif ch == "[":
                _emit_text()
                state = _State.IN_TARGET
            else:
                acc.append(ch)

        # -- ESCAPED --------------------------------------------------------
        elif state is _State.ESCAPED:
            acc.append(ch)
            state = _State.SCANNING

        # -- IN_TARGET ------------------------------------------------------
        elif state is _State.IN_TARGET:
            if ch == "]":
                raw = "".join(targets)
                parsed = [t.strip() for t in raw.split(",") if t.strip()]
                targets.clear()
                targets.extend(parsed) if parsed else targets.append("")
                state = _State.BODY_GAP
            else:
                targets.append(ch)

        # -- BODY_GAP -------------------------------------------------------
        elif state is _State.BODY_GAP:
            if ch == "{":
                depth = 1
                state = _State.IN_BRACE
            elif ch in (" ", "\t"):
                pass
            elif ch == "\n":
                _emit_injection()
                state = _State.SCANNING
            else:
                body.append(ch)
                state = _State.IN_LINE

        # -- IN_BRACE -------------------------------------------------------
        elif state is _State.IN_BRACE:
            if ch == "\\" and i + 1 < n:
                nxt = text[i + 1]
                if nxt == "}":
                    i += 1
                    body.append("}")
                elif nxt == "\\":
                    i += 1
                    body.append("\\")
                else:
                    body.append(ch)
            elif ch == "{":
                depth += 1
                body.append(ch)
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    _emit_injection()
                    state = _State.SCANNING
                else:
                    body.append(ch)
            else:
                body.append(ch)

        # -- IN_LINE --------------------------------------------------------
        elif state is _State.IN_LINE:
            if ch == "\n":
                _emit_injection()
                state = _State.SCANNING
            elif ch == "[":
                _emit_injection()
                state = _State.IN_TARGET
                continue
            elif ch == "\\" and i + 1 < n:
                nxt = text[i + 1]
                if nxt == "[":
                    body.append("[")
                    i += 1
                elif nxt == "\\":
                    body.append("\\")
                    i += 1
                else:
                    body.append(ch)
            else:
                body.append(ch)

        i += 1

    # ---- end of input -----------------------------------------------------
    if state is _State.IN_TARGET:
        _emit_text()
        tokens.append(Text("[" + "".join(targets)))
    elif state is _State.BODY_GAP:
        _emit_injection()
    elif state is _State.IN_BRACE:
        _emit_text()
        tokens.append(Text("{" + "".join(body)))
    elif state is _State.IN_LINE:
        _emit_injection()
    elif state is _State.SCANNING:
        _emit_text()

    return tokens


# ---------------------------------------------------------------------------
# Compilation
# ---------------------------------------------------------------------------


def _compile(tokens: list[Token], targets: frozenset[str]) -> str:
    """Resolve injections for the given set of active targets.

    Spacing rules for each ``Injection`` token:

    * **Matching** (``targets ∩ injection.targets ≠ ∅``):
      eat **one** space character from the left **and** from the right.
    * **Non‑matching**: eat **one** space character from the **left only**.

    Args:
        tokens: Flat token list from :func:`tokenize`.
        targets: The set of targets to compile for.

    Returns:
        Compiled string.
    """
    n = len(tokens)

    eat_left: list[bool] = [False] * n
    eat_left_all: list[bool] = [False] * n
    eat_right: list[bool] = [False] * n

    for i, t in enumerate(tokens):
        if not isinstance(t, Injection):
            continue
        matches = bool(targets & t.targets)
        if i > 0 and isinstance(tokens[i - 1], Text):
            if matches:
                eat_left[i - 1] = True
            else:
                eat_left_all[i - 1] = True
        if matches and i + 1 < n and isinstance(tokens[i + 1], Text):
            eat_right[i + 1] = True

    parts: list[str] = []
    for i, t in enumerate(tokens):
        if isinstance(t, Text):
            content = t.content
            if eat_right[i] and content.startswith(" "):
                content = content[1:]
            if eat_left[i] and content.endswith(" "):
                content = content[:-1]
            if eat_left_all[i]:
                content = content.rstrip(" ")
            if content:
                parts.append(content)
        elif isinstance(t, Injection) and (targets & t.targets):
            parts.append(t.body)

    return "".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compile_spec(text: str, targets: frozenset[str]) -> str:
    """Compile a gmdfs specification for one or more targets.

    Pipeline:

    1. Parse and validate YAML front matter (extract ``views``).
    2. Validate blank line after the closing ``---``.
    3. FSM-based tokenization.
    4. Injection resolution with space-eating.

    Args:
        text: Raw specification file content.
        targets: Set of target names to include.

    Returns:
        Compiled markdown string.

    Raises:
        ValueError: On any structural or validation error.
    """
    views, body = parse_front_matter(text)

    unknown = targets - views
    if unknown:
        msg = (
            f"Unknown target(s): {', '.join(sorted(unknown))}. "
            f"Available: {', '.join(sorted(views))}"
        )
        raise ValueError(msg)

    body = validate_and_strip_views_blank(text, body)
    tokens = tokenize(body)
    return _compile(tokens, targets)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for ``python -m tools.gmdfs``."""
    parser = argparse.ArgumentParser(
        description="Compile gmdfs specification → target-specific markdown",
    )
    parser.add_argument("spec", help="Path to the ``.md`` specification file")
    parser.add_argument(
        "-o",
        "--out",
        action="append",
        required=True,
        dest="outputs",
        help="Format: ``target1:target2:…:output_path``. "
        "All targets preceding the last ``:`` are activated for that file.",
    )
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        parser.error(f"Specification not found: {spec_path}")

    raw = spec_path.read_text(encoding="utf-8")
    views, _ = parse_front_matter(raw)

    entries: list[tuple[frozenset[str], Path]] = []
    for mapping in args.outputs:
        parts = mapping.split(":")
        if len(parts) < 2:
            parser.error(
                f"Invalid ``--out`` format: {mapping!r}. "
                "Expected ``target:path`` or ``target1:target2:…:path``"
            )
        *target_names, raw_path = parts
        out = Path(raw_path)
        targets_for_file = frozenset(target_names)

        unknown = targets_for_file - views
        if unknown:
            parser.error(
                f"Unknown target(s): {', '.join(sorted(unknown))}. "
                f"Available: {', '.join(sorted(views))}"
            )
        entries.append((targets_for_file, out))

    for targets_for_file, out_path in entries:
        result = compile_spec(raw, targets_for_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result, encoding="utf-8")
        label = "+".join(sorted(targets_for_file))
        print(f"  ✓ {label} → {out_path}")


if __name__ == "__main__":
    main()
