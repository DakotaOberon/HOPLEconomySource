from discord import Interaction, app_commands
from discord.ext import commands


class MyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='ping', description='Example command to that replies with pong.')
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message(f'Pong {interaction.user.display_name}.')

async def setup(bot: commands.Bot):
    await bot.add_cog(MyCog(bot))
