# Research Article Processor

This project is a command-line tool designed to process medical research articles in PDF format. It uses the Google Generative AI API to summarize the articles and generate Quarto slideshow presentations based on these summaries.

## Features

-   **Batch Processing:** Processes multiple PDF files from an input directory.
-   **Google File API Integration:** Uploads PDFs to Google's file storage for processing and retrieves them if already uploaded.
-   **AI-Powered Summarization:** Generates summaries of research articles using the Google Generative AI API.
-   **AI-Powered Presentation Generation:** Creates Quarto presentations from the summaries and the original PDFs.
-   **Configurable:** Uses a `config.yaml` file for flexible configuration.
-   **Command-Line Interface:** Allows you to specify which processing steps to run via command line.

## Prerequisites

Before you begin, ensure you have met the following requirements:

1.  **Python 3.7+:** Make sure you have Python 3.7 or higher installed.
2.  **Google Generative AI API Key:** You will need to obtain a Google Generative AI API key.
3.  **Quarto:** You need to have [Quarto](https://quarto.org/) installed to render the generated presentations (from .qmd to .pptx).

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment:**

    *   On macOS/Linux:

        ```bash
        source venv/bin/activate
        ```
    *   On Windows:

        ```bash
        venv\Scripts\activate
        ```
4.  **Install required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```
    This will install the project dependencies
    - `google-generativeai`
    - `PyYAML`
    - `httpx`
    - `tqdm`
    - `google-api-core`
    - `google-auth`

## Configuration

1.  **Create a `config.yaml` file:** This file contains the configuration of the program.  It should be placed in the root of the project folder.  You can use the `config.yaml` file provided in the repo as a template.
2.  **Create `secrets.yaml`**: This is where you store your API key.  This file should also be placed in the root of the project folder.

    Your `secrets.yaml` file should look like the following:

    ```yaml
    api_key: "YOUR_ACTUAL_API_KEY"
    ```

    Replace `"YOUR_ACTUAL_API_KEY"` with your actual Google Generative AI API key.

**Configuration Options:**

*   **`model_name`**: The name of the Google Generative AI model to use (e.g., "gemini-2.0-flash-exp").
*   **`input_dir`**: The directory where the input PDF files are located (default: "pdfs_to_process").
*   **`output_dir`**: The directory where output summaries and presentations are saved (default: "output").
*   **`processed_dir`**: The directory where processed PDF files are moved (default: "processed").
*   **`summary_instructions_path`**: Path to the file containing instructions for generating summaries (default: "prompts/summary_instructions.md").
*   **`presentation_instructions_path`**: Path to the file containing instructions for generating presentations (default: "prompts/presentation_instructions.txt").
*   **`retry_attempts`**: The maximum number of retry attempts for API calls (default: 2).
*   **`secrets_file`**: The path to the secrets file that contains the API key (default: "secrets.yaml")

## Usage

### Command-Line Arguments

The script uses `argparse` to provide a command-line interface with the following arguments:

*   `--file`: Path to a single PDF file to process. If this is specified, other files in the input dir are skipped.
*   `--summary_only`: Only generate summaries and don't generate presentations.
*   `--presentation_only`: Only generate presentations (if summary output is present) and don't generate summaries.

### Examples

1.  **Process all PDFs in the input directory:**

    ```bash
    python -m article_processor.main
    ```
    This command will process all `.pdf` files in the `pdfs_to_process` folder (or the folder you configured in `config.yaml`) and move them into the `processed` folder. Summaries and presentations are placed into an output folder under the `output` directory.

2.  **Process a single PDF file:**

    ```bash
    python -m article_processor.main --file path/to/your/file.pdf
    ```

3.  **Only generate summaries:**

    ```bash
     python -m article_processor.main --summary_only
    ```
4. **Only generate presentations (assuming you have already generated summaries)**
    ```bash
     python -m article_processor.main --presentation_only
    ```

## Output

The processed output is placed within the output directory specified in `config.yaml`.
* For each PDF in the input dir, a sub folder is created with the safe filename.
* In this folder, a `*_summary.md` and `*_presentation.qmd` is generated (if the appropriate arguments are given)
*   The `.md` files contain the summary output for that article, and the `.qmd` files contain a quarto presentation output based on that article.

## Rendering Presentations

The generated `.qmd` files are Quarto files. You can render these files into presentation formats using the Quarto CLI.  For example to render to a PPTX file you can run the following command in the folder where the qmd file is located:

   ```bash
      quarto render *.qmd --to pptx
   ```
   This will generate a pptx file that can be used for a presentation

