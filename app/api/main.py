import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile

from app.models.credit_card_info_model import CreditCardInfo
from app.services.azure.document_intelligence import analyze_credit_card
from app.services.file_upload import upload_file
from app.utils.config import FILE_MAX_UPLOAD_SIZE, FILE_UPLOAD_TEMP_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    FILE_UPLOAD_TEMP_DIR.cleanup()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"status": "ok", "max_upload_size_bytes": FILE_MAX_UPLOAD_SIZE}


@app.post("/credit_card_info")
async def credit_card_info(file: UploadFile = File(...)) -> CreditCardInfo:
    """
    Process and analyze credit card information from an uploaded image file.

    This endpoint accepts an image file containing credit card information, processes it
    using OCR (Optical Character Recognition), and returns structured credit card details.

    Args:
        file (UploadFile): The uploaded image file containing credit card information.

    Returns:
        dict: A dictionary containing the extracted credit card information with the following fields:

            - card_holder_name (str): Name of the card holder
            - card_number (str): Credit card number
            - expiriration_date (str): Card expiration date
            - bank_issuer (str): Name of the issuing bank

        Or in case of error:
            dict: A dictionary with an 'error' key containing the error message

    Raises:
        Exception: If there's an error during file processing or analysis

    Note:
        The uploaded file is automatically deleted after processing, regardless of success or failure.
    """
    try:
        file_upload_result = await upload_file(file)
        credit_card_info = analyze_credit_card(file_upload_result["path"])
        credit_card_fields = credit_card_info["documents"][0]["fields"]

        if not credit_card_fields:
            return {"error": "The uploaded file is not a valid credit card image."}

        return {
            "card_holder_name": credit_card_fields.get("CardHolderName", {}).get(
                "content"
            ),
            "card_number": credit_card_fields.get("CardNumber", {}).get("content"),
            "expiriration_date": credit_card_fields.get("ExpirationDate", {}).get(
                "content"
            ),
            "bank_issuer": credit_card_fields.get("IssuingBank", {})
            .get("content", "")
            .replace("\n", " "),
        }
    except Exception as error:
        return {"error": str(error)}
    finally:
        os.remove(file_upload_result["path"])
