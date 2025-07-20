
from decimal import Decimal
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from settings.database import Base


class Transaction(Base):
    from_account: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    to_account: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    amount: Mapped[Decimal]
    
    sender_account: Mapped["Account"] = relationship(
        "Account",
        back_populates="sent_transactions",
        foreign_keys=[from_account]
    )
    receiver_account: Mapped["Account"] = relationship(
        "Account",
        back_populates="received_transactions",
        foreign_keys=[to_account]
    )