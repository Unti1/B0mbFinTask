from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from db.models.account import Account
from db.schemas.account import BaseAccount
from db.schemas.transaction import TransactionCreate

from settings.config import settings


router = APIRouter(prefix="/transaction")
limiter = Limiter(key_func=get_remote_address)

@router.post("/")
@limiter.limit("10/minute")
async def create_transaction(request: Request, data: TransactionCreate = Depends()):
    if data.to_account == data.from_account:
        raise HTTPException(400, "Нельзя отправлять переводы самому себе")

    async with ClientSession(
        base_url=f"http://{settings.HOST}:{settings.PORT}"
    ) as client:
        response_from = await client.get(f"/api/v1/account/{data.from_account}")
        response_to = await client.get(f"/api/v1/account/{data.to_account}")
        from_account_data = await response_from.json()
        to_account_data = await response_to.json()

        account_from = BaseAccount(**from_account_data)
        account_to = BaseAccount(**to_account_data)

    if data.amount > account_from.balance:
        return HTTPException(
            400, "На счёту отправителя недостаточно средств для совершения транзакции"
        )

    await Account.update(id=account_from.id, balance=account_from.balance - data.amount)
    await Account.update(id=account_to.id, balance=account_to.balance + data.amount)
    return {"status": "success"}
