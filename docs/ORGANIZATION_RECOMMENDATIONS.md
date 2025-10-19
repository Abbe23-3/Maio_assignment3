# Organization Recommendations

- Use feature branches (`feature/<topic>`) and open PRs early so CI runs before merging.
- Keep `models/` for reproducible artifacts only; stash experiments under a dedicated `experiments/` directory.
- Update `CHANGELOG.md` with every release candidate and ensure metrics are recalculated.
- Avoid committing `.venv/` or other virtual environment folders; rely on `.flake8` `exclude` rules and `.gitignore`.
- Seed random number generators (already done via `random_state`) when experimenting with new models to maintain reproducibility.
