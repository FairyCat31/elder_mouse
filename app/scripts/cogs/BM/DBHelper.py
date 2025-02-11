from app.scripts.utils.DB.dbmanager import DBManager, DBType
from app.scripts.cogs.BM.models import User, Sponsor
from sqlalchemy.orm import Session
from sqlalchemy import select, insert


class DBManagerForBoosty(DBManager):
    def __init__(self):
        super().__init__("test", DBType.MySQL)


    @DBManager.db_session
    def get_minecraft_name(self, session: Session, ds_id: int) -> str:
        stmt = select(User).where(User.ds_id == ds_id)
        booster_info = session.scalars(stmt).one_or_none()
        if booster_info is None:
            return ""
        return booster_info.name

    # CREATE TABLE IF NOT EXISTS sponsors (
    #     id INTEGER PRIMARY KEY AUTO_INCREMENT,
    #     ds_id INTEGER NOT NULL,
    #     minecraft_name VARCHAR(16) NOT NULL,
    #     sponsor_role INTEGER NOT NULL,
    #     own_role INTEGER UNIQUE DEFAULT -1,
    #     mine_bonuses_status TINYINT(1) DEFAULT 0
    # );

    @DBManager.db_session
    def set_sponsor(self, session: Session,
                         ds_id: int,
                         minecraft_name: str,
                         sponsor_role: int,
                         own_role: int,
                         mine_bonuses_status: bool
                         ) -> None:
        stmt = insert(Sponsor).values(ds_id=ds_id, minecraft_name=minecraft_name, sponsor_role=sponsor_role,
                                      mine_bonuses_status=mine_bonuses_status, own_role=own_role)
        session.scalars(stmt)

    @DBManager.db_session
    def get_sponsor(self, session: Session, ds_id: int = None) -> list:
        stmt = select(Sponsor)

        if ds_id is not None:
            stmt = stmt.where(Sponsor.ds_id == ds_id)

        result = session.scalars(stmt).all()

        return result

