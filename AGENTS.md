AGENTS - repository conventions and helper commands

Application context
- Purpose: a golfer tracking app for strokes-gained analytics and practice plans.
- Modules: round entry, shot tracking, strokes-gained services, and a practice-plans module.

Tech stack
- Django, htmx, tailwind

Styling
- Use tailwind to create modern styling similar to tailwind ui

Testing
- Prefer pytest. Look for other test files for examples

Build / Run / Test
- Install dev deps: `rye sync` (project uses `rye` in pyproject.toml).
- Run app: `rye run python manage.py runserver` (or `python manage.py runserver`).
- Run full test suite: `rye run pytest` (pytest-django configured via `pytest.ini`).
- Run a single test: `rye run pytest path/to/test_file.py::TestClass::test_method -q` or `rye run pytest -k test_name -q`.
- Lint templates: `rye run djlint .` (templates-only linter; use `--reformat` to auto-fix).

Code style (short)
- Imports: group and order: standard lib, third-party, local app imports; separate groups with a blank line, avoid `from x import *`.
- Formatting: follow PEP8; wrap at ~88 chars; consistent 4-space indentation.
- Types: add type hints for public functions and complex returns; prefer `django-types` for models.
- Naming: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_SNAKE` for constants.
- Strings: prefer f-strings for interpolation; avoid concatenation.
- Tests: small, deterministic tests; use `factory-boy`; avoid DB state leakage between tests.

Cursor/Copilot rules
- No `.cursor/rules/` or `.github/copilot-instructions.md` found in repo; follow the guidelines above.

Keep changes minimal and focused; ask before wide refactors or adding new dev tools.
