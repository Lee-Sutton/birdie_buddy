# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Birdie Buddy is a Django-based golf tracking application focused on strokes-gained analytics and practice session management. The app helps golfers analyze their performance by tracking detailed shot-by-shot data and calculating strokes gained metrics across different aspects of the game (driving, approach, short game, putting).

## Technology Stack

- **Backend**: Django 5.1.4 with PostgreSQL
- **Frontend**: HTMX + Tailwind CSS (via django-cotton components)
- **Package Management**: Rye
- **Testing**: pytest with pytest-django, factory-boy for fixtures, pytest-playwright for e2e tests
- **Storage**: Azure Blob Storage (via django-storages) for scorecard images
- **AI Services**:
  - Anthropic Claude for scorecard parsing
  - OpenAI for practice notes enhancement

## Development Commands

### Environment Setup
```bash
# Install dependencies
rye sync

# Start PostgreSQL and Azurite (Azure Storage emulator)
docker-compose up -d

# Apply database migrations
python manage.py migrate
```

### Running the Application
```bash
# Start development server
rye run python manage.py runserver
# or
python manage.py runserver

# Run Tailwind CSS in watch mode (required for styling changes)
rye run invoke tailwind
# or
invoke tailwind --watch
```

### Testing
```bash
# Run full test suite
rye run pytest

# Run specific test file
rye run pytest path/to/test_file.py -q

# Run specific test method
rye run pytest path/to/test_file.py::TestClass::test_method -q

# Run tests matching a keyword
rye run pytest -k test_name -q
```

### Code Quality
```bash
# Lint Django templates (uses djlint)
rye run djlint .

# Auto-format templates
rye run djlint . --reformat
```

## Application Architecture

### Core Apps

1. **round_entry**: Main app for golf round tracking
   - Models: `Round`, `Hole`, `Shot`, `ScorecardUpload`
   - Tracks detailed shot-by-shot data for each hole
   - Calculates strokes gained metrics using PGA Tour baseline data
   - Supports scorecard image upload with AI-powered parsing

2. **practice**: Practice session tracking
   - Models: `PracticeSession`
   - Tracks practice type (Full Swing, Short Game, Putting), outcome, and notes
   - AI-enhanced notes using OpenAI for structured feedback

3. **users**: User management (extends Django auth)

4. **components**: Reusable django-cotton UI components

### Strokes Gained Architecture

The strokes gained calculation is central to this app. Key concepts:

- **Shot Categories**:
  - Driving: Tee shots on par 4/5 holes (>250 yards)
  - Approach: Shots from 30-250 yards in fairway/rough/tee
  - Short Game: Shots ≤30 yards from fairway/rough/sand
  - Putting: All shots from the green

- **Calculation Flow**:
  1. Each `Shot` has a `start_distance` and `lie` (tee, fairway, rough, sand, green)
  2. `avg_strokes_to_holeout()` looks up baseline PGA data for that distance/lie
  3. Strokes gained = baseline - (1 + next_shot_baseline)
  4. `Hole` and `Round` models aggregate SG across shot categories

- **Key Services**:
  - `strokes_gained.py`: Core calculation logic
  - `avg_strokes_to_holeout.py`: PGA Tour baseline data lookup
  - `{driving,approach,short_game,putting}_stats_service.py`: Category-specific stats aggregation
  - `scorecard_parser_service.py`: Uses Anthropic Claude to parse scorecard images

### View/Template Patterns

- Uses django-crispy-forms with crispy-tailwind for form rendering
- HTMX for dynamic interactions (e.g., adding shots to holes)
- Templates use django-cotton for component-based UI
- Forms typically use `LoginRequiredMixin` and filter by `request.user`

### Testing Patterns

- Tests live alongside the code they test (e.g., `models.py` → `models_test.py`)
- Factory fixtures in `factories/` directories use factory-boy
- Common fixtures in `conftest.py`: `user`, `authenticated_client`
- E2E tests in `e2e/` directories use pytest-playwright

## Environment Configuration

Required environment variables (set in `.env` file at project root):

```
SECRET_KEY=<django-secret>
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (matches docker-compose.yml defaults)
POSTGRES_DB=birdie_buddy
POSTGRES_USER=birdie_user
POSTGRES_PASSWORD=birdie_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=6432

# Azure Storage (use Azurite for local dev)
AZURE_CONNECTION_STRING=<connection-string>

# AI Services
ANTHROPIC_API_KEY=<key>
OPENAI_KEY=<key>
GCLOUD_VISION_API_KEY=<key>
```

## Code Style Guidelines

- **Imports**: Group by stdlib, third-party, local; separate with blank lines
- **Formatting**: PEP8, ~88 char line length, 4-space indentation
- **Type Hints**: Add for public functions and complex returns; use django-types for models
- **Naming**: `snake_case` functions/vars, `PascalCase` classes, `UPPER_SNAKE` constants
- **Strings**: Prefer f-strings over concatenation
- **Tests**: Small, deterministic, use factory-boy, avoid DB state leakage

## Database Schema Notes

- `Round.holes_played` tracks expected holes (1-18), `Round.complete` property checks if all holes have shots
- `Hole.mental_scorecard` tracks the "Tiger Five" metric (shots where mental errors occurred)
- `Shot.number` is the shot sequence within a hole
- Shot distances stored in both yards and feet (automatically converted on save based on lie type)
- `ScorecardUpload` can be linked to a `Round` after parsing completes

## Key Implementation Details

1. **Shot Type Auto-Classification**: `Shot._parse_shot_type()` automatically sets shot type based on distance/lie during save

2. **Strokes Gained Calculation**: Done per shot in `Shot.calculate_strokes_gained()`, aggregated up through Hole → Round

3. **User Scoping**: All models have a `user` ForeignKey; views filter by `request.user` for multi-tenancy

4. **Form Styling**: Use crispy-forms with Tailwind templates (see `forms.py` files for examples)

5. **Static Files**: Tailwind compiles from `static/css/input.css` → `output.css`; must run `invoke tailwind` during development
