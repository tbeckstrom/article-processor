# article_processor/api_client.py
import google.generativeai as genai
import time
import google.api_core.exceptions
from googleapiclient.errors import HttpError
from google.api_core.exceptions import ServiceUnavailable
import logging
import httpx
from typing import List, Dict, Any
from google.generativeai.types import File
from .config_utils import get_api_key

logger = logging.getLogger(__name__)


class GoogleAPIClient:
    """Client for interacting with the Google Generative AI API."""

    def __init__(self, model_name, retry_attempts = 2):
          api_key = get_api_key()
          genai.configure(api_key=api_key)
          self.model = genai.GenerativeModel(model_name)
          self.retry_attempts = retry_attempts

    def _handle_api_error(self, e, attempt):
        if isinstance(e, ServiceUnavailable):
                logger.warning(f"503 error occurred (attempt {attempt+1}): {e}")
                if attempt < self.retry_attempts:
                   sleep_time = 2**(attempt)
                   logger.info(f"Sleeping for {sleep_time} seconds before retrying")
                   time.sleep(sleep_time)  # exponential backoff
                   return True
        elif isinstance(e, HttpError) and e.resp.status == 409 and "already exists" in str(e): #Check for googleapiclient's HttpError with 409
            logger.warning(f"409 error occurred, file exists {e}. Will try to get file")
            return 'file_exists'

        logger.exception(f"Error during API call (attempt {attempt+1}): {e}")
        return False # indicates retry should not occur

    def upload_file(self, file_path, file_name):
        """Uploads a file to the Google API."""
        for attempt in range(self.retry_attempts + 1):
            try:
                logger.debug(f"Uploading {file_name}, attempt {attempt+1}")
                file = genai.upload_file(path=file_path, mime_type='application/pdf', name=file_name)
                logger.debug(f"Uploaded {file_name} succesfully")
                return file
            except Exception as e:
                error_status = self._handle_api_error(e, attempt)
                if  error_status == 'file_exists': #if it is a 409 error, attempt to get the file
                    return self.get_file(file_name)
                elif error_status: #if retryable error, retry
                    continue
                else:
                    raise
        return None


    def get_file(self, file_name):
        """Gets a file from the Google API if it exists, otherwise returns None."""
        for attempt in range(self.retry_attempts + 1):
            try:
                files = genai.list_files()
                file_paths = [f.name for f in files]
                file_names = [fp.split('/')[-1] for fp in file_paths]
                
                logger.debug(f'Existing files: {file_names}')

                if file_name in file_names:
                    logger.debug(f"Getting {file_name}")
                    return genai.get_file(file_name)
                logger.debug(f"{file_name} not found")
                return None
            except Exception as e:
                error_status = self._handle_api_error(e, attempt)
                if error_status: #if retryable error, retry
                    continue
                else:
                    raise

        

    def generate_content(self, prompt_contents):
         """Generates content using the AI model."""
         for attempt in range(self.retry_attempts + 1):
                try:
                    response = self.model.generate_content(prompt_contents)
                    return response
                except Exception as e:
                    if self._handle_api_error(e, attempt):
                       continue
                    else:
                       raise
         return None

    