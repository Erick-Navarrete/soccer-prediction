# Soccer Prediction Project

## Project Overview
AI-powered Premier League match prediction web app with ELO-based model, Flask backend, and interactive frontend.

## Tech Stack
- **Backend**: Flask (Python), pickle model, ELO rating system
- **Frontend**: Vanilla JS, Chart.js for visualizations, Font Awesome icons
- **Data**: `data/predictions.json` (current week), `data/historical.json` (past results), `data/summary.json`
- **Deploy**: Render, PythonAnywhere

## Key Files
- `web/app.py` — Flask routes and API endpoints
- `web/templates/index.html` — Single-page app with tab sections
- `web/static/js/app.js` — Core JS: data loading, tab switching, rendering
- `web/static/js/charts.js` — Chart.js charts (accuracy, distribution, calibration, ELO)
- `web/static/css/style.css` — Light theme + responsive
- `web/static/css/style-dark.css` — Dark mode overrides
- `src/` — ML model code (data_loader, feature_engineering, ml_models)

## Architecture
- Single-page app with 4 tabs: Predictions, Historical, Standings, Analytics
- Tab switching via `switchSection()` in app.js — syncs top nav, bottom mobile nav, and sidebar
- Charts load lazily when Analytics tab is selected
- Mobile: bottom tab bar (`.mobile-bottom-nav`) + hamburger sidebar menu
- API base: `/api/` — all data fetched via JSON endpoints

## Mobile Requirements (CRITICAL)
- **Bottom tab bar** is the primary mobile navigation — MUST be visible on all screen widths <= 768px
- **Hamburger menu** provides supplemental sidebar navigation on mobile
- Charts must use `devicePixelRatio: 1` on mobile for performance
- `touch-action: none` on canvas to prevent scroll hijacking
- Chart containers must have explicit `height` set (not percentage-based)

## Workflow Orchestration

### 1. Plan Node Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately — don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One tack per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

-----

# Task Management
1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

-----

# Core Principles
- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
