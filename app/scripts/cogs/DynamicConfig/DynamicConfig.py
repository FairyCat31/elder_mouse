from app.scripts.components.smartdisnake import SmartBot
from app.scripts.cogs.DynamicConfig.DynamicConfigElder import DynamicConfigElder


CLASS_CONFIG_BY_NAME = {
    "ElderMouse": DynamicConfigElder
}


def setup(bot: SmartBot):
    dynamic_config_class = CLASS_CONFIG_BY_NAME.get(bot.name)
    if dynamic_config_class is None:
        raise ImportError(f"Can't found class config for bot {bot.name}")

    bot.add_cog(dynamic_config_class(bot))
