# INSTRUCTIONS.md

## Purpose
This document defines the workflow and standards for AI agents when processing PROMPTs in this repository.

## Language Policy
- All source code, including tests, code comments, changelogs, and commit messages, **must be written in English**.

## Workflow
1. **Code Implementation**
   - Implement the requested feature or fix in English.
   - Write all code comments and docstrings in English.
   - Update or create tests for new or changed functionality (in English).
   - Update the changelog (CHANGES.md) in English if applicable.

2. **Code Formatting**
   - After completing code changes, run:
     - `uv run isort .` (to sort imports)
     - `uv run black .` (to format code)

3. **Translation Management**
   - If new descriptions or user-facing text were added or changed:
     - Extract new/updated strings to `.pot` files.
     - Update and merge translation files (`.po`).
     - Remove `fuzzy` flags from updated translations.
     - Remove unused translations.
     - Compile translations.

4. **Testing**
   - Add or update tests for all new/changed code.
   - Run tests and check code coverage using `pytest`.
   - If coverage is less than 100%, add tests until full coverage is achieved.

5. **Commit Preparation**
   - Prepare a commit message in English summarizing the changes for review/acceptance.

## Summary Checklist
- [ ] All code, comments, changelogs, and commit messages are in English
- [ ] Code formatted with isort and black
- [ ] Translations extracted, updated, cleaned, and compiled (if needed)
- [ ] Tests added/updated for all changes
- [ ] 100% test coverage verified
- [ ] Commit message prepared in English

---

**Follow this instruction for every PROMPT processed by AI agents in this repository.**
