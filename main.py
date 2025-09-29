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
        
        # First, count total frames in the GIF
        total_frames = 0
        try:
            while True:
                patpat_gif.seek(total_frames)
                total_frames += 1
        except EOFError:
            pass
        
        # Process each frame of the GIF with squishing animation
        frames = []
        durations = []
        
        try:
            frame_count = 0
            while frame_count < total_frames:
                patpat_gif.seek(frame_count)
                
                # Get current frame and convert to RGBA
                patpat_frame = patpat_gif.convert('RGBA')
                
                # Create a completely new image for each frame (this ensures clean slate)
                combined_frame = Image.new('RGBA', (gif_width, gif_height), (0, 0, 0, 0))
                
                # Calculate squish factor based on frame position
                # Peak squish at frame 3 out of 5 (60% through animation)
                if total_frames > 1:
                    progress = frame_count / (total_frames - 1)  # 0 to 1
                    
                    # Create squish curve: builds to peak at 60%, then returns to normal
                    if progress <= 0.6:  # First part - increasing squish
                        squish_factor = progress * 1.67  # 0 to 1 (at 60% progress)
                    else:  # Second part - decreasing squish  
                        squish_factor = (1.0 - progress) * 2.5  # 1 to 0 (from 60% to 100%)
                    
                    # Limit squish factor between 0 and 1
                    squish_factor = max(0, min(1, squish_factor))
                    
                    # Apply squish: reduce height, keep width
                    squish_height_reduction = squish_factor * 0.3  # Max 30% height reduction
                    squished_height = int(avatar_size[1] * (1 - squish_height_reduction))
                    squished_size = (avatar_size[0], squished_height)
                    
                    # Create squished avatar
                    squished_avatar = avatar_img.resize(squished_size, Image.Resampling.LANCZOS)
                else:
                    squished_avatar = avatar_img
                    squished_size = avatar_size
                
                # Position squished avatar in the bottom center area (BASE LAYER)
                avatar_x = (gif_width - squished_size[0]) // 2
                avatar_y = gif_height - squished_size[1] - 10  # Bottom center with 10px margin
                
                # Paste the squished avatar first (base layer)
                combined_frame.paste(squished_avatar, (avatar_x, avatar_y), squished_avatar)
                
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
