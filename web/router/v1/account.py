from typing import Annotated
from fastapi import APIRouter, Body, Depends, Path, Query, Request, Response
from fastapi_cache.coder import JsonCoder
from fastapi_cache.decorator import cache
from slowapi import Limiter
from slowapi.util import get_remote_address

from db.models.account import Account
from db.schemas.account import AccountCreate, BaseAccount


router = APIRouter(prefix="/account")
limiter = Limiter(key_func=get_remote_address)


async def custom_key_builder(
    func, namespace: str = "", *, request: Request, response: Response, **kwargs
):
    uid = request.path_params["uid"]
    account = await Account.get(id=uid)
    updated_at = account.updated_at.isoformat()
    return f"account:{uid}:{updated_at}"


@router.get("/all")
@limiter.limit("20/minute")
async def get_all_accounts(request: Request, limit: Annotated[int, Query()] = None):
    accounts = await Account.get_all(limit=limit)
    json_accounts = [
        BaseAccount.model_validate(account).model_dump(mode="json")
        for account in accounts
    ]
    return json_accounts


@router.get("/{uid}")
@limiter.limit("20/minute")
@cache(expire=60 * 5, coder=JsonCoder, key_builder=custom_key_builder)
async def get_concrete_account(
    request: Request, uid: Annotated[str, Path(min_length=36, max_length=36)]
):
    account = await Account.get(id=uid)
    return BaseAccount.model_validate(account).model_dump(mode="json")


@router.post("/")
@limiter.limit("20/minute")
async def create_account(request: Request, data: AccountCreate):
    json_data = data.model_dump(mode="json")
    account = await Account.create(**json_data)
    return {"uid": account.id}
