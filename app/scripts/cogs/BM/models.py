from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    ds_id: Mapped[str] = mapped_column(String(36))
    name: Mapped[str] = mapped_column(String(255))
    verified: Mapped[int] = mapped_column(Integer())

    def __repr__(self):
        return f"User(id={self.id!r}, ds_id={self.ds_id!r}, name={self.name!r}, verified={self.verified!r})"
