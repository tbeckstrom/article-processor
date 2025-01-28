# article_processor/prompt_utils.py
import os

def load_prompt_template(file_path):
    """Loads a prompt template from a file."""
    with open(file_path, "r", encoding='utf-8') as f:
        return f.read()


def build_prompt(instructions, examples, input_file, presentation=True, input_summary=None):
    """Builds a prompt with instructions, examples, and input."""
    prompt_contents = [instructions]
    summary_prompt = "Prompt: Please summarize the following article."
    presentation_prompt = "Prompt: Please create a quarto presentation using the following research article and its summary."
    if not presentation:

        for i,example in enumerate(examples, start=1):
            prompt_contents.append(f"<EXAMPLE{i}>")
            prompt_contents.append(summary_prompt) # this could be made an input as well
            prompt_contents.append(example["pdf"])
            prompt_contents.append("Response:")
            prompt_contents.append(example["summary"])
            prompt_contents.append(f"</EXAMPLE{i}>")

        prompt_contents.append(summary_prompt)
        prompt_contents.append(input_file)
        prompt_contents.append("Response:")
    else:

        for i,example in enumerate(examples, start=1):
            prompt_contents.append(f"<EXAMPLE{i}>")
            prompt_contents.append(presentation_prompt) 
            prompt_contents.append(example["pdf"])
            prompt_contents.append(example["summary"])
            prompt_contents.append("Response:")
            prompt_contents.append(example["qmd"])
            prompt_contents.append(f"</EXAMPLE{i}>")

        prompt_contents.append(presentation_prompt) 
        prompt_contents.append(input_file)
        prompt_contents.append(input_summary)
        prompt_contents.append("Response:")
    
    return prompt_contents