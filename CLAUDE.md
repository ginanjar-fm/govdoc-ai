# Git Configuration

When committing to git, always use:

```
git -c user.name="ginanjar.fm" -c user.email="ginanjar.fahrul.m@gmail.com" commit ...
```

All agents must use this identity for every commit. Never use the system default git user.

# Commit Convention

All commit messages MUST follow conventional commit format:

- `feat:` - New features
- `fix:` - Bug fixes
- `test:` - Test additions/changes
- `docs:` - Documentation updates
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Format: `<type>: <short description>` (lowercase, no period at end, imperative mood).

**IMPORTANT: NEVER add "Co-Authored-By" trailers to commit messages.** No attribution lines of any kind. Commit messages must contain ONLY the subject line and optional body. No trailers.
