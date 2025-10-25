# 📦 `morchaos` – Requirements Analysis & Acceptance Criteria  

> **Goal** – Turn a set of ad‑hoc scripts into a single, maintainable, testable, and distributable Python package.  
> **Audience** – Future maintainers, CI/CD engineers, and any developer that may import the library or run the bundled CLIs.

---

## 1.  Scope & Vision

| Item | Description |
|------|-------------|
| **Scope** | All logic currently in ad‑hoc scripts is moved into a single package (`morchaos`). |
| **Vision** | A clean separation between *domain logic* (`core/`) and *command‑line glue* (`cli/`). |
| **Deliverables** | • `morchaos` package (source + tests) <br>• `pyproject.toml` with Poetry metadata <br>• Console‑script entry points <br>• Basic documentation skeleton |

---

## 2.  Functional Requirements (FR)

| FR‑ID | Requirement | Acceptance Criteria |
|-------|-------------|---------------------|
| **FR‑01** | **Core modules** – expose pure functions for each domain area. | • `core.file_utils` contains `safe_path`, `remove_temp_dirs`, etc. <br>• Each function has a documented signature and returns the expected type. |
| **FR‑02** | **Duplicate detection** – find duplicate files by SHA‑256. | • `duplicate.find_duplicates(root, extensions, ignore_dirs)` returns a `Dict[str, List[Path]]` where each list has ≥ 2 items. <br>• `act_on_duplicates` can delete or move files based on user‑supplied action. |
| **FR‑03** | **Image deduplication** – compute perceptual hash and find duplicates. | • `image.phash_for_file(path)` returns a 64‑bit hash string. <br>• `find_image_duplicates` returns a mapping similar to `duplicate.find_duplicates`. |
| **FR‑04** | **Source‑code deduplication** – whitespace‑insensitive comparison. | • `source.normalize_hash(path)` returns a deterministic hash. <br>• `find_source_duplicates` returns a mapping of identical source files. |
| **FR‑05** | **Ebook catalogisation** – extract author metadata and move files. | • `ebook.catalogize(root)` moves each ebook into `<root>/<author>/` preserving original filename. <br>• Supports PDF, EPUB, MOBI, DOCX. |
| **FR‑06** | **Chatbot wrapper** – simple HTTP client for local Ollama/Chat‑model endpoints. | • `run_chat(messages, ...)` returns a string response. <br>• Handles streaming responses. |
| **FR‑07** | **System info collector** – expose CPU, memory, disk, battery, network data. | • `system.get_cpu_info()` returns a dict with keys `cores`, `freq`, `usage`. <br>• All getters return a dict of primitives. |
| **FR‑08** | **CLI wrappers** – thin `argparse`/`click` scripts that call core functions. | • Each CLI prints a helpful `--help` message. <br>• CLI exits with status 0 on success, non‑zero on error. |
| **FR‑09** | **Logging** – global logger configured once. | • `logger.init_logging()` sets a console handler with level `INFO`. <br>• All modules use `logging.getLogger(__name__)`. |
| **FR‑10** | **Testing** – unit‑test skeletons for every core module. | • `tests/` contains at least one test per function. <br>• `pytest` runs without errors. |
| **FR‑11** | **Packaging** – build‑ready `pyproject.toml`. | • `poetry build` produces a wheel and sdist. <br>• Console scripts are registered (`duplicate`, `image-diff`, etc.). |
| **FR‑12** | **Extensibility** – easy to add new file‑type deduplication or CLI wrappers. | • Adding a new module in `core/` and a corresponding CLI in `cli/` should require no changes to existing code. |

---

## 3.  Non‑Functional Requirements (NFR)

| NFR‑ID | Requirement | Acceptance Criteria |
|--------|-------------|---------------------|
| **NFR‑01** | **Performance** – duplicate detection must finish in < 30 s for 10 k files on a typical laptop. | • Benchmark script reports average runtime < 30 s on a 10 k file set. |
| **NFR‑02** | **Memory Footprint** – peak usage < 200 MB. | • `psutil.Process().memory_info().rss` stays below 200 MB during duplicate scan. |
| **NFR‑03** | **Security** – no arbitrary code execution from user input. | • All file paths are resolved via `Path.resolve()`; no `eval` or `exec`. |
| **NFR‑04** | **Maintainability** – code follows PEP‑8, type hints, and uses `logging`. | • `flake8` and `mypy` pass with no errors. |
| **NFR‑05** | **Testability** – pure functions, deterministic outputs. | • Unit tests cover 90 %+ of core code; no hidden state. |
| **NFR‑06** | **Distribution** – installable via `pip install morchaos`. | • `pip install .` installs package and entry points without errors. |
| **NFR‑07** | **Documentation** – docstrings for all public APIs. | • `pydoc` shows meaningful help for each function. |
| **NFR‑08** | **Cross‑Platform** – works on Windows, macOS, Linux. | • Tests run on all three OSes in CI. |

---

## 4.  Constraints

| Constraint | Impact |
|------------|--------|
| **Python version** | Must support ≥ 3.10 (Poetry default). |
| **Dependencies** | Only the listed libraries (imagehash, Pillow, pdfplumber, psutil, requests, etc.). |
| **File system** | Assumes POSIX‑style paths; Windows paths are expanded via `Path.home()`. |
| **Network** | Chatbot requires a running local Ollama/Chat‑model endpoint; no external API keys. |
| **CI** | Must run on GitHub Actions (or similar) with minimal setup. |

---

## 5.  Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Large file sets** | Medium | Duplicate detection may exceed time/memory limits. | Use incremental hashing; allow `--max-depth` CLI flag. |
| **Binary file corruption** | Low | Hashing may fail. | Wrap file reads in try/except; skip unreadable files. |
| **Ebook metadata extraction failure** | Medium | Catalogisation may mis‑classify. | Fallback to filename parsing; log warnings. |
| **Chatbot endpoint downtime** | Low | CLI may hang. | Timeout on HTTP requests; graceful error message. |
| **Dependency version drift** | Medium | Build failures. | Pin versions in `pyproject.toml`; use Poetry lock. |
| **Cross‑platform path issues** | Medium | File moves may fail on Windows. | Use `Path` everywhere; test on all OSes. |

---

## 6.  Acceptance Criteria (High‑Level)

1. **Build & Install**  
   * `poetry install` installs all dependencies.  
   * `poetry build` produces a wheel and sdist.  
   * `pip install .` installs the package and registers console scripts.

2. **Core Functionality**  
   * Running `duplicate --directory ./data` lists duplicate groups.  
   * Running `image-diff --directory ./images` lists image duplicates.  
   * Running `ebook-catalog --directory ./ebooks` moves files into `<root>/<author>/`.  
   * `run_chat(...)` returns a non‑empty string.

3. **Logging & Error Handling**  
   * All modules log at `INFO` level.  
   * Invalid arguments produce a clear error message and exit code 2.  
   * Unexpected exceptions are caught in CLI and exit with code 1.

4. **Testing**  
   * `pytest` runs all tests with ≥ 90 % coverage.  
   * CI pipeline passes on Windows, macOS, Linux.

5. **Documentation**  
   * `pydoc morchaos.core.duplicate` shows a concise description.  
   * CLI `--help` displays all options.

6. **Performance**  
   * Duplicate scan of 10 k files completes in < 30 s on a 2 GHz laptop.  
   * Peak memory < 200 MB.

7. **Extensibility**  
   * Adding a new `core/` module and a corresponding CLI in `cli/` does not break existing tests or builds.

---

## 7.  Test Plan (Skeleton)

```text
tests/
├─ test_file_utils.py
│   ├─ test_safe_path()
│   └─ test_sanitize_filename()
├─ test_duplicate.py
│   ├─ test_find_duplicates()
│   └─ test_act_on_duplicates()
├─ test_image.py
│   ├─ test_phash_for_file()
│   └─ test_find_image_duplicates()
├─ test_source.py
│   ├─ test_normalize_hash()
│   └─ test_find_source_duplicates()
├─ test_ebook.py
│   ├─ test_catalogize()
│   └─ test_author_extraction()
├─ test_ollama_chat.py
│   └─ test_run_chat()
├─ test_system.py
│   └─ test_get_cpu_info()
└─ conftest.py   # fixtures for temp dirs, mock responses
```

Each test file should:

* Use `tmp_path` fixture for isolated file system.  
* Mock external calls (`requests.post`, `psutil`) where appropriate.  
* Assert expected outputs and side‑effects (e.g., file moves).  

---

## 8.  Glossary

| Term | Definition |
|------|------------|
| **Core** | Pure business logic modules (`core/`). |
| **CLI** | Thin command‑line wrappers (`cli/`). |
| **Duplicate** | Files with identical content (hash). |
| **Perceptual Hash** | Image similarity metric (`imagehash`). |
| **Author Extraction** | Metadata extraction from ebook formats. |
| **Chatbot** | HTTP client for local language‑model endpoints, via the `ollama_chat` module. |
| **Entry Point** | Console script defined in `pyproject.toml`. |

---

### Final Note

The above requirements analysis, acceptance criteria, and test plan provide a clear roadmap for turning the ad‑hoc scripts into a robust, maintainable, and distributable `morchaos` package.  Once the implementation follows these specs, the package will be ready for CI/CD pipelines, future extensions, and community use.