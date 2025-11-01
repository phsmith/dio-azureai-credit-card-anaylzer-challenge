from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

from app.utils.config import (
    AZUREAI_DOCUMENTINTELLIGENCE_API_KEY,
    AZUREAI_DOCUMENTINTELLIGENCE_ENDPOINT,
)

document_intelligence_client = DocumentIntelligenceClient(
    AZUREAI_DOCUMENTINTELLIGENCE_ENDPOINT,
    AzureKeyCredential(AZUREAI_DOCUMENTINTELLIGENCE_API_KEY),
)


def analyze_credit_card(file):
    with open(file, "rb") as fd:
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-creditCard", body=fd
        )

    return poller.result()
