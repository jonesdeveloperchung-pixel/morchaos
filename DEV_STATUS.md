# Development Status

## Specifications

All specifications are located in the `specifications` folder.

- `requirements_specification.md`
- `source_code.md`
- `system_design.md`

## Ongoing Integration

All ongoing integration data, code, and files are located in the `TODO` folder. Each subdirectory represents a separate feature or task.

- `GPU`
- `Img_Catalog`
- `llama`
- `LLMs`
- `Lottery`
- `MCP`
- `Misc`
- `OPENAI`
- `powershell`
- `Python`
- `python-utilities`
- `system_prompt_collection`

## New Features

### Filename Safety / Renaming Utility
*   **Description**: Develop a robust utility for safe and intelligent filename handling.
*   **Capabilities**:
    *   Sanitize filenames by removing invalid characters, replacing spaces, and enforcing length limits.
    *   Perform safe renaming operations, including conflict resolution to prevent accidental overwrites or data loss.
    *   Potential integration with existing file management tools within `morchaos`.
*   **Relevant files**: `filename_safty.py`, `safe_rename.py`.

### Prompt Content Transformation and Display
*   **Description**: Provide utilities for transforming prompt content between formats and displaying prompt details.
*   **Capabilities**:
    *   Convert text prompts to JSON format and vice-versa (functionality covered by `prompt-manager convert`).
    *   Display the content of a prompt file, potentially by nickname.
*   **Relevant files**: `txt2json.py` (functionality covered), `print_prompt.py`.

### Code Generation / OOP System Prompt Integration
*   **Description**: Extend AI capabilities to assist with code generation and adherence to specific programming paradigms.
*   **Capabilities**:
    *   Integrate specialized system prompts within `ollama-chat` or a new dedicated CLI tool (e.g., `morchaos code-gen`) for code generation tasks (e.g., "Generate Python class for X").
    *   Facilitate adherence to Object-Oriented Programming (OOP) principles through AI-guided prompt application.
    *   Explore integration with existing source code analysis tools in `morchaos`.
*   **Relevant files**: `OOP_system_prompt.py`.

### Role-based Prompting System
*   **Description**: Implement a system for managing and applying different AI roles or personas.
*   **Capabilities**:
    *   Allow users to define and select "roles" or "personas" that encapsulate a system prompt along with other AI interaction settings (e.g., default model, temperature, response style).
    *   Enhance the prompt management feature to support the creation and application of these roles.
*   **Relevant files**: `role_collector.py`.

### PDF AI Analysis
*   **Description**: Integrate AI capabilities to analyze and process PDF documents.
*   **Capabilities**:
    *   Extract information from PDFs using AI models.
    *   Summarize PDF content.
    *   Answer questions based on PDF content.
*   **Relevant files**: `pdf_analysis_with_ollama.py`, `process_pdfs_with_ai.py`, `pdf_processor.py`.

### Empty Folder Cleaner
*   **Description**: Utility to identify and remove empty directories.
*   **Capabilities**:
    *   Scan a specified directory for empty subfolders.
    *   Optionally remove identified empty folders.
*   **Relevant files**: `remove_empty_folders.py`.

### File Content Cleaner
*   **Description**: Perform various cleaning operations on file content.
*   **Capabilities**:
    *   Remove specific characters or patterns (e.g., newlines, extra spaces).
    *   Standardize file content.
*   **Relevant files**: `remove_newline_from_file.py`.

### Folder Scanner
*   **Description**: Tool to scan and output information about folder contents.
*   **Capabilities**:
    *   Scan a directory and list files/folders based on criteria.
    *   Output folder structure in various formats.
*   **Relevant files**: `scan_folder_and_output.py`.

### Subfolder Creator
*   **Description**: Utility to create subfolders based on defined patterns or lists.
*   **Capabilities**:
    *   Generate a hierachy of subfolders under a given root.
    *   Can be used for organizing files into predefined structures.
*   **Relevant files**: `subfolder_creator.py`.

### CUDA/GPU Information
*   **Description**: Provide detailed information about CUDA and GPU availability and status.
*   **Capabilities**:
    *   Check if CUDA is available.
    *   Display GPU properties and usage.
*   **Relevant files**: `check_cuda_availability.py`, `check_cuda_installation.py`.

### Temporary Folder Cleaner
*   **Description**: Clean up temporary files and folders to free up disk space.
*   **Capabilities**:
    *   Identify and remove temporary files created by the system or applications.
    *   Clear specified temporary directories.
*   **Relevant files**: `cleanup_temp_folders.py`.

### Directory Structure Creator
*   **Description**: Create complex directory structures from a declarative definition.
*   **Capabilities**:
    *   Read a configuration (e.g., YAML, JSON) defining a directory tree.
    *   Create directories and empty files as specified.
*   **Relevant files**: `create_directory_structure.py`.

### Directory Tree Printer
*   **Description**: Visualize directory structures.
*   **Capabilities**:
    *   Print a textual representation of a directory tree.
    *   Optionally filter by depth or file types.
*   **Relevant files**: `directory_tree_printer.py`.

### JWT Encoder/Decoder
*   **Description**: A utility for encoding and decoding JSON Web Tokens.
*   **Capabilities**:
    *   Encode data into a JWT.
    *   Decode and verify JWT tokens.
*   **Relevant files**: `jwt_encode.py`.

### Sentiment Analysis
*   **Description**: Perform sentiment analysis on text data.
*   **Capabilities**:
    *   Determine the emotional tone of text (positive, negative, neutral).
    *   Can be applied to various text inputs.
*   **Relevant files**: `sentiment-analysis.py`.

### Simple TCP Server/Client
*   **Description**: Provide basic TCP client and server functionalities.
*   **Capabilities**:
    *   Set up a simple TCP server to listen for connections.
    *   Implement a simple TCP client to send/receive data.
*   **Relevant files**: `simple_tcp_server_client.py`.

### Image Generation (Stable Diffusion)
*   **Description**: Integrate image generation capabilities using Stable Diffusion models.
*   **Capabilities**:
    *   Generate images from text prompts.
    *   Configure generation parameters (e.g., resolution, steps).
*   **Relevant files**: `stable_diffusion_inference.py`, `generate_stable_diffusion_image.py`.

### Stock Price Sentiment Analysis
*   **Description**: Analyze sentiment related to stock prices, potentially integrating with financial data sources.
*   **Capabilities**:
    *   Extract news or social media text for a given stock.
    *   Perform sentiment analysis on extracted text to gauge market sentiment.
*   **Relevant files**: `stock_price_sentiment-analysys.py`.

## Completed Tasks

- Implemented `ollama-chat` command with `argparse` CLI.
- Integrated system and user prompt handling (string, file, JSON for system).
- Added health check and list models functionality.
- Implemented interactive chat mode.
- Wrote comprehensive unit tests for `ollama-chat`.
- Implemented **Prompt Management CLI/API**:
    *   Created `morchaos.core.prompt_manager` with functions for reading, converting, listing, and downloading prompts.
    *   Created `morchaos.cli.prompt_manager` with `convert`, `list`, `map`, and `download` subcommands.
    *   Integrated `read_prompt` into `morchaos.cli.ollama_chat`.
    *   Added `prompt-manager` script entry to `pyproject.toml`.
    *   Wrote comprehensive unit tests for `prompt-manager`.
- Implemented **Prompt File Mapper Integration**:
    *   Added `extract_nickname`, `map_prompt_files`, and `save_mapping_to_json` to `morchaos.core.prompt_manager`.
    *   Added `map` subcommand to `morchaos.cli.prompt_manager`.
    *   Modified `morchaos.cli.ollama_chat` to load `prompt_file_map.json` and resolve nicknames.
