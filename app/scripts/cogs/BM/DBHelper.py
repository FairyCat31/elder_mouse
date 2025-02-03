from app.scripts.components.dbmanager.dbmanager import DBManager, DBType
from app.scripts.cogs.BM.models import User
from sqlalchemy.orm import Session
from sqlalchemy import select


class DBManagerForBoosty(DBManager):
    def __init__(self):
        super().__init__("main", DBType.MySQL)

    @DBManager.db_session
    def get_minecraft_name(self, session: Session, ds_id: int) -> (int, int):
        stmt = select(User).where(User.ds_id == ds_id)
        booster_info = session.scalars(stmt).one_or_none()
        if booster_info is None:
            return -1, 0
        return booster_info.verified, booster_info.name
