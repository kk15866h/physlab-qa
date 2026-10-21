# Release checklist

This checklist is intended to keep PhysLab QA releases reproducible and scientifically reviewable.

## Before a release

1. Confirm the version in `pyproject.toml`, `src/physlab_qa/__init__.py`, and CLI `--version` output agree.
2. Run the complete test suite on all supported Python versions through GitHub Actions.
3. Run the installed-wheel smoke test, not only editable-install tests.
4. Run `ruff check --select F src tests examples` to catch undefined names and related correctness errors.
5. Run `python -m build` and `python -m twine check dist/*`.
6. Re-run the synthetic pendulum example and inspect the generated Markdown report.
7. Review `docs/numerical-design.md` for any changed assumptions, formulas, or limitations.
8. Update `CHANGELOG.md` with user-visible changes and known limitations.
9. Verify that README installation commands work from a clean environment.
10. Do not claim validation against real experiments unless the underlying dataset, provenance, and comparison have actually been reviewed.

## Release notes should state

- What changed.
- Which Python versions were tested.
- Whether numerical behavior changed.
- Which assumptions apply to uncertainties and weighted fitting.
- Any known correctness limitations.
- Whether examples use synthetic or real data.

## After a release

- Keep the release immutable except for documentation corrections clearly described as such.
- Triage external bug reports and numerical discrepancies promptly.
- Add a regression test for every confirmed correctness bug when practical.
- Preserve links to the exact commit used for published analyses.
