# 📦 `morchaos` – System Architecture & Implementation Blueprint  

Below is a **complete, production‑ready design** that turns the ad‑hoc scripts into a single, maintainable, testable, and distributable Python package.  
It covers:

* High‑level architecture diagram  
* Component specifications (core, CLI, logging, packaging, CI)  
* Data models & public interfaces  
* Implementation guidelines (type hints, error handling, logging, tests)  
* Technology stack & tooling recommendations  
* Extensibility & future‑proofing  

---

## 1.  Architecture Overview

```
┌───────────────────────────────────────────────────────────────────────┐
│                           morchaos package                            │
│ ┌───────────────────────────────────────────────────────────────────┐│
│ │  ┌───────────────────────┐  ┌───────────────────────┐           ││
│ │  │  core/ (business logic)│  │  cli/ (command‑line)  │           ││
│ │  └───────────────────────┘  └───────────────────────┘           ││
│ │  ┌───────────────────────┐  ┌───────────────────────┐           ││
│ │  │  logger/ (global log) │  │  tests/ (unit tests)  │           ││
│ │  └───────────────────────┘  └───────────────────────┘           ││
│ │  ┌───────────────────────┐  ┌───────────────────────┐           ││
│ │  │  pyproject.toml (meta)│  │  docs/ (Sphinx)       │           ││
│ │  └───────────────────────┘  └───────────────────────┘           ││
│ └───────────────────────────────────────────────────────────────────┘│
│  ┌───────────────────────────────────────────────────────────────────┐│
│  │  CI/CD (GitHub Actions) – matrix: Windows / macOS / Linux        ││
│  └───────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────────────┘
```

* **core/** – pure, deterministic functions that implement the business logic.  
* **cli/** – thin wrappers that expose the core functions as console scripts (using `click`).  
* **logger/** – a single module that configures a global logger; all other modules import it.  
* **tests/** – pytest test suite with fixtures, mocks, and coverage ≥ 90 %.  
* **pyproject.toml** – Poetry‑managed build metadata, dependencies, and entry points.  
* **docs/** – Sphinx documentation (auto‑generated from docstrings).  
* **CI** – GitHub Actions matrix that installs the package, runs tests, linting, type‑checking, and builds the wheel/sdist.

---

## 2.  Component Specifications

| Component | Responsibility | Key Files | Public API |
|-----------|----------------|-----------|------------|
| **core.file_utils** | Path sanitisation, temp‑dir cleanup | `core/file_utils.py` | `safe_path(path: str | Path) -> Path`<br>`remove_temp_dirs(root: Path, patterns: Iterable[str]) -> int` |
| **core.duplicate** | SHA‑256 duplicate detection | `core/duplicate.py` | `find_duplicates(root: Path, extensions: Iterable[str], ignore_dirs: Iterable[str]) -> Dict[str, List[Path]]`<br>`act_on_duplicates(groups: Dict[str, List[Path]], action: Literal["delete","move"], target_dir: Optional[Path])` |
| **core.image** | Perceptual hash & image duplicate detection | `core/image.py` | `phash_for_file(path: Path) -> str`<br>`find_image_duplicates(root: Path, extensions: Iterable[str]) -> Dict[str, List[Path]]` |
| **core.source** | Whitespace‑insensitive source‑code hashing | `core/source.py` | `normalize_hash(path: Path) -> str`<br>`find_source_duplicates(root: Path, extensions: Iterable[str]) -> Dict[str, List[Path]]` |
| **core.ebook** | Metadata extraction & catalogisation | `core/ebook.py` | `catalogize(root: Path, dry_run: bool = False) -> int` |
| **core.ollama_chat** | HTTP client for local Ollama/Chat‑model | `core/ollama_chat.py` | `run_chat(messages: List[Dict[str, str]], model: str, url: str, timeout: int)`<br>`health_check(url: str, timeout: int) -> bool`<br>`list_models(url: str, timeout: int) -> list[dict[str, any]]` |
| **core.system** | System metrics | `core/system.py` | `get_cpu_info() -> Dict[str, Any]`<br>`get_memory_info() -> Dict[str, Any]`<br>`get_disk_info() -> Dict[str, Any]`<br>`get_battery_info() -> Dict[str, Any]`<br>`get_network_info() -> Dict[str, Any]` |
| **logger.init_logging** | Global logger configuration | `logger/__init__.py` | `init_logging(level: int = logging.INFO, fmt: str = DEFAULT_FMT)` |
| **cli.duplicate** | Console script `duplicate` | `cli/duplicate.py` | `main()` |
| **cli.image_diff** | Console script `image-diff` | `cli/image_diff.py` | `main()` |
| **cli.source_diff** | Console script `source-diff` | `cli/source_diff.py` | `main()` |
| **cli.ebook_catalog** | Console script `ebook-catalog` | `cli/ebook_catalog.py` | `main()` |
| **cli.ollama_chat** | Console script `chatbot` | `cli/ollama_chat.py` | `main()` |
| **cli.system_info** | Console script `system-info` | `cli/system_info.py` | `main()` |

> **Note** – All CLI modules use `click` for argument parsing, `logger` for output, and exit with `0` on success, `2` on user error, `1` on unexpected exception.

---

## 3.  Data Models & Interfaces

| Data | Type | Description | Example |
|------|------|-------------|---------|
| **Path** | `pathlib.Path` | All file system references. | `Path("/home/user/docs/report.pdf")` |
| **DuplicateGroup** | `Dict[str, List[Path]]` | Key = hash, value = list of duplicate files. | `{ "a3f5...": [Path("1.txt"), Path("2.txt")], ... }` |
| **ImageHash** | `str` | 64‑bit perceptual hash string (hex). | `"3f5a2b1c..."` |
| **SourceHash** | `str` | Normalised source‑code hash. | `"e4d909c290d0fb1ca068ffaddf22cbd0"` |
| **EbookMetadata** | `Dict[str, str]` | Keys: `author`, `title`, `format`. | `{ "author": "J.K. Rowling", "title": "Harry Potter", "format": "pdf" }` |
| **SystemInfo** | `Dict[str, Any]` | Sub‑dicts for CPU, memory, disk, battery, network. | `{ "cpu": {"cores": 8, "freq": 2800, "usage": 12.3}, ... }` |

### Public Function Signatures (core)

```python
# core/file_utils.py
def safe_path(path: str | Path) -> Path:
    """Return an absolute, resolved Path. Raises ValueError if path is outside root."""

def remove_temp_dirs(root: Path, patterns: Iterable[str]) -> int:
    """Delete directories matching patterns under root. Return number of dirs removed."""

# core/duplicate.py
def find_duplicates(
    root: Path,
    extensions: Iterable[str] = ("*",),
    ignore_dirs: Iterable[str] = (),
) -> Dict[str, List[Path]]:
    """Return mapping of SHA‑256 hash → list of duplicate files."""

def act_on_duplicates(
    groups: Dict[str, List[Path]],
    action: Literal["delete", "move"],
    target_dir: Optional[Path] = None,
) -> int:
    """Delete or move duplicate files. Return number of files processed."""
```

(Other modules follow the same pattern – pure functions, no side‑effects except file I/O.)

---

## 4.  Implementation Guidelines

### 4.1  Coding Style

| Rule | Tool | Notes |
|------|------|-------|
| PEP‑8 | `flake8` | `--max-line-length=88` |
| Type hints | `mypy` | `--strict` |
| Docstrings | `pydocstyle` | Google style, 2‑line summary + detailed description |
| Logging | `logging` | `logger.getLogger(__name__)` |
| Tests | `pytest` | `--cov=morchaos --cov-report=xml` |

### 4.2  Error Handling

* **User errors** – `click.BadParameter`, `ValueError`, `FileNotFoundError`.  
  * Log at `ERROR` level.  
  * Exit with code `2`.  
* **Unexpected errors** – catch `Exception` in `cli/*.py` wrappers, log stack trace, exit `1`.  
* **Core functions** – raise only `ValueError` / `FileNotFoundError` for invalid input; otherwise let the exception propagate (tests will assert on it).

### 4.3  Global Logger

```python
# logger/__init__.py
DEFAULT_FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

def init_logging(level: int = logging.INFO, fmt: str = DEFAULT_FMT) -> None:
    """Configure root logger once per process."""
    logging.basicConfig(level=level, format=fmt, datefmt="%Y-%m-%d %H:%M:%S")
```

All modules import `from logger import init_logging, logger` and call `init_logging()` in the CLI entry point.

### 4.4  File‑I/O & Performance

* **Chunked hashing** – read files in 64 KiB blocks to keep memory usage low.  
* **Parallelism** – optional `concurrent.futures.ThreadPoolExecutor` for image hashing (CPU‑bound).  
* **Avoiding recursion** – use `os.scandir()` or `Path.rglob()`; skip ignored dirs early.  
* **Dry‑run support** – `core.ebook.catalogize` accepts `dry_run=True` to list actions without moving files.

### 4.5  Tests & Fixtures

```python
# tests/conftest.py
@pytest.fixture
def tmp_dir(tmp_path):
    """Return a temporary directory with a deterministic file tree."""
```

* **Mocking** – `pytest-mock` for `requests` (chatbot) and `psutil` (system).  
* **Coverage** – `pytest-cov` + `--cov-report=xml` for GitHub Actions.  
* **Test data** – small, reproducible file sets (text, images, source, ebooks).  

### 4.6  Packaging & Distribution

* **Poetry** – `pyproject.toml` contains:

```toml
[tool.poetry]
name = "morchaos"
version = "0.1.0"
description = "Utility scripts for file deduplication, image diff, source diff, ebook catalog, chatbot, and system metrics."
authors = ["Your Name <you@example.com>"]
readme = "README.md"
packages = [{include = "morchaos"}]

[tool.poetry.dependencies]
python = "^3.10"
click = "^8.1"
imageio = "^2.31"
imageio-ffmpeg = "^0.4.9"
imagehash = "^4.3"
requests = "^2.31"
psutil = "^5.9"
ebooklib = "^0.18"
tqdm = "^4.66"

[tool.poetry.scripts]
duplicate = "morchaos.cli.duplicate:main"
image-diff = "morchaos.cli.image_diff:main"
source-diff = "morchaos.cli.source_diff:main"
ebook-catalog = "morchaos.cli.ebook_catalog:main"
chatbot = "morchaos.cli.ollama_chat:main"
system-info = "morchaos.cli.system_info:main"
archive-org = "morchaos.cli.archive_org:main"
xkcd = "morchaos.cli.xkcd:main"
youtube = "morchaos.cli.youtube:main"
email-bot = "morchaos.cli.email_bot:main"
geocode = "morchaos.cli.geocode:main"
prompt-manager = "morchaos.cli.prompt_manager:main"

[build-system]
requires = ["poetry-core>=1.0"]
build-backend = "poetry.core.masonry.api"
```

* **Build** – `poetry build` → `dist/*.whl` + `dist/*.tar.gz`.  
* **Test** – `poetry run pytest`.  
* **Lint** – `poetry run flake8`.  
* **Type‑check** – `poetry run mypy morchaos`.  
* **Docs** – `poetry run sphinx-build docs docs/_build`.

---

## 5.  Technology Stack & Tooling

| Layer | Library / Tool | Why |
|-------|----------------|-----|
| **Path handling** | `pathlib` | Modern, type‑safe, cross‑platform |
| **Argument parsing** | `click` | Declarative, auto‑help, supports sub‑commands |
| **Logging** | `logging` | Standard, configurable, no external deps |
| **Hashing** | `hashlib`, `imagehash` | Fast, battle‑tested |
| **Image I/O** | `imageio`, `Pillow` | Handles JPEG/PNG/… |
| **Source parsing** | `tokenize`, `re` | No external deps |
| **Ebook metadata** | `ebooklib` | Supports PDF, EPUB, MOBI, etc. |
| **HTTP client** | `requests` | Simple, well‑tested |
| **System metrics** | `psutil` | Cross‑platform, high‑level API |
| **Build & deps** | `Poetry` | Declarative, lockfile, virtual env |
| **Testing** | `pytest`, `pytest-cov`, `pytest-mock` | BDD‑style, fixtures |
| **Linting** | `flake8`, `pydocstyle` | CI quality gate |
| **Type‑checking** | `mypy` | Static safety |
| **Docs** | `Sphinx` + `autodoc` | Auto‑generated API docs |
| **CI** | GitHub Actions | Matrix: Windows / macOS / Linux, `python-3.10` |

---

## 6.  CI / CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  build-test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: [3.10]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install Poetry
        run: pip install poetry
      - name: Install deps
        run: poetry install --no-root
      - name: Lint
        run: |
          poetry run flake8 morchaos
          poetry run pydocstyle morchaos
      - name: Type‑check
        run: poetry run mypy morchaos
      - name: Test
        run: poetry run pytest --cov=morchaos --cov-report=xml
      - name: Build
        run: poetry build
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist-${{ matrix.os }}
          path: dist/
```

* The job uploads the built wheel/sdist for manual inspection.  
* `--cov-report=xml` is consumed by the `codecov` action if you want PR checks.

---

## 7.  Extensibility & Future Proofing

| Feature | How it’s supported | Example |
|---------|-------------------|---------|
| **Add a new deduplication algorithm** | Create a new `core.<name>.py` module, expose a `find_<name>_duplicates` function, add a CLI wrapper. | `core.audio.py` → `find_audio_duplicates` |
| **Change the hash algorithm** | Update the core function; CLI remains unchanged. | Switch SHA‑256 → SHA‑512 in `core.duplicate` |
| **Add a new console script** | Add a `cli/<name>.py` that calls the core function. | `cli.audio_diff.py` |
| **Support a new ebook format** | Extend `core.ebook.extract_metadata` to parse the format. | Add support for `epub` via `ebooklib` |
| **Add a new system metric** | Add a new function in `core.system` and expose it via `cli.system_info`. | `get_gpu_info()` |
| **Change logging format** | Update `logger/__init__.py` and re‑run `init_logging()` in the CLI. | Add color via `colorlog` if desired |

> **Why this works** – All public APIs are **pure functions** (except for file I/O). Adding a new feature never touches the existing modules, so the risk of regressions is minimal.

---

## 8.  Sample Implementation Snippets

### 8.1  `core.duplicate.find_duplicates`

```python
# core/duplicate.py
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Iterable, Dict, List

def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def find_duplicates(
    root: Path,
    extensions: Iterable[str] = ("*",),
    ignore_dirs: Iterable[str] = (),
) -> Dict[str, List[Path]]:
    root = root.resolve()
    ignore_set = {Path(p).resolve() for p in ignore_dirs}
    groups: Dict[str, List[Path]] = defaultdict(list)

    for ext in extensions:
        for file in root.rglob(ext):
            if any(file.is_relative_to(ign) for ign in ignore_set):
                continue
            groups[_hash_file(file)].append(file)

    # Filter out groups with only one file
    return {h: files for h, files in groups.items() if len(files) > 1}
```

### 8.2  `cli.duplicate`

```python
# cli/duplicate.py
import click
from pathlib import Path
from logger import init_logging, logger
from core.duplicate import find_duplicates, act_on_duplicates

@click.command()
@click.argument("root", type=click.Path(exists=True, file_okay=False))
@click.option("--ext", "-e", multiple=True, default=("*.txt",), help="File extensions to scan.")
@click.option("--ignore", "-i", multiple=True, default=(), help="Directories to ignore.")
@click.option("--action", type=click.Choice(["delete", "move"]), default="delete")
@click.option("--target", type=click.Path(file_okay=False), default=None)
def main(root, ext, ignore, action, target):
    """Find and optionally delete/move duplicate files."""
    init_logging()
    root = Path(root).resolve()
    target_dir = Path(target).resolve() if target else None

    groups = find_duplicates(root, extensions=ext, ignore_dirs=ignore)
    logger.info(f"Found {len(groups)} duplicate groups.")
    processed = act_on_duplicates(groups, action, target_dir)
    logger.info(f"Processed {processed} files.")
    click.echo(f"Done. {processed} files {action}ed.")
```

### 8.3  `logger/__init__.py`

```python
# logger/__init__.py
import logging

DEFAULT_FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

def init_logging(level: int = logging.INFO, fmt: str = DEFAULT_FMT) -> None:
    """Configure root logger once per process."""
    logging.basicConfig(level=level, format=fmt, datefmt="%Y-%m-%d %H:%M:%S")
```

All other modules simply do:

```python
from logger import init_logging, logger
```

---

## 9.  Testing Strategy

| Test Type | Purpose | Tool | Coverage |
|-----------|---------|------|----------|
| Unit tests | Verify pure functions | `pytest` | ≥ 90 % |
| Integration tests | Verify file‑system side‑effects | `pytest` + `tmp_path` fixture | |
| Mock external services | `requests` (chatbot) | `pytest-mock` | |
| Linting | `flake8` | CI gate |
| Type‑checking | `mypy` | CI gate |
| Documentation | `sphinx-build` | Auto‑generate from docstrings |

**Example fixture** – create a deterministic file tree:

```python
# tests/conftest.py
@pytest.fixture
def sample_dir(tmp_path):
    (tmp_path / "a.txt").write_text("foo")
    (tmp_path / "b.txt").write_text("foo")  # duplicate
    (tmp_path / "c.txt").write_text("bar")
    return tmp_path
```

**Test** – `tests/test_duplicate.py`

```python
def test_find_duplicates(sample_dir):
    groups = find_duplicates(sample_dir, extensions=("*.txt",))
    assert len(groups) == 1
    assert set(groups[next(iter(groups))]) == {sample_dir / "a.txt", sample_dir / "b.txt"}
```

---

## 10.  Documentation & User Guide

* **Sphinx** – `docs/conf.py` pulls in `autodoc` and `napoleon` for Google‑style docstrings.  
* **Read‑the‑Docs** – optional hosting; the docs are built automatically in CI.  
* **CLI help** – `click` automatically generates `--help` output.  

Example `duplicate --help`:

```
Usage: duplicate [OPTIONS] ROOT

  Find duplicate files under ROOT.

Options:
  -e, --ext TEXT  File extensions to scan (default: *.txt)
  -i, --ignore TEXT  Directories to ignore
  -a, --action [delete|move]  Action to perform on duplicates
  -t, --target TEXT  Target directory for move action
  --help             Show this message and exit.
```

---

## 11.  Extending the Package

| Scenario | How to add | Minimal changes |
|----------|------------|-----------------|
| **New deduplication algorithm** | Add `core.<name>.py` + `cli.<name>.py` | 1‑2 files, no changes elsewhere |
| **New CLI flag** | Add `click.option` in the relevant CLI module | No core changes |
| **New dependency** | Add to `[tool.poetry.dependencies]` | Re‑run `poetry lock` |
| **New platform support** | Add OS‑specific code in `core.system` (e.g., `psutil.sensors_battery()` on Linux) | No changes to CLI |

> **Why it scales** – The core layer is completely decoupled from the CLI and packaging. Adding a new feature only touches the new module(s) and the corresponding CLI wrapper.

---

## 12.  Summary Checklist

| ✅ | Item |
|---|------|
| **Core functions are pure** – no hidden state. |
| **Single logger configuration** – `logger.init_logging()` called once in CLI. |
| **Console scripts use `click`** – robust help, exit codes. |
| **Poetry build** – `pyproject.toml` with entry points. |
| **CI matrix** – Windows, macOS, Linux. |
| **Linting & type‑checking** – `flake8`, `mypy`, `pydocstyle`. |
| **Tests** – ≥ 90 % coverage, fixtures, mocks. |
| **Docs** – Sphinx auto‑generated from docstrings. |
| **Extensible** – add new modules without touching existing code. |

---

## 13.  Quick Start

```bash
# Install
pip install morchaos

# Find text duplicates
duplicate /home/user/docs --ext *.txt --ignore .git

# Move duplicates to a backup folder
duplicate /home/user/docs --ext *.txt --action move --target /home/user/backup

# Image perceptual diff
image-diff /home/user/photos

# Source‑code diff
source-diff /home/user/code

# Catalog ebooks
ebook-catalog /home/user/ebooks

# Ask the local chatbot
chatbot "What is the capital of France?"

# System metrics
system-info
```

All commands print nicely formatted logs and exit with the appropriate status code.

---

## 14.  Final Thoughts

* **Maintainability** – The separation of concerns (core vs CLI) keeps the codebase clean.  
* **Testability** – Pure functions are trivial to unit‑test; file‑system side‑effects are isolated in the CLI layer.  
* **Performance** – Chunked hashing, optional parallelism, and early directory pruning keep memory usage low.  
* **Security** – `safe_path()` guarantees that all file operations stay inside the user‑supplied root.  
* **Cross‑platform** – `pathlib`, `psutil`, and `click` work on Windows, macOS, and Linux.  
* **Future‑proof** – Adding new algorithms or metrics is a matter of dropping a new module into `core/` and a thin CLI wrapper.

Happy coding! 🚀