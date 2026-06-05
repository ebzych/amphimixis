# gmdfs — Examples

## CLI usage

```bash
# Compile for one target
python -m tools.gmdfs spec.md -o user:build/user.md

# Compile for multiple targets
python -m tools.gmdfs spec.md -o user:build/user.md -o admin:build/admin.md

# Compile with MULTI-TARGET activation (includes injections for user AND admin)
python -m tools.gmdfs spec.md -o user:admin:build/both.md

# Short alias
python -m tools.gmdfs spec.md -o user:out.md
```

---

## Syntax reference

| Pattern | Meaning |
|---------|---------|
| `[A] {body}` | Inject *body* when target **A** is active |
| `[A, B] {body}` | Inject *body* when **A** *or* **B** is active |
| `[A] rest of line` | Implicit body (no `{}`), spans to next `[` or `\n` |
| `\[A] {body}` | Escaped `[` — renders literally as `[A] {body}` |
| `\\[A] {body}` | Literal `\` followed by normal injection of `[A]` |

---

## Spacing behaviour

Given the line: `Hello [A] {world} !`

| Active target | Result |
|---------------|--------|
| `A` | `Helloworld!` — space before `[` and after `}` eaten |
| `B` (not A) | `Hello !` — only left space eaten (before `[`) |

Given the line: `x  [A] {y}  z`

| Active target | Result |
|---------------|--------|
| `A` | `x y z` — one of two spaces eaten on each side |
| `B` (not A) | `x  z` — one left space eaten, right spaces preserved |

---

## Example 1 — Single-line `{…}` blocks

**spec.md:**
```markdown
---
views:
  - user
  - admin
---

# Welcome

[user] { You are a regular user. }

[admin] { You are an admin. }

Common footer.
```

**Compiled for `user`:**
```markdown
# Welcome

You are a regular user.

Common footer.
```

---

## Example 2 — Implicit (rest-of-line) body

**spec.md:**
```markdown
---
views:
  - llm
  - mdoc
---

1. ## Finding the active repository:
   [llm] - check Internet for matching repos
   - check latest commits and issues
   [mdoc] - review documentation sources
```

**Compiled for `llm`:**
```markdown
1. ## Finding the active repository:
   - check Internet for matching repos
   - check latest commits and issues
```

**Compiled for `mdoc`:**
```markdown
1. ## Finding the active repository:

   - check latest commits and issues
   - review documentation sources
```

---

## Example 3 — Multi-target compilation

**spec.md:**
```markdown
---
views:
  - user
  - admin
  - audit
---

[user] {User data}
[admin] {Admin data}
[audit] {Audit data}
```

```bash
python -m tools.gmdfs spec.md -o user:admin:combined.md
```

**combined.md:**
```markdown
User data
Admin data
```

---

## Example 4 — Multi-target injection

**spec.md:**
```markdown
---
views:
  - developer
  - reviewer
  - manager
---

[developer, reviewer] {Technical details}
[manager] {Executive summary}
```

**Compiled for `developer`:**
```markdown
Technical details
```

**Compiled for `developer:manager`:**
```markdown
Technical details
Executive summary
```

---

## Example 5 — Escape sequences

**spec.md:**
```markdown
---
views:
  - user
---

Usage: \[user] {args} — renders brackets literally
```

**Compiled for `user`:**
```markdown
Usage: [user] {args} — renders brackets literally
```