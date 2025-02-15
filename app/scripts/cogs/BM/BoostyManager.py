from typing import List, Dict

from disnake.ext import commands
from app.scripts.cogs.DynamicConfig import DynamicConfigShape as DynConf
from app.scripts.utils.urcon import RconManager
from app.scripts.utils.logger import LogType
from app.scripts.utils.smartdisnake import SmartBot, SmartEmbed
from app.scripts.utils.ujson import JsonManager, AddressType
from app.scripts.cogs.BM.DBHelper import DBManagerForBoosty
from disnake import Member, Role, User, AllowedMentions


class Sponsor:
    def __init__(self, bot: SmartBot, sponsor: Member, subscribe_role: Role):
        self.bot = bot
        self.discord: Member = sponsor
        self.subscribe_role: Role = subscribe_role
        self.own_role: Role | None = None
        self.mine_cmds_status: int = 0
        # dyn vars for minecraft commands
        self.dyn_vars: dict = {}
        self.bonuses, self.punishments = self.__init_role_bonuses_and_punishments(self.subscribe_role.id)
        self.handle_funcs = {
            "info_msg": self.send_info_msg,
            "thx_embed": self.send_thx_embed,
            "mine_commands": self.run_cmd_on_server
        }

    def __repr__(self):
        return f"Sponsor(discord={self.discord.name})"

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
        msg_text = msg_text.format(user_name=self.discord.mention, role_name=self.subscribe_role.mention)
        await channel.send(msg_text, allowed_mentions=AllowedMentions(users=False, roles=False))
        return 0

    async def send_thx_embed(self, embed_names: List[str]) -> int:
        embeds = []
        embeds_dyn_vars = {"member": self.discord.name}
        for embed_name in embed_names:
            embed_args = self.bot.props[f"embeds/{embed_name}"]
            embed = SmartEmbed(embed_args, embeds_dyn_vars)
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

    async def give_all_bonuses(self) -> dict:
        result_codes = {}
        for name_func, arg in self.bonuses.items():
            handler_func = self.handle_funcs[name_func]
            code = await handler_func(arg)
            result_codes[name_func] = code

        return result_codes

    async def give_all_punishments(self) -> dict:
        result_codes = {}
        for name_func, arg in self.punishments.items():
            handler_func = self.handle_funcs[name_func]
            code = await handler_func(arg)
            result_codes[name_func] = code

        return result_codes

class BoostyManager(commands.Cog):
    def __init__(self, bot: SmartBot):
        self.bot = bot
        self.db = DBManagerForBoosty()
        self.boosty_jsm = JsonManager(AddressType.FILE, "boostysub.json")
        self.boosty_jsm.load_from_file()
        self.boosty_roles_id = self.boosty_jsm["subs"].keys()
        self.sponsor_map: Dict[int, Sponsor] = {}

    async def set_dynamic_vars(self, sponsor: Sponsor):
        minecraft_name = self.db.get_minecraft_name(sponsor.discord.id)
        dyn_vars = {"minecraft_name": minecraft_name}
        sponsor.dyn_vars = dyn_vars.copy()


    async def on_boosty_role_add(self, member: Member, new_role: Role):
        sponsor = Sponsor(self.bot, member, new_role)
        self.db.save_sponsor(sponsor)
        print(sponsor.discord.id, sponsor.discord.name, "[ + ]")
        await self.set_dynamic_vars(sponsor)
        codes = await sponsor.give_all_bonuses()
        mine_cmds_status = codes.get("mine_commands")
        if mine_cmds_status == 0:
            sponsor.mine_cmds_status = 1
            self.db.update_sponsor(sponsor)

        self.sponsor_map[sponsor.discord.id] = sponsor


    async def on_boosty_role_del(self, sponsor: Sponsor):
        print(sponsor.discord.id, sponsor.discord.name, "[ - ]")
        self.db.del_sponsor(sponsor)
        await sponsor.give_all_punishments()
        del self.sponsor_map[sponsor.discord.id]

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
            handler_func = "add"
            bigger, smaller = new_roles, old_roles
        else:
            bigger, smaller = old_roles, new_roles
            handler_func = "sub"

        edited_role = None
        for role in bigger:
            if role not in smaller:
                edited_role = role
                break

        # check if edited role from boosty subs
        if str(edited_role.id) not in self.boosty_roles_id:
            return

        # handling edit role event by special func for bot
        if handler_func == "add":
            await self.on_boosty_role_add(after, edited_role)
        elif handler_func == "sub":
            await self.on_boosty_role_del(self.sponsor_map[after.id])

    @commands.Cog.listener(name="on_ready")
    @DynConf.is_cfg_setup("boosty_channel", "guild", echo=False)
    async def sync_sponsors(self):
        self.bot.log.printf("Start loading data of sponsors ...")
        data_all_sponsors = self.db.get_sponsor()
        # LOAD SPONSORS FROM DATABASE
        guild = self.bot.get_guild(self.bot.props["dynamic_config/guild"])
        for data_sponsor in data_all_sponsors:
            member = guild.get_member(data_sponsor.ds_id)
            role = guild.get_role(data_sponsor.sponsor_role)
            if member is None:
                member = self.bot.get_user(data_sponsor.ds_id)
            sponsor = Sponsor(self.bot, member, role)
            self.sponsor_map[data_sponsor.ds_id] = sponsor
        self.bot.log.printf("Data of sponsors loaded [ ✅  ]")
        self.bot.log.printf("Start syncing data of sponsors ...")
        ghosts = 0
        news = 0
        for sponsor in list(self.sponsor_map.values()):
                if type(sponsor.discord) == User:
                    await self.on_boosty_role_del(sponsor)
                    ghosts += 1
                    continue
                if sponsor.subscribe_role not in sponsor.discord.roles:
                    await self.on_boosty_role_del(sponsor)
                    ghosts += 1
                    continue

        for role_id in self.boosty_roles_id:
            if role_id == "default":
                continue
            role = guild.get_role(int(role_id))

            for member in role.members:
                if member.id not in self.sponsor_map.keys():
                    await self.on_boosty_role_add(member, role)
                    news += 1
                    continue
        self.bot.log.printf(f"Ghosts ({ghosts}) and News ({news}) were found")
        self.bot.log.printf("Syncing data of sponsors complete [ ✅  ]")
        print(self.sponsor_map.values())



def setup(bot: SmartBot):
    bot.add_cog(BoostyManager(bot))
