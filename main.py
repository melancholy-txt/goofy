import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests
from PIL import Image, ImageDraw
import io

# Load environment variables from .env file
load_dotenv()

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Prevents warning, even though we only use slash commands

# Use an unusual prefix since we only use slash commands
bot = commands.Bot(command_prefix="$#!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        # Sync slash commands with Discord
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

# Get a member's profile picture
@bot.tree.command(name="avatar", description="Get a member's profile picture")
async def avatar(interaction: discord.Interaction, member: discord.Member):
    # Create an embed to make it look nice
    embed = discord.Embed(
        title=f"{member.display_name}'s Avatar",
        color=member.color or discord.Color.blue()
    )
    
    # Get the avatar URL (falls back to default if no custom avatar)
    avatar_url = member.display_avatar.url
    
    embed.set_image(url=avatar_url)
    embed.set_footer(text=f"Requested by {interaction.user.display_name}")
    
    # Add a link to open the full-size image
    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        label="Open Full Size",
        url=avatar_url,
        style=discord.ButtonStyle.link
    ))
    
    await interaction.response.send_message(embed=embed, view=view)

# Patpat command - overlays patting animation on avatar
@bot.tree.command(name="patpat", description="Pat someone's avatar!")
async def patpat(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()  # Give us more time for image processing
    
    try:
        # Check if patpat.gif exists
        if not os.path.exists("patpat.gif"):
            await interaction.followup.send("Sorry, patpat.gif file not found!")
            return
        
        # Download the user's avatar
        avatar_url = member.display_avatar.with_size(256).url
        response = requests.get(avatar_url)
        avatar_img = Image.open(io.BytesIO(response.content))
        
        # Open the patpat gif
        patpat_gif = Image.open("patpat.gif")
        
        # Get dimensions from the patpat gif
        gif_width, gif_height = patpat_gif.size
        
        # Resize avatar to be bigger (about 2/3 of gif width)
        avatar_size = (int(gif_width * 0.65), int(gif_width * 0.65))  # Make avatar bigger
        avatar_img = avatar_img.resize(avatar_size, Image.Resampling.LANCZOS)
        
        # Create circular mask for avatar
        mask = Image.new('L', avatar_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + avatar_size, fill=255)
        
        # Apply circular mask to avatar
        avatar_img = avatar_img.convert("RGBA")
        avatar_img.putalpha(mask)
        
        # Process each frame of the GIF
        frames = []
        durations = []
        
        try:
            frame_count = 0
            while True:
                patpat_gif.seek(frame_count)
                
                # Get current frame and convert to RGBA
                patpat_frame = patpat_gif.convert('RGBA')
                
                # Create a completely new image for each frame (this ensures clean slate)
                combined_frame = Image.new('RGBA', (gif_width, gif_height), (0, 0, 0, 0))
                
                # Position avatar in the bottom center area (BASE LAYER)
                avatar_x = (gif_width - avatar_size[0]) // 2
                avatar_y = gif_height - avatar_size[1] - 10  # Bottom center with 10px margin
                
                # Paste the avatar first (base layer)
                combined_frame.paste(avatar_img, (avatar_x, avatar_y), avatar_img)
                
                # Paste ONLY the current patpat frame on top (TOP LAYER)
                # This ensures only the current frame is visible, not accumulated frames
                combined_frame.paste(patpat_frame, (0, 0), patpat_frame)
                
                # Keep as RGBA to preserve transparency
                frames.append(combined_frame)
                
                # Get frame duration
                try:
                    duration = patpat_gif.info['duration']
                except KeyError:
                    duration = 100  # Default 100ms
                durations.append(duration)
                
                frame_count += 1
                
        except EOFError:
            pass  # End of frames
        
        # Save as animated GIF with proper disposal
        output = io.BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            disposal=2  # Clear frame before next one
        )
        output.seek(0)
        
        # Send just the GIF file without embed
        file = discord.File(output, filename="patpat.gif")
        await interaction.followup.send(file=file)
        
    except Exception as e:
        await interaction.followup.send(f"Sorry, couldn't create patpat image: {str(e)}")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set!")
        print("Please set your Discord bot token as an environment variable.")
        exit(1)
    bot.run(token)
