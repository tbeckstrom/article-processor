# article_processor/main.py

import os
import argparse
import google.generativeai as genai
import glob
import time
from tqdm import tqdm
import logging
from .config_utils import load_config
from .api_client import GoogleAPIClient
from .file_utils import (create_output_dir,
                          create_article_output_dir,
                           generate_safe_file_name,
                            list_pdf_files,
                            move_processed_file)
from .ai_utils import generate_summary, generate_presentation
from .prompt_utils import load_prompt_template
# initialize logging at start of main.py
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)



def load_example_data(example_dir, api_client: GoogleAPIClient):
    """Loads example files for prompting."""
    example_summaries = []
    example_presentations = []

    for file_path in glob.glob(os.path.join(example_dir, "pdfs", "*.pdf")):
        file_name = os.path.basename(file_path)
        safe_name = generate_safe_file_name(file_name)
        summary_path = os.path.join(example_dir, "summaries",  f"{os.path.splitext(file_name)[0]}_summary_example.md")
        qmd_path = os.path.join(example_dir, "presentations", f"{os.path.splitext(file_name)[0]}.qmd")

        logger.debug(f"Summary path: {summary_path}\npresentation path: {qmd_path}")

        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary_content = f.read()

        else:
             summary_content = None
             logger.debug(f"Summary path doesn't exist: {summary_path}")

        if os.path.exists(qmd_path):
            with open(qmd_path, 'r', encoding='utf-8') as f:
                qmd_content = f.read()
        else:
            qmd_content = None
            logger.debug(f"Presentation path doesn't exist: {qmd_path}")

        example_pdf = None
        
        if os.path.exists(file_path):
             example_pdf = api_client.upload_file(file_path, safe_name)
        
        if example_pdf:
            if summary_content:
                example_summaries.append({"pdf":example_pdf,"summary":summary_content})
            if qmd_content:
                  example_presentations.append({"pdf": example_pdf, "qmd": qmd_content, "summary": summary_content})

    return example_summaries, example_presentations
        

def process_pdf(config, api_client, file_path, output_dir, example_summaries=None, example_presentations=None, run_summary = True, run_presentation = True):
    """Processes a single PDF file."""
    file_name = os.path.basename(file_path)
    safe_name = generate_safe_file_name(file_name)
    article_output_dir = create_article_output_dir(output_dir, safe_name)

    logger.debug(f'processing PDF - file name: {file_name}\nSafe Name: {safe_name}\Article output Dir: {article_output_dir}')

    pdf_file = api_client.get_file(safe_name)
    if not pdf_file:
        pdf_file = api_client.upload_file(file_path, safe_name)
        if not pdf_file:
            logger.debug(f"Failed to upload {file_name}, skipping...")
            return False # return if failed to upload

    

    if run_summary:
        print(f"Generating summary for: {file_name}")
        if not example_summaries:
            logger.debug(f'No example summaries provided,  skipping file')
            return True
        summary_text = generate_summary(config, api_client, pdf_file, example_summaries)
        summary_output_path = os.path.join(article_output_dir, f"{safe_name}_summary.md")
        with open(summary_output_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
            print(f"Summary written to: {summary_output_path}")
    else:
        summary_output_path = os.path.join(article_output_dir, f"{safe_name}_summary.md")
        if not os.path.exists(summary_output_path):
            print(f"Summary not found for: {file_name}, skipping presentation")
            logger.debug(f'Expected summary at path: {summary_output_path}')
            return True # dont need to move if only running presentation
        else:
            with open(summary_output_path, 'r', encoding='utf-8') as f:
                summary_text = f.read()
                print(f"Using summary from: {summary_output_path}")

    if run_presentation:
        print(f"Generating presentation for: {file_name}")
        if not example_presentations:
            logger.debug(f'No example presentations provided,  skipping file')
            return True
        presentation_output_path = os.path.join(article_output_dir, f"{safe_name}_presentation.qmd")
        presentation_text = generate_presentation(config, api_client, pdf_file, summary_text, example_presentations)
        with open(presentation_output_path, 'w', encoding='utf-8') as f:
           f.write(presentation_text)
           print(f"Presentation written to: {presentation_output_path}")
    return True


def main():
    """Main function to process PDFs."""
    parser = argparse.ArgumentParser(description="Process medical research PDFs.")
    parser.add_argument("--file", type=str, help="Path to a single PDF file to process.")
    parser.add_argument("--summary_only", action="store_true", help="Only generate summaries")
    parser.add_argument("--presentation_only", action="store_true", help="Only generate presentations")
    args = parser.parse_args()

    config = load_config()
    api_client = GoogleAPIClient(config["model_name"], config["retry_attempts"])
    create_output_dir(config["output_dir"])
    example_summaries, example_presentations = load_example_data(config["example_dir"], api_client)

    if args.file:
        if not os.path.exists(args.file):
             print("Error: file does not exist")
             return
        run_summary = not args.presentation_only
        run_presentation = not args.summary_only
        process_pdf(config, api_client, args.file, config["output_dir"], run_summary, run_presentation)

    else:
        pdf_files = list_pdf_files(config["input_dir"])
        if not pdf_files:
            print("No PDF files found in the input directory.")
            return

        for file_path in pdf_files:
            run_summary = not args.presentation_only
            run_presentation = not args.summary_only
            if process_pdf(config, api_client, file_path, config["output_dir"], example_summaries, example_presentations, run_summary, run_presentation): # only move if succesful
                move_processed_file(file_path, config["processed_dir"])

if __name__ == "__main__":
    main()