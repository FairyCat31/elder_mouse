from typing import List

from disnake.ext import commands
from app.scripts.cogs.DynamicConfig import DynamicConfigShape as DynConf
from app.scripts.utils.urcon import RconManager
from app.scripts.utils.logger import LogType
from app.scripts.utils.smartdisnake import SmartBot, SmartEmbed
from app.scripts.utils.ujson import JsonManager, AddressType
from app.scripts.cogs.BM.DBHelper import DBManagerForBoosty
from disnake import Member, Role


class Sponsor:
    def __init__(self, bot: SmartBot, sponsor: Member, subscribe_role: Role):
        self.bot = bot
        self.discord: Member = sponsor
        self.subscribe_role: Role = subscribe_role
        # dyn vars for minecraft commands
        self.dyn_vars: dict = {}
        self.bonuses, self.punishments = self.__init_role_bonuses_and_punishments(self.subscribe_role.id)
        self.handle_funcs = {
            "info_msg": self.send_info_msg,
            "thx_embed": self.send_thx_embed,
            "mine_commands": self.run_cmd_on_server
        }

    @staticmethod
    def __init_role_bonuses_and_punishments(role_id: int) -> (dict, dict):
        boosty_jsm = JsonManager(AddressType.FILE, "boostysub.json")
        boosty_jsm.load_from_file()
        bonuses = {}
        punishments = {}
        for bonus_name, bonus_data in boosty_jsm["subs/default/when_add"].items():
            bonuses.setdefault(bonus_name, bonus_data)
        for bonus_name, bonus_data in boosty_jsm[f"subs/{role_id}/when_add"].items():
            bonuses[bonus_name] = bonus_data

        for pun_name, pun_data in boosty_jsm["subs/default/when_del"].items():
            punishments.setdefault(pun_name, pun_data)
        for pun_name, pun_data in boosty_jsm[f"subs/{role_id}/when_del"].items():
            punishments[pun_name] = pun_data

        return bonuses, punishments

    async def send_info_msg(self, msg_text: str) -> int:
        if not msg_text:
            return 0
        channel = self.bot.get_channel(self.bot.props["dynamic_config/boosty_channel"])
        msg_text = msg_text.format(user_name=self.discord.name, role_name=self.subscribe_role.name)
        await channel.send(msg_text)
        return 0

    async def send_thx_embed(self, embed_names: List[str]) -> int:
        embeds = []
        for embed_name in embed_names:
            embed_args = self.bot.props[f"embeds/{embed_name}"]
            embed = SmartEmbed(embed_args)
            embeds.append(embed)
        channel = self.bot.get_channel(self.bot.props["dynamic_config/boosty_channel"])
        await channel.send(content=self.discord.mention, embeds=embeds)
        return 0

    async def run_cmd_on_server(self, cmd_sessions: list) -> int:
        """
        # Execute commands on the servers
        cmd_sessions - [[server: str, commands: [STR, ...] ], ...]
            Output - [[BOOL, ...], ...]"""

        for data in cmd_sessions:
            rcon_manager = RconManager(data["server"])
            code, res = await rcon_manager.test_connect()
            if code:
                self.bot.log.printf(res, LogType.WARN)
                return 1
            else:
                response = await rcon_manager.cmd(data["commands"], dyn_vars=self.dyn_vars.copy())
                for text in response[0]:
                    self.bot.log.printf(text)

        return 0

    async def give_all_bonuses(self) -> int:
        result = 0
        for name_func, arg in self.bonuses.items():
            handler_func = self.handle_funcs[name_func]
            code = await handler_func(arg)
            if code:
                result = 1

        return result

    async def give_all_punishments(self) -> int:
        result = 0
        for name_func, arg in self.punishments.items():
            handler_func = self.handle_funcs[name_func]
            code = await handler_func(arg)
            if code:
                result = 1

        return result

class BoostyManager(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot
        self.db = DBManagerForBoosty()
        self.boosty_jsm = JsonManager(AddressType.FILE, "boostysub.json")
        self.boosty_jsm.load_from_file()
        self.boosty_roles_id = self.boosty_jsm["subs"].keys()

    async def set_dynamic_vars(self, sponsor: Sponsor):
        minecraft_name = self.db.get_minecraft_name(sponsor.discord.id)
        dyn_vars = {"minecraft_name": minecraft_name}
        sponsor.dyn_vars = dyn_vars.copy()

    async def update_booster_data(self, sponsor: Sponsor) -> int:
        return 0

    async def on_boosty_role_add(self, member: Member, new_role: Role):
        sponsor = Sponsor(self.bot, member, new_role)
        print(sponsor.discord.id, sponsor.discord.name, "[ + ]")
        await self.set_dynamic_vars(sponsor)
        await sponsor.give_all_bonuses()

    async def on_boosty_role_del(self, member: Member, del_role: Role):
        sponsor = Sponsor(self.bot, member, del_role)
        print(sponsor.discord.id, sponsor.discord.name, "[ - ]")
        await self.set_dynamic_vars(sponsor)
        await sponsor.give_all_punishments()

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
        if str(edited_role.id) not in self.boosty_roles_id:
            return

        # handling edit role event by special func for bot
        await handler_func(after, edited_role)


def setup(bot: SmartBot):
    bot.add_cog(BoostyManager(bot))
