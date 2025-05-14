from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey
from dataclasses import dataclass
from sqlalchemy.orm import DeclarativeBase
from enum import Enum
class Base(DeclarativeBase):
    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


@dataclass
class Product(Base):
    __tablename__ = 'product'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    desc: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(255))
    brand: Mapped[str] = mapped_column(String(255))
    price: Mapped[int] = mapped_column()
    image_url: Mapped[str] = mapped_column(String(255))