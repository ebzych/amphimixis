"""Tests for the gmdfs compiler."""

import pytest

from tools.gmdfs import (
    compile_spec,
    parse_front_matter,
    tokenize,
    validate_and_strip_views_blank,
)
from tools.gmdfs.compiler import Injection, Text


# ===========================================================================
# parse_front_matter
# ===========================================================================


class TestParseFrontMatter:
    def test_valid_front_matter(self):
        text = "---\nviews:\n  - user\n  - admin\n---\n\nbody"
        views, body = parse_front_matter(text)
        assert views == frozenset({"user", "admin"})
        assert body == "\n\nbody"

    def test_no_front_matter(self):
        views, body = parse_front_matter("just text")
        assert views == frozenset()
        assert body == "just text"

    def test_unclosed_front_matter(self):
        text = "---\nviews:\n  - user\n"
        with pytest.raises(ValueError, match="never closed"):
            parse_front_matter(text)

    def test_missing_views_key(self):
        text = "---\nfoo: bar\n---\n\nbody"
        with pytest.raises(ValueError, match="views"):
            parse_front_matter(text)

    def test_views_not_a_list(self):
        text = "---\nviews: 'scalar'\n---\n\nbody"
        with pytest.raises(ValueError, match="non-empty list"):
            parse_front_matter(text)

    def test_empty_views_list(self):
        text = "---\nviews: []\n---\n\nbody"
        with pytest.raises(ValueError, match="non-empty list"):
            parse_front_matter(text)

    def test_invalid_yaml(self):
        text = "---\n  invalid: yaml: :\n---\n\nbody"
        with pytest.raises(ValueError, match="Invalid YAML"):
            parse_front_matter(text)


# ===========================================================================
# validate_and_strip_views_blank
# ===========================================================================


class TestValidateAndStripViewsBlank:
    def test_valid_blank_line(self):
        text = "---\nviews:\n  - a\n---\n\nbody"
        body = "\n\nbody"
        result = validate_and_strip_views_blank(text, body)
        assert result == "body"

    def test_missing_blank_line(self):
        text = "---\nviews:\n  - a\n---\nbody"
        body = "\nbody"
        with pytest.raises(ValueError, match="blank line"):
            validate_and_strip_views_blank(text, body)


# ===========================================================================
# tokenize
# ===========================================================================


class TestTokenize:
    def test_plain_text_only(self):
        tokens = tokenize("hello world")
        assert tokens == [Text("hello world")]

    def test_empty_string(self):
        tokens = tokenize("")
        assert tokens == []

    def test_brace_injection(self):
        tokens = tokenize("[user] {hello}")
        assert tokens == [
            Injection(frozenset({"user"}), "hello", brace=True),
        ]

    def test_rest_of_line_injection(self):
        tokens = tokenize("[user] rest of line")
        assert tokens == [
            Injection(frozenset({"user"}), "rest of line"),
        ]

    def test_rest_of_line_ends_at_newline(self):
        tokens = tokenize("[user] first line\nsecond line")
        assert tokens == [
            Injection(frozenset({"user"}), "first line\n"),
            Text("second line"),
        ]

    def test_multi_target_marker(self):
        tokens = tokenize("[a, b, c] {body}")
        assert tokens == [
            Injection(frozenset({"a", "b", "c"}), "body", brace=True),
        ]

    def test_escaped_bracket(self):
        tokens = tokenize(r"\[user] {body}")
        assert tokens == [Text("[user] {body}")]

    def test_escaped_backslash(self):
        tokens = tokenize(r"\\[user] {body}")
        assert tokens == [
            Text("\\"),
            Injection(frozenset({"user"}), "body", brace=True),
        ]

    def test_escaped_backslash_in_brace(self):
        tokens = tokenize(r"[user] {\}}")
        assert tokens == [
            Injection(frozenset({"user"}), "}", brace=True),
        ]

    def test_mixed_content(self):
        tokens = tokenize("before [a] {x} after")
        assert tokens == [
            Text("before "),
            Injection(frozenset({"a"}), "x", brace=True),
            Text(" after"),
        ]

    def test_brace_body_strips_spaces(self):
        tokens = tokenize("[user] {  hello world  }")
        assert tokens == [
            Injection(frozenset({"user"}), "hello world", brace=True),
        ]

    def test_brace_body_strips_newlines(self):
        tokens = tokenize("[user] {\n\nhello\n\n}")
        assert tokens == [
            Injection(frozenset({"user"}), "\nhello\n", brace=True),
        ]

    def test_nested_braces(self):
        tokens = tokenize("[user] {outer {inner} end}")
        assert tokens == [
            Injection(frozenset({"user"}), "outer {inner} end", brace=True),
        ]

    def test_inline_starts_another_injection(self):
        tokens = tokenize("[a] x [b] y")
        assert tokens == [
            Injection(frozenset({"a"}), "x "),
            Injection(frozenset({"b"}), "y"),
        ]

    def test_inline_escaped_bracket(self):
        tokens = tokenize(r"[a] x \[b] y")
        assert tokens == [
            Injection(frozenset({"a"}), "x [b] y"),
        ]

    def test_unterminated_target(self):
        tokens = tokenize("[user")
        assert tokens == [Text("[user")]

    def test_unterminated_brace(self):
        tokens = tokenize("[user] {hello")
        assert tokens == [
            Text("{hello"),
        ]


# ===========================================================================
# compile_spec — full pipeline, matching EXAMPLES.md
# ===========================================================================


class TestCompileSpecExamples:
    SPEC1 = """\
---
views:
  - user
  - admin
---

# Welcome

[user] { You are a regular user. }

[admin] { You are an admin. }

Common footer.
"""

    def test_example1_user(self):
        result = compile_spec(self.SPEC1, frozenset({"user"}))
        assert result == "# Welcome\n\nYou are a regular user.\n\nCommon footer.\n"

    def test_example1_admin(self):
        result = compile_spec(self.SPEC1, frozenset({"admin"}))
        assert result == "# Welcome\n\nYou are an admin.\n\nCommon footer.\n"

    SPEC2 = """\
---
views:
  - llm
  - mdoc
---

1. ## Finding the active repository:
   [llm] - check Internet for matching repos
   - check latest commits and issues
   [mdoc] - review documentation sources
"""

    def test_example2_llm(self):
        result = compile_spec(self.SPEC2, frozenset({"llm"}))
        assert result == (
            "1. ## Finding the active repository:\n"
            "   - check Internet for matching repos\n"
            "   - check latest commits and issues\n"
        )

    def test_example2_mdoc(self):
        result = compile_spec(self.SPEC2, frozenset({"mdoc"}))
        assert result == (
            "1. ## Finding the active repository:\n"
            "   - check latest commits and issues\n"
            "   - review documentation sources\n"
        )

    SPEC3 = """\
---
views:
  - user
  - admin
  - audit
---

[user] {User data}
[admin] {Admin data}
[audit] {Audit data}
"""

    def test_example3_user_admin(self):
        result = compile_spec(self.SPEC3, frozenset({"user", "admin"}))
        assert result == "User data\nAdmin data\n"

    def test_example3_audit_only(self):
        result = compile_spec(self.SPEC3, frozenset({"audit"}))
        assert result == "\nAudit data\n"

    def test_example3_all_three(self):
        result = compile_spec(self.SPEC3, frozenset({"user", "admin", "audit"}))
        assert result == "User data\nAdmin data\nAudit data\n"

    SPEC4 = """\
---
views:
  - developer
  - reviewer
  - manager
---

[developer, reviewer] {Technical details}
[manager] {Executive summary}
"""

    def test_example4_developer(self):
        result = compile_spec(self.SPEC4, frozenset({"developer"}))
        assert result == "Technical details\n"

    def test_example4_developer_manager(self):
        result = compile_spec(self.SPEC4, frozenset({"developer", "manager"}))
        assert result == "Technical details\nExecutive summary\n"

    SPEC5 = """\
---
views:
  - user
---

Usage: \\[user] {args}
"""

    def test_example5_escaped_bracket(self):
        result = compile_spec(self.SPEC5, frozenset({"user"}))
        assert result == "Usage: [user] {args}\n"


class TestCompileSpec:
    def test_no_front_matter_accepts_any_target(self):
        result = compile_spec("hello [user] {world}", frozenset({"user"}))
        assert result == "helloworld"

    def test_no_front_matter_empty_targets(self):
        result = compile_spec("hello [user] {world}", frozenset())
        assert result == "hello"

    def test_unknown_target_raises(self):
        text = "---\nviews:\n  - user\n---\n\nbody"
        with pytest.raises(ValueError, match="Unknown target"):
            compile_spec(text, frozenset({"bogus"}))

    def test_empty_spec(self):
        result = compile_spec("", frozenset())
        assert result == ""

    def test_multi_target_marker_or_logic(self):
        text = "---\nviews:\n  - a\n  - b\n---\n\n[a, b] {shared}"
        result = compile_spec(text, frozenset({"a"}))
        assert result == "shared"
        result = compile_spec(text, frozenset({"b"}))
        assert result == "shared"
        result = compile_spec(text, frozenset({"a", "b"}))
        assert result == "shared"

    def test_indentation_preserved(self):
        text = "---\nviews:\n  - llm\n---\n\n1. step:\n   [llm] - detail"
        result = compile_spec(text, frozenset({"llm"}))
        assert result == "1. step:\n   - detail"

    def test_multiline_brace_body(self):
        text = (
            "---\nviews:\n  - x\n---\n\nbefore\n\n[x] {\n\nline1\n\nline2\n\n}\n\nafter"
        )
        result = compile_spec(text, frozenset({"x"}))
        assert result == "before\n\nline1\n\nline2\n\nafter"

    def test_unknown_target_in_cli_format(self):
        text = "---\nviews:\n  - user\n---\n\nbody"
        with pytest.raises(ValueError, match="Unknown target"):
            compile_spec(text, frozenset({"admin"}))


# ===========================================================================
# Space-eating edge cases
# ===========================================================================


class TestSpaceEating:
    def test_eat_one_space_left_and_right_matching(self):
        spec = "---\nviews:\n  - a\n---\n\nHello [a] {world} !"
        result = compile_spec(spec, frozenset({"a"}))
        assert result == "Helloworld!"

    def test_eat_one_space_left_only_non_matching(self):
        spec = "---\nviews:\n  - a\n  - b\n---\n\nHello [a] {world} !"
        result = compile_spec(spec, frozenset({"b"}))
        assert result == "Hello !"

    def test_two_spaces_left_eat_one_matching(self):
        spec = "---\nviews:\n  - a\n---\n\nx  [a] {y}  z"
        result = compile_spec(spec, frozenset({"a"}))
        assert result == "x y z"

    def test_two_spaces_left_eat_one_non_matching(self):
        spec = "---\nviews:\n  - a\n  - b\n---\n\nx  [a] {y}  z"
        result = compile_spec(spec, frozenset({"b"}))
        assert result == "x  z"
