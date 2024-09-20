from disnake.ext import commands
from app.scripts.cogs.DynamicConfig.DynamicConfigHelper import is_cfg_setup
from app.scripts.components.rconmanager import RconManager
from app.scripts.components.logger import LogType
from app.scripts.components.smartdisnake import SmartBot, SmartEmbed
from app.scripts.components.jsonmanager import JsonManager, AddressType
from disnake import Member, Role


class Sponsor:
    def __init__(self, bot: SmartBot, sponsor: Member, sub: Role):
        self.bot = bot
        self.sponsor = sponsor
        self.sub = sub
        # dyn vars for minecraft commands
        self.dyn_vars = self.__get_dyn_var()
        self.bonuses = self.__get_role_bonuses(self.sub.id)
        self.bonuses_func = {
            "info_msg": self.send_info_msg,
            "thx_embed": self.send_thx_embed,
            "mine_commands": self.run_cmd_on_server
        }

    @staticmethod
    def __get_dyn_var():
        return {}

    @staticmethod
    def __get_role_bonuses(role_id: int) -> dict:
        boosty_jsm = JsonManager(AddressType.FILE, "boostysub.json")
        boosty_jsm.load_from_file()
        default_bonuses = boosty_jsm["subs/default"]
        role_bonuses = boosty_jsm[f"subs/{role_id}"]
        result = {**default_bonuses, **role_bonuses}
        print(result)
        return result

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

    async def run_cmd_on_server(self, data: dict) -> None:
        rcon_manager = RconManager(data["server"])
        if rcon_manager.code:
            self.bot.log.printf(rcon_manager.res, LogType.WARN)
        response = rcon_manager.cmd(data["commands"], self.dyn_vars)
        for text, code in response:
            print(text, code)

    async def give_all_bonuses(self) -> None:
        for name_func, arg in self.bonuses.items():
            handler_func = self.bonuses_func[name_func]
            await handler_func(arg)


class BoostyManager(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot
        self.boosty_jsm = JsonManager(AddressType.FILE, "boostysub.json")
        self.boosty_jsm.load_from_file()
        self.boosty_roles_id = self.boosty_jsm["subs"].keys()

    async def on_boosty_role_add(self, member: Member, new_role: Role):
        sponsor = Sponsor(self.bot, member, new_role)
        await sponsor.give_all_bonuses()

    async def on_boosty_role_del(self, member: Member, del_role: Role):
        did = member.id

    @commands.Cog.listener(name="on_member_update")
    async def on_member_update(self, before: Member, after: Member):
        res = is_cfg_setup(self.bot.props["dynamic_config"], "sub_channel")
        if res:
            self.bot.log.printf(res)
            return

        new_roles = after.roles
        old_roles = before.roles
        new_is = len(new_roles)
        old_is = len(old_roles)
        # check if updated roles
        if new_is == old_is:
            return
        # catch edited role and handler function
        role_edited = None
        handler_func = None
        if new_is > old_is:
            handler_func = self.on_boosty_role_add
            for i in range(new_is-1):
                if new_roles[i].name == old_roles[i].name:
                    continue
                role_edited = new_roles[i]
                break
            if role_edited is None:
                role_edited = new_roles[-1]
        elif old_is > new_is:
            handler_func = self.on_boosty_role_del
            for i in range(old_is-1):
                if new_roles[i].name == old_roles[i].name:
                    continue
                role_edited = old_roles[i]
                break
            if role_edited is None:
                role_edited = old_roles[-1]
        # check if edited role from boosty subs
        if str(role_edited.id) not in self.boosty_roles_id:
            return
        # handling edit role event by special func for bot
        await handler_func(after, role_edited)


def setup(bot: SmartBot):
    bot.add_cog(BoostyManager(bot))
