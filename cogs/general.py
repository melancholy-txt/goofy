import discord
from discord import app_commands
from discord.ext import commands

class GeneralCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Get a member's profile picture")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def avatar(
        self,
        interaction: discord.Interaction,
        member: discord.User | discord.Member | None = None,
    ):
        member = member or interaction.user
        
        embed_color = member.color if isinstance(member, discord.Member) else discord.Color.blue()
        embed = discord.Embed(
            title=f"{member.display_name}'s Avatar",
            color=embed_color
        )
        
        avatar_url = member.display_avatar.url
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Open Full Size",
            url=avatar_url,
            style=discord.ButtonStyle.link
        ))
        
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralCog(bot))
