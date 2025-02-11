from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ds_id: Mapped[str] = mapped_column(String(36))
    name: Mapped[str] = mapped_column(String(255))

    def __repr__(self):
        return f"User(id={self.id!r}, ds_id={self.ds_id!r}, name={self.name!r}, verified={self.verified!r})"


class Sponsor(Base):
    __tablename__ = "sponsors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ds_id: Mapped[int] = mapped_column(Integer())
    minecraft_name: Mapped[str] = mapped_column(String(16))
    sponsor_role: Mapped[int]  = mapped_column(Integer())
    own_role: Mapped[int] = mapped_column(Integer(), unique=True)
    mine_bonuses_status: Mapped[int] = mapped_column(Boolean())

    def __repr__(self):
        return (f"User(id={self.id!r}, ds_id={self.ds_id!r}, minecraft_name={self.minecraft_name!r}," +
                f" sponsor_role={self.sponsor_role!r}, own_role={self.own_role!r}, " +
                f"mine_bonuses_status{self.mine_bonuses_status!r})")
