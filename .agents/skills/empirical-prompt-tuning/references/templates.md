# Empirical Prompt Tuning Templates

Use these as lightweight templates.
Keep the actual artifacts shorter when possible.

## 1. Classification Table

| Target | Type | Priority | Why now | Canonical file | Notes |
|---|---|---|---|---|---|
| `project-scaffolder` | skill | Critical | Writes project structure and docs | `E:\codex\workspace\.agents\skills\project-scaffolder\SKILL.md` | High breakage cost if guidance drifts |

Priority meanings:

- `Critical`: frequent or high-impact failure
- `Important`: regular use, moderate failure cost
- `Opportunistic`: evaluate when touched
- `Exempt`: evaluation cost is not worth it

## 2. Scenario Template

```md
### Scenario: <short name>

- Target:
- Case type: median | edge
- User-like request:
- Required artifact or input:
- Why this scenario matters:
```

## 3. Checklist Template

```md
#### Checklist

- [critical] <must-pass requirement>
- <observable requirement>
- <observable requirement>
- <observable requirement>
```

Checklist rules:

- keep 3 to 7 items
- make each item judgeable after execution
- mark at least 1 `[critical]` item

## 4. Result Log Template

```md
### Trial Result: <scenario name>

- Executor separation: empirical | static-only
- Success:
- Failed `[critical]` items:
- Precision notes:
- Tool usage notes:
- Duration:
- Retry count:
- Ambiguous points:
- Discretion completions by executor:
- Next revision theme:
```
