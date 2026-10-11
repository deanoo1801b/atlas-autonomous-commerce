# KKAM Books tests

From the repository root:

```bash
PYTHONPATH=kkam-books/src python -m unittest discover -s kkam-books/tests -v
```

The catalogue tests use only Python's standard library. PDF QA tests cover missing, malformed and too-small files. Valid-PDF page-count and render tests require the optional packages in `kkam-books/requirements-optional.txt` and should be added to CI after dependencies are installed.

Passing unit tests do not mean the n8n workflows have been imported or deployed.
