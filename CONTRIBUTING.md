# Contributing

Keep changes small enough to explain. Start with a concrete problem, describe the expected behavior, and add a focused test when behavior changes.

1. Install `requirements-dev.txt` in a Python 3.12 virtual environment.
2. Add or update code and the relevant Sphinx guide.
3. Run `python -m scripts.ingest`, `python -m pytest -q`, and `python -m sphinx -W -b html docs docs/_build/html`.
4. For retrieval changes, compare the development benchmark with the previous report. Reserve test cases for final evaluation.
5. Never add keys, private documents, generated virtual environments or unsupported performance claims.

All demo documents are public. A new source must be original, fictional, or explicitly licensed for redistribution. Keep source metadata and citation tests aligned after changing documents.
