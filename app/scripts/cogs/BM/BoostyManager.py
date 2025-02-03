from disnake.ext import commands
from app.scripts.cogs.DynamicConfig import DynamicConfigShape as DynConf
from app.scripts.components.rconmanager import RconManager
from app.scripts.components.logger import LogType
from app.scripts.components.smartdisnake import SmartBot, SmartEmbed
from app.scripts.components.jsonmanager import JsonManager, AddressType
from app.scripts.cogs.BM.DBHelper import DBManagerForBoosty
from disnake import Member, Role


class Sponsor:
    def __init__(self, bot: SmartBot, sponsor: Member, subscribe_role: Role):
        self.bot = bot
        self.sponsor: Member = sponsor
        self.subscribe_role: Role = subscribe_role
        # dyn vars for minecraft commands
        self.dyn_vars: dict = {}
        self.bonuses = self.__get_role_bonuses(self.subscribe_role.id)
        self.bonuses_func = {
            "info_msg": self.send_info_msg,
            "thx_embed": self.send_thx_embed,
            "mine_commands": self.run_cmd_on_server
        }

    @staticmethod
    def __get_role_bonuses(role_id: int) -> dict:
        boosty_jsm = JsonManager(AddressType.FILE, "boostysub.json")
        boosty_jsm.load_from_file()
        bonuses = {}
        for bonus_name, bonus_data in boosty_jsm["subs/default"].items():
            bonuses.setdefault(bonus_name, bonus_data)
        for bonus_name, bonus_data in boosty_jsm[f"subs/{role_id}"].items():
            bonuses[bonus_name] = bonus_data

        return bonuses

    async def send_info_msg(self, msg_text: str) -> None:
        if not msg_text:
            return
        channel = self.bot.get_channel(self.bot.props["dynamic_config/sub_channel"])
        msg_text = msg_text.format(user_name=self.sponsor.name, role_name=self.sub.name)
        await channel.send(msg_text)

    async def send_thx_embed(self, embed_name: str) -> None:
        embed_args = self.bot.props[f"embeds/{embed_name}"]
        embed = SmartEmbed(embed_args)
        channel = self.bot.get_channel(self.bot.props["dynamic_config/sub_channel"])
        await channel.send(content=self.sponsor.mention, embed=embed)

    async def run_cmd_on_server(self, cmd_sessions: list) -> None:
        for data in cmd_sessions:
            rcon_manager = RconManager(data["server"])
            code, res = await rcon_manager.test_connect()
            if code:
                self.bot.log.printf(res, LogType.WARN)
            response = await rcon_manager.cmd(*data["commands"], dyn_vars=self.dyn_vars.copy())
            for text in response[0]:
                self.bot.log.printf(text)

    async def give_all_bonuses(self) -> None:
        for name_func, arg in self.bonuses.items():
            handler_func = self.bonuses_func[name_func]
            await handler_func(arg)


class BoostyManager(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot
        self.db = DBManagerForBoosty()
        self.boosty_jsm = JsonManager(AddressType.FILE, "boostysub.json")
        self.boosty_jsm.load_from_file()
        self.boosty_roles_id = self.boosty_jsm["subs"].keys()

        idcheck = self.db.get_minecraft_name(573129166132740096)
        print(idcheck)

    async def on_boosty_role_add(self, member: Member, new_role: Role):
        sponsor = Sponsor(self.bot, member, new_role)
        await sponsor.give_all_bonuses()

    async def on_boosty_role_del(self, member: Member, del_role: Role):
        did = member.id

    @commands.Cog.listener(name="on_member_update")
    @DynConf.is_cfg_setup("boosty_channel", echo=False)
    async def on_member_update(self, before: Member, after: Member):
        new_roles = after.roles
        old_roles = before.roles
        new_is = len(new_roles)
        old_is = len(old_roles)
        # check if updated roles
        if new_is == old_is:
            return
        # catch edited role and handler function
        if new_is > old_is:
            handler_func = self.on_boosty_role_add
            bigger, smaller = new_roles, old_roles
        else:
            bigger, smaller = old_roles, new_roles
            handler_func = self.on_boosty_role_del

        edited_role = None
        for role in bigger:
            if role not in smaller:
                edited_role = role
                break

        # check if edited role from boosty subs
        if str(edited_role) not in self.boosty_roles_id:
            return
        print(edited_role.id, edited_role.name)
        # handling edit role event by special func for bot
        await handler_func(after, edited_role)


def setup(bot: SmartBot):
    bot.add_cog(BoostyManager(bot))
