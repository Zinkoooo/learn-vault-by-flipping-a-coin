from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

class Score(Base):
    __tablename__ = "score"

    id: Mapped[int] = mapped_column(primary_key=True)
    heads: Mapped[int] = mapped_column(default=0, nullable=False)
    tails: Mapped[int] = mapped_column(default=0, nullable=False)
