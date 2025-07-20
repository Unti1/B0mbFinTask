

from decimal import Decimal
from sqlalchemy.orm import Mapped, relationship

from settings.database import Base


class Account(Base):
    owner_name: Mapped[str]
    balance: Mapped[Decimal]
    
    sent_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="sender_account",
        cascade="all, delete-orphan",
        foreign_keys="[Transaction.from_account]"
    )
    received_transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="receiver_account",
        cascade="all, delete-orphan",
        foreign_keys="[Transaction.to_account]"
    )