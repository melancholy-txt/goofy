import discord
from discord import app_commands
from discord.ext import commands
import io
import requests
from PIL import Image

from core.patpat import generate_patpat_gif
from core.plinko import generate_plinko_gif
from core.pinball import generate_pinball_gif

class GamesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="patpat", description="Pat someone's avatar!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def patpat(self, interaction: discord.Interaction, member: discord.User | discord.Member | None = None):
        member = member or interaction.user
        await interaction.response.defer()
        
        try:
            avatar_url = member.display_avatar.with_size(256).url
            response = requests.get(avatar_url)
            avatar_img = Image.open(io.BytesIO(response.content))
            
            output = generate_patpat_gif(avatar_img)
            
            file = discord.File(output, filename="patpat.gif")
            await interaction.followup.send(file=file)
        except FileNotFoundError as e:
            await interaction.followup.send(str(e))
        except Exception as e:
            await interaction.followup.send(f"Sorry, couldn't create patpat image: {str(e)}")

    @app_commands.command(name="plinko", description="Drop someone's avatar down a Plinko board!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def plinko(self, interaction: discord.Interaction, member: discord.User | discord.Member | None = None):
        member = member or interaction.user
        await interaction.response.defer()
        
        try:
            avatar_url = member.display_avatar.with_size(128).url
            response = requests.get(avatar_url)
            avatar_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
            
            output = generate_plinko_gif(avatar_img, member.display_name)
            
            file = discord.File(output, filename="plinko.gif")
            await interaction.followup.send(file=file)
        except Exception as e:
            await interaction.followup.send(f"Sorry, couldn't create the Plinko simulation: {str(e)}")

    @app_commands.command(name="pinball", description="Play pinball with someone's avatar!")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def pinball(self, interaction: discord.Interaction, member: discord.User | discord.Member | None = None):
        member = member or interaction.user
        await interaction.response.defer()
        
        try:
            avatar_url = member.display_avatar.with_size(128).url
            response = requests.get(avatar_url)
            avatar_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
            
            output, score = generate_pinball_gif(avatar_img, member.display_name)
            
            file = discord.File(output, filename="pinball.gif")
            await interaction.followup.send(f"🎯 Final Score: **{score}** points!", file=file)
        except Exception as e:
            await interaction.followup.send(f"Sorry, couldn't create the pinball simulation: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(GamesCog(bot))
