# 📦 morchaos

A collection of utilities for file management, deduplication, and system monitoring.

## Features

- **File Deduplication**: Find and manage duplicate files using SHA-256 hashing
- **Image Deduplication**: Detect similar images using perceptual hashing
- **Source Code Deduplication**: Find duplicate source files with whitespace normalization
- **Ebook Catalogization**: Organize ebooks by author using metadata extraction
- **Ollama Chat Interface**: Interact with local Ollama models, supporting system/user prompts from strings or files, health checks, and model listing.
- **Prompt Manager**: A CLI tool and API for managing system prompts, including format conversion, listing, mapping nicknames to prompt files, and downloading prompts from online sources.
- **System Information**: Collect CPU, memory, disk, battery, and network statistics
- **PDF AI Analysis**: Analyze and process PDF documents using AI.
- **Empty Folder Cleaner**: Identify and remove empty directories.
- **File Content Cleaner**: Perform various cleaning operations on file content (e.g., remove newlines).
- **Folder Scanner**: Scan folders and output information about their contents.
- **Subfolder Creator**: Create subfolders based on defined patterns or lists.
- **CUDA/GPU Information**: Provide detailed information about CUDA and GPU availability and status.
- **Temporary Folder Cleaner**: Clean up temporary files and folders.
- **Directory Structure Creator**: Create complex directory structures from a declarative definition.
- **Directory Tree Printer**: Visualize directory structures.
- **JWT Encoder/Decoder**: Encode and decode JSON Web Tokens.
- **Sentiment Analysis**: Perform sentiment analysis on text data.
- **Simple TCP Server/Client**: Provide basic TCP client and server functionalities.
- **Image Generation (Stable Diffusion)**: Integrate image generation capabilities using Stable Diffusion models.
- **Stock Price Sentiment Analysis**: Analyze sentiment related to stock prices.
- **PDF AI Analysis**: Analyze and process PDF documents using AI.
- **Empty Folder Cleaner**: Identify and remove empty directories.
- **File Content Cleaner**: Perform various cleaning operations on file content (e.g., remove newlines).
- **Folder Scanner**: Scan folders and output information about their contents.
- **Subfolder Creator**: Create subfolders based on defined patterns or lists.
- **CUDA/GPU Information**: Provide detailed information about CUDA and GPU availability and status.
- **Temporary Folder Cleaner**: Clean up temporary files and folders.
- **Directory Structure Creator**: Create complex directory structures from a declarative definition.
- **Directory Tree Printer**: Visualize directory structures.
- **JWT Encoder/Decoder**: Encode and decode JSON Web Tokens.
- **Sentiment Analysis**: Perform sentiment analysis on text data.
- **Simple TCP Server/Client**: Provide basic TCP client and server functionalities.
- **Image Generation (Stable Diffusion)**: Integrate image generation capabilities using Stable Diffusion models.
- **Stock Price Sentiment Analysis**: Analyze sentiment related to stock prices.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/jonesdeveloperchung-pixel/morchaos.git
cd morchaos

# Install with Poetry
poetry install

# Or install with pip
pip install .
```

### Dependencies

- Python ≥3.10
- click (CLI framework)
- imagehash, Pillow (image processing)
- pdfplumber, python-docx, ebooklib (ebook metadata)
- psutil (system information)
- requests (HTTP client)
- ollama (Ollama API client)

## Usage

### Command Line Tools

After installation, the following console scripts are available:

#### Duplicate File Detection
```bash
# Find duplicates in a directory
duplicate --directory /path/to/files

# Delete duplicates (keeps first occurrence)
duplicate --directory /path/to/files --action delete

# Move duplicates to a separate directory
duplicate --directory /path/to/files --action move --target-dir /path/to/duplicates

# Filter by file extensions
duplicate --directory /path/to/files --extensions .txt .doc

# Ignore specific directories
duplicate --directory /path/to/files --ignore-dirs temp cache
```

#### Image Duplicate Detection
```bash
# Find similar images
image-diff --directory /path/to/images

# Adjust similarity threshold (0-64, lower = more strict)
image-diff --directory /path/to/images --threshold 10

# Specify image extensions
image-diff --directory /path/to/images --extensions .jpg .png .gif
```

#### Source Code Duplicate Detection
```bash
# Find duplicate source files (whitespace-insensitive)
source-diff --directory /path/to/code

# Specify source file extensions
source-diff --directory /path/to/code --extensions .py .js .java
```

#### Ebook Catalogization
```bash
# Preview metadata extraction
ebook-catalog --directory /path/to/ebooks --preview

# Organize ebooks by author (dry run)
ebook-catalog --directory /path/to/ebooks --dry-run

# Actually organize ebooks
ebook-catalog --directory /path/to/ebooks
```

#### Ollama Chat Interface
```bash
# Single prompt with default system prompt
chatbot -U "What is a closure in Python?"

# Single prompt with custom system prompt
chatbot -S "You are a sarcastic Unix expert." -U "Explain virtual memory."

# Single prompt with system prompt from file
chatbot --sf system_prompt.file -U "What is a closure in Python?"

# Single prompt with system prompt from JSON file
chatbot --sf system_prompt.json -U "What is a closure in Python?"

# Use a prompt nickname (after mapping with prompt-manager map to create prompt_file_map.json in the current directory)
chatbot --sf my_awesome_prompt -U "Tell me more!"

# Interactive chat mode
chatbot --interactive

# Use a different model
chatbot -m llama2 --interactive

# Check endpoint health
chatbot --health-check

# List available models
chatbot --list-models
```

#### Prompt Manager
```bash
# Convert a text prompt to JSON format
prompt-manager convert input.txt output.json

# Convert a JSON prompt to text format
prompt-manager convert input.json output.txt

# List all prompt files in the current directory
prompt-manager list

# List all prompt files in a specific directory
prompt-manager list /path/to/prompts

# Map prompt files in the default folder to nicknames and save to prompt_file_map.json (default output file for chatbot)
prompt-manager map

# Map prompt files in a specific folder and save to a custom file
prompt-manager map /path/to/my_prompts --output-file my_map.json

# Download a prompt from DocsBot.ai and save it to the current directory
prompt-manager download https://docsbot.ai/prompts/category/my-awesome-prompt

# Download a prompt and save it to a specific output directory
prompt-manager download https://docsbot.ai/prompts/category/my-awesome-prompt --output-dir my_downloads
```

#### System Information
```bash
# Show all system information
system-info

# Show specific category
system-info --category cpu
system-info --category memory

# Output as JSON
system-info --json
```

### Python API

```python
from morchaos.core import duplicate, image, source, ebook, ollama_chat, system, prompt_manager
from morchaos.core.ollama_chat import run_chat, health_check, list_models # Import core functions directly
from pathlib import Path

# Find duplicate files
duplicates = duplicate.find_duplicates(Path("/path/to/files"))
duplicate.act_on_duplicates(duplicates, "delete")

# Find similar images
similar_images = image.find_image_duplicates(Path("/path/to/images"))

# Find duplicate source code
source_duplicates = source.find_source_duplicates(Path("/path/to/code"))

# Catalogize ebooks
ebook.catalogize(Path("/path/to/ebooks"))

# Use ollama chat (example using the core functions directly)
import asyncio
async def chat_example():
    messages = [{"role": "user", "content": "Hello!"}]
    await run_chat(messages) # Use the run_chat function directly

# asyncio.run(chat_example()) # This would run the example

# Convert a prompt programmatically
input_txt = Path("my_prompt.txt")
input_txt.write_text("My system prompt content.")
output_json = Path("my_prompt.json")
prompt_manager.convert_prompt_format(input_txt, output_json)

# List prompts programmatically
all_prompts = prompt_manager.list_prompts(Path("."))

# Map prompt files programmatically
prompt_mappings = prompt_manager.map_prompt_files(Path("TODO/system_prompt_collection/docsbot_prompts"), Path("my_custom_map.json"))


# Get system information
cpu_info = system.get_cpu_info()
memory_info = system.get_memory_info()
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
poetry install --with dev

# Run tests
pytest

# Run tests with coverage
pytest --cov=morchaos --cov-report=html

# Type checking
mypy morchaos

# Code formatting
black morchaos tests

# Linting
flake8 morchaos tests
```

### Project Structure

```
morchaos/
├── core/                 # Business logic modules
│   ├── duplicate.py      # SHA-256 duplicate detection
│   ├── image.py          # Perceptual hash image comparison
│   ├── source.py         # Source code normalization
│   ├── ebook.py          # Ebook metadata extraction
│   ├── ollama_chat.py    # Ollama chat integration
│   ├── prompt_manager.py # Prompt management functions
│   ├── system.py         # System information collection
│   └── file_utils.py     # File utilities
├── cli/                  # Command-line interfaces
│   ├── duplicate.py      # duplicate command
│   ├── image_diff.py     # image-diff command
│   ├── source_diff.py    # source-diff command
│   ├── ebook_catalog.py  # ebook-catalog command
│   ├── ollama_chat.py    # chatbot command
│   ├── prompt_manager.py # prompt-manager command
│   └── system_info.py    # system-info command
├── logger/               # Logging configuration
└── tests/                # Test suite
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions of all kinds! To get started:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Make your changes with clear commit messages
4. Run tests and ensure code quality checks pass
5. Submit a pull request

### Guidelines

- Follow the existing code style (PEP8)
- Include tests for new features or bug fixes
- Document new functionality in the README or docstrings
- Be respectful and constructive in code reviews and discussions

---

Let me know if you'd like a CONTRIBUTING.md or LICENSE file scaffolded next, or if you want to add badges, changelogs, or CI instructions.