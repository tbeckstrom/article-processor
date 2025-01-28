# article_processor/file_utils.py

import os
import shutil
import re
from tqdm import tqdm


def create_output_dir(output_dir):
    """Creates the output directory if it doesn't exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def create_article_output_dir(output_dir, article_name):
    """Creates an output directory for a specific article."""
    article_output_dir = os.path.join(output_dir, article_name)
    if not os.path.exists(article_output_dir):
        os.makedirs(article_output_dir)
    return article_output_dir

def move_processed_file(file_path, processed_dir):
    """Moves a processed file to the processed directory."""
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
    try:
        shutil.move(file_path, processed_dir)
    except Exception as e:
        print(f"Error moving file: {e}")

def generate_safe_file_name(file_name):
        """Generates a safe file name compatible with Google File API."""
        name_without_extension = os.path.splitext(file_name)[0]
        safe_name = name_without_extension[:39] #Truncate to 39 characters
        safe_name = safe_name.lower()
        safe_name = re.sub(r'[^a-z0-9-]', '-', safe_name)
        safe_name = re.sub(r'-+', '-', safe_name).strip('-')
        return safe_name

def list_pdf_files(input_dir):
    """Lists all PDF files in the input directory."""
    pdf_files = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_files.append(os.path.join(input_dir, filename))
    return pdf_files