import os
import tempfile

from dotenv import load_dotenv

load_dotenv()

AZUREAI_DOCUMENTINTELLIGENCE_ENDPOINT = os.environ.get(
    "AZUREAI_DOCUMENTINTELLIGENCE_ENDPOINT"
)
AZUREAI_DOCUMENTINTELLIGENCE_API_KEY = os.environ.get(
    "AZUREAI_DOCUMENTINTELLIGENCE_API_KEY"
)
FILE_CHUNK_SIZE = os.environ.get("FILE_CHUNK_SIZE", 1024 * 1024)  # 1 MB
FILE_MAX_UPLOAD_SIZE = os.environ.get("FILE_MAX_UPLOAD_SIZE", 5 * 1024 * 1024)  # 5 MB
FILE_UPLOAD_TEMP_DIR = tempfile.TemporaryDirectory()
