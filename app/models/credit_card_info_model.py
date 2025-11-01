from pydantic import BaseModel


class CreditCardInfo(BaseModel):
    card_holder_name: str | None
    card_number: str | None
    expiriration_date: str | None
    bank_issuer: str | None
