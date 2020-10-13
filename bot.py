from discord.ext import commands
import cogs

BOT_COLOR = 0x00FCDD
DATA_PATH = 'guild_data.json'


def run(discord_token, donate_url=None):
    """ Create the bot, add the cogs and run it. """
    bot = commands.Bot(command_prefix=('a!', 'A!'), case_insensitive=True)
    bot.add_cog(cogs.CacherCog(bot, DATA_PATH))
    bot.add_cog(cogs.ConsoleCog(bot))
    bot.add_cog(cogs.HelpCog(bot, BOT_COLOR))
    bot.add_cog(cogs.QueueCog(bot, BOT_COLOR))

    if donate_url:
        bot.add_cog(cogs.DonateCog(bot, BOT_COLOR, donate_url))

    bot.run(discord_token)