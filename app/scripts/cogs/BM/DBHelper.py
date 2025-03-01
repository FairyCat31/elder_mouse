from app.scripts.utils.DB.dbmanager import DBManager, DBType
from app.scripts.cogs.BM.models import User, Sponsor
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from typing import List


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
    def save_sponsor(self, session: Session, sponsor) -> None:
        ds_id = sponsor.discord.id
        sponsor_role = sponsor.subscribe_role.id
        minecraft_name = session.scalar(select(User.name).where(User.ds_id == ds_id))

        stmt = insert(Sponsor).values(ds_id=ds_id, sponsor_role=sponsor_role, minecraft_name=minecraft_name)
        session.execute(stmt)
        session.commit()

    @DBManager.db_session
    def update_sponsor(self, session: Session, sponsor) -> None:
        ds_id = sponsor.discord.id
        sponsor_role = sponsor.subscribe_role.id
        own_role = sponsor.own_role.id if sponsor.own_role is not None else -1
        mine_cmds_status = sponsor.mine_cmds_status

        stmt = (update(Sponsor).values(
            sponsor_role=sponsor_role,
            own_role=own_role,
            mine_bonuses_status=mine_cmds_status).where(Sponsor.ds_id == ds_id))
        session.execute(stmt)
        session.commit()

    @DBManager.db_session
    def get_sponsor(self, session: Session, ds_id: int = None) -> List[Sponsor]:
        stmt = select(Sponsor)

        if ds_id is not None:
            stmt = stmt.where(Sponsor.ds_id == ds_id)

        result = session.scalars(stmt).all()

        return result

    @DBManager.db_session
    def del_sponsor(self, session: Session, sponsor) -> None:
        stmt = delete(Sponsor).where(Sponsor.ds_id == sponsor.discord.id)

        session.execute(stmt)
        session.commit()
