import yaml
import argparse
from pathlib import Path
from typing import NamedTuple


class Text(NamedTuple):
    content: str


class Injection(NamedTuple):
    targets: list[str]
    body: str


Token = Text | Injection


def parse_front_matter(text: str) -> tuple[set[str], str]:
    if not text.startswith("---"):
        return set(), text

    end = text.find("---", 3)
    if end == -1:
        return set(), text

    yaml_text = text[3:end]
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError:
        return set(), text[end + 3 :]

    views = set(data["views"]) if data and "views" in data else set()
    return views, text[end + 3 :]


def _is_escaped(text: str, pos: int) -> bool:
    count = 0
    p = pos - 1
    while p >= 0 and text[p] == "\\":
        count += 1
        p -= 1
    return count % 2 == 1


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    n = len(text)

    while i < n:
        if text[i] == "\\" and i + 1 < n and text[i + 1] == "[":
            tokens.append(Text("["))
            i += 2
            continue

        if text[i] == "\\" and i + 1 < n and text[i + 1] == "\\":
            tokens.append(Text("\\"))
            i += 2
            continue

        if text[i] == "[" and not _is_escaped(text, i):
            close_bracket = text.find("]", i)
            if close_bracket == -1:
                tokens.append(Text("["))
                i += 1
                continue

            targets_str = text[i + 1 : close_bracket]
            targets = [t.strip() for t in targets_str.split(",") if t.strip()]

            body_start = close_bracket + 1
            while body_start < n and text[body_start] in " \t":
                body_start += 1

            if body_start < n and text[body_start] == "{":
                depth = 1
                j = body_start + 1
                while j < n and depth > 0:
                    if text[j] == "\\" and j + 1 < n and text[j + 1] == "}":
                        j += 2
                        continue
                    if text[j] == "{":
                        depth += 1
                    elif text[j] == "}":
                        depth -= 1
                    j += 1

                if depth == 0:
                    body = text[body_start + 1 : j - 1]
                    tokens.append(Injection(targets, body.rstrip("\n")))
                    i = j
                else:
                    tokens.append(Text(text[i]))
                    i += 1
            else:
                j = body_start
                while j < n:
                    if text[j] == "\n":
                        break
                    if text[j] == "[" and not _is_escaped(text, j):
                        break
                    j += 1

                body = text[body_start:j]
                tokens.append(Injection(targets, body))
                i = j
            continue

        tokens.append(Text(text[i]))
        i += 1

    return tokens


def compile_for_target(tokens: list[Token], target: str) -> str:
    parts: list[str] = []
    for token in tokens:
        if isinstance(token, Text):
            parts.append(token.content)
        elif isinstance(token, Injection):
            if target in token.targets:
                parts.append(token.body)
    return "".join(parts)


def compile_spec(text: str, target: str) -> str:
    views, body = parse_front_matter(text)
    if target not in views:
        raise ValueError(
            f"Target '{target}' not in views {views}. "
            f"Available views: {', '.join(sorted(views))}"
        )
    tokens = tokenize(body)
    return compile_for_target(tokens, target)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile gmdfs specification to target-specific markdown files"
    )
    parser.add_argument("spec", help="Path to gmdfs specification file")
    parser.add_argument(
        "--out",
        action="append",
        required=True,
        help="Target:output_path (e.g., user:docs/user.md)",
    )
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        parser.error(f"Specification file not found: {spec_path}")

    text = spec_path.read_text(encoding="utf-8")
    views, _ = parse_front_matter(text)

    for mapping in args.out:
        if ":" not in mapping:
            parser.error(
                f"Invalid --out format '{mapping}'. Expected target:output_path"
            )

        target, output_path = mapping.split(":", 1)
        if target not in views:
            parser.error(
                f"Target '{target}' not found in spec. Available views: {', '.join(sorted(views))}"
            )

    for mapping in args.out:
        target, output_path = mapping.split(":", 1)
        result = compile_spec(text, target)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result, encoding="utf-8")
        print(f"  ✓ {target} → {out}")


if __name__ == "__main__":
    main()
