# article_processor/ai_utils.py
import os
import pandas
import logging
from .api_client import GoogleAPIClient
from .prompt_utils import load_prompt_template, build_prompt

logger = logging.getLogger(__name__)

def generate_summary(config, api_client: GoogleAPIClient, pdf_file, example_summaries):
    """Generates a summary of the research article."""
    instructions = load_prompt_template(config["summary_instructions_path"])
    prompt_contents = build_prompt(instructions,example_summaries, pdf_file, presentation=False)
    # logger.debug(f'{prompt_contents}')
    response = api_client.generate_content(prompt_contents)
    return response.text

def generate_presentation(config, api_client, pdf_file, summary, example_presentations):
    """Generates a presentation based on the research article and summary."""
    instructions = load_prompt_template(config["presentation_instructions_path"])
    prompt_contents = build_prompt(instructions, example_presentations, pdf_file, presentation=True, input_summary=summary)
    # logger.debug(f'{prompt_contents}')
    response = api_client.generate_content(prompt_contents)
    return response.text
