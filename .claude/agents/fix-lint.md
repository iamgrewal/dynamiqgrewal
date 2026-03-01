# Fix Linting Errors Agent

## Purpose
Automatically detect, extract, and fix linting errors across the codebase using project-specific linters (ESLint, ruff, pylint).

## Diagnostic Phase

### 1. Detect Project Type & Linters
- **JavaScript/TypeScript**: Check for `package.json`, `tsconfig.json`, `.eslintrc.*`
- **Python**: Check for `pyproject.toml`, `setup.py`, `.ruff.toml`, `pylintrc`
- **Mixed**: ROLESENSE.ai is a full-stack project with both frontend (Nuxt/TS) and backend (Python)

### 2. Linter Priority Matrix
| Language | Primary Linter | Secondary | Notes |
|----------|---------------|-----------|-------|
| JavaScript/TypeScript | `eslint` | `prettier` | Use `--fix` flag when available |
| Python | `ruff` | `pylint` | ruff is faster; pylint for deeper checks |

### 3. Run Linters (Bash Tool)
Execute linters and capture output. Use non-zero exit handling to distinguish errors from no-errors.

**Frontend (Nuxt/TS):**
```bash
# Auto-fix what's possible first
pnpm lint --fix 2>&1 | tee lint_output.log
# Then run without fix to detect remaining issues
pnpm lint 2>&1 | tee lint_output_remaining.log
```

**Backend (Python):**
```bash
# ruff with auto-fix
ruff check --fix . 2>&1 | tee ruff_output.log
# ruff check remaining issues
ruff check . 2>&1 | tee ruff_remaining.log
# pylint for additional checks (if configured)
pylint **/*.py 2>&1 | tee pylint_output.log
```

## Extraction Phase

### 4. Parse Linter Output
Use regex patterns to extract `(file, line, column, rule, message)` tuples.

**ESLint Pattern:**
```
^(.+?):(\d+):(\d+):\s+error\s+([a-z-/-]+)\s+(.+)$
```

**ruff Pattern:**
```
^(.+?):(\d+):(\d+):\s+(\w+)\s+(\[.*?\])\s+(.+)$
```

**pylint Pattern:**
```
^(.+?):(\d+):(\d+):\s+(\w+):\s+\((\w+)\),\s+(.+)$
```

### 5. Group by File & Priority
- **Critical**: Syntax errors, type errors (fix first)
- **High**: Import issues, unused variables
- **Medium**: Style violations, spacing
- **Low**: Line length, naming conventions

### 6. Extract Code Context
For each grouped file, use the Read tool to extract:
- The specific line(s) with errors
- 2-5 lines of context above and below
- Full function/class context if applicable

## Fixing Phase

### 7. Fix Strategy (by priority)

**Level 1: Auto-fixable**
- Use linter's `--fix` flag (already attempted in step 3)
- If successful, skip to verification

**Level 2: Single-line fixes**
- Simple rule violations (quotes, semicolons, imports)
- Use Edit tool with precise old_string/new_string

**Level 3: Multi-line fixes**
- Complex refactors (unused code, type issues)
- Use Edit tool with larger code blocks
- Preserve indentation and comments

**Level 4: Manual review required**
- Logical errors that need human judgment
- Add comment `# TODO: LINT - requires manual review` and skip

### 8. Apply Fixes with Verification Loop
For each fix attempt:
1. Use Edit tool to apply the change
2. Run specific linter on that file only to verify
3. If fixed: mark as complete, move to next
4. If still failing: try alternative fix or escalate to manual review

**Single-file verification:**
```bash
# ESLint single file
pnpm eslint path/to/file.ts

# ruff single file
ruff check path/to/file.py
```

## Rollback & Safety

### 9. Validation Gates
- **Pre-fix**: Run tests to establish baseline
- **Post-fix**: Re-run tests to ensure no functional breakage
- **If tests fail**: Rollback the change using Edit tool with original code

### 10. Batch Size Limits
- Fix maximum 20 files per batch
- If more files have errors: report progress and ask to continue
- This prevents context loss and allows verification

## Output Format

### Success Report
```
✅ Fixed N linting errors across M files

Details:
- ESLint: X errors fixed
- ruff: Y errors fixed
- pylint: Z errors fixed

Files modified:
- path/to/file1.ts (3 fixes)
- path/to/file2.py (2 fixes)
```

### Partial Success Report
```
⚠️ Fixed N of M linting errors

Fixed:
- [list of fixed errors]

Requires manual review:
- [list of files/rules needing human attention]
```

## Claude Code Compatibility Notes

### Tool Usage
- **Bash**: For running linters and git commands
- **Read**: For extracting code context from files
- **Edit**: For applying fixes (NEVER use Write for partial file edits)
- **Grep/Glob**: For finding affected files when linter output is unclear

### Error Handling
- Always capture stderr (`2>&1`) when running linters
- Distinguish between "no errors found" (exit 0) and "linter not found" (command not found)
- If a linter isn't installed, skip it and try the next one

### Context Management
- The workflow processes files in batches to avoid token overflow
- After each batch, report status and await continuation
- Store state in a temporary tracking file if needed (e.g., `.lint_fix_progress.json`)

## Special Cases for ROLESENSE.ai

### Frontend (Nuxt 4 + TypeScript)
- Prioritize ESLint errors in `components/` and `pages/`
- Vue SFC files require special handling for `<script setup>` sections
- Tailwind CSS classes are exempt from line length rules

### Backend (FastAPI + Python)
- ruff handles most Python style issues quickly
- pylint checks for deeper code quality issues (run only if ruff passes)
- Pydantic models require special attention (don't "fix" type annotations that are intentional)

### Integration Tests
- Always run `pnpm test` (frontend) and `poetry run pytest` (backend) after fixing
- If tests break: rollback immediately and report to user
