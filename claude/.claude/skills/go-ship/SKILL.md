---
name: go-ship
description: >
  Use when Go implementation work is done and ready to ship. Runs the
  full quality pipeline: make check, /simplify, commit, push, and
  make install.
disable-model-invocation: true
---

# Go ship

Simplify, commit, push, and install a Go project in one pass. Go
conventions are enforced by the `go-conventions` skill plus project
hooks. No separate review step.

## Pipeline

Run these steps sequentially. Stop on failure.

### 1. make check

```bash
make check
```

If vet or tests fail, fix the issues before proceeding.

### 2. Simplify

Invoke the `simplify` skill (`/simplify`). Fix any issues found, re-run `make check` after fixes.

### 3. Commit and push

Follow the standard git commit workflow from the system prompt. Stage specific files, write a descriptive commit message, push to remote.

### 4. Install

```bash
make install
```

Confirm the binary was installed successfully.

## When NOT to use

- Mid-implementation (not all changes are done yet)
- Non-Go projects
- When the user only wants a subset (e.g., just commit, just review)
