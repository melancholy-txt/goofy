import discord
from discord import app_commands
from discord.ext import commands
class ReactionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.base_url = "https://avisnak.eu"

    async def _send_resized(self, interaction: discord.Interaction, image_name: str, size: int):
        # image_name is either 'cutie' or 'waow'
        prefix = image_name[0].lower() # 'c' or 'w'
        url = f"{self.base_url}/{prefix}{size}.webp"
        
        try:
            await interaction.response.send_message(url)
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Error: {e}", ephemeral=True)
            else:
                await interaction.followup.send(f"Error: {e}", ephemeral=True)

    # CUTIE COMMANDS (c)
    
    @app_commands.command(name="c16", description="Post cutie at 16x16")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def c16(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "cutie", 16)
        
    @app_commands.command(name="cs", description="Post cutie at 16x16 (Small)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def cs(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "cutie", 16)

    @app_commands.command(name="c24", description="Post cutie at 24x24")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def c24(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "cutie", 24)
        
    @app_commands.command(name="cm", description="Post cutie at 24x24 (Medium)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def cm(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "cutie", 24)

    @app_commands.command(name="c64", description="Post cutie at 64x64")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def c64(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "cutie", 64)
        
    @app_commands.command(name="cl", description="Post cutie at 64x64 (Large)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def cl(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "cutie", 64)

    @app_commands.command(name="c128", description="Post cutie at 128x128")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def c128(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "cutie", 128)
        
    @app_commands.command(name="cxl", description="Post cutie at 128x128 (Extra Large)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def cxl(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "cutie", 128)

    # WAOW COMMANDS (w)
    
    @app_commands.command(name="w16", description="Post waow at 16x16")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def w16(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "waow", 16)
        
    @app_commands.command(name="ws", description="Post waow at 16x16 (Small)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def ws(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "waow", 16)

    @app_commands.command(name="w24", description="Post waow at 24x24")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def w24(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "waow", 24)
        
    @app_commands.command(name="wm", description="Post waow at 24x24 (Medium)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def wm(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "waow", 24)

    @app_commands.command(name="w64", description="Post waow at 64x64")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def w64(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "waow", 64)
        
    @app_commands.command(name="wl", description="Post waow at 64x64 (Large)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def wl(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "waow", 64)

    @app_commands.command(name="w128", description="Post waow at 128x128")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def w128(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "waow", 128)
        
    @app_commands.command(name="wxl", description="Post waow at 128x128 (Extra Large)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def wxl(self, interaction: discord.Interaction):
        await self._send_resized(interaction, "waow", 128)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionsCog(bot))
