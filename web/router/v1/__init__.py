from fastapi import APIRouter
from web.router.v1.account import router as account_router
from web.router.v1.transaction import router as transaction_router

router = APIRouter(prefix="/v1")
router.include_router(account_router)
router.include_router(transaction_router)
