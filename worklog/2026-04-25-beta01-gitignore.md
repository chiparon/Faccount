# 2026-04-25 beta0.1 gitignore

## Goal
- Prepare ignore rules before publishing beta0.1 to GitHub.
- Avoid committing local env files, dependencies, build output, runtime logs, and IDE config.

## Changes
- Reorganized `.gitignore` into sections.
- Added ignores for `venv/`, `.env.*`, `.idea/`, `.vscode/`, `frontend/.vite/`, frontend debug logs, `logs/`, `*.log`, and `Thumbs.db`.
- Kept `.env.example` and `backend/.env.example` available for commit.
- Prepared repository remote for `git@github.com:chiparon/Faccount.git` before beta0.1 publishing.

## Validation
- Verified key local paths are ignored: `backend/.env`, `backend/.venv`, `frontend/node_modules`, `frontend/dist`, `logs`, and `backend/.idea`.
- Confirmed no sensitive or large ignore-risk files are currently tracked.

## Remaining
- Before publishing, run `git status --ignored --short` once more.
- Git currently reports a repository ownership mismatch unless using `git -c safe.directory=E:/Eproject/accounts ...` or configuring `safe.directory` globally.
