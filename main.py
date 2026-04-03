import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import pymunk
import random
import math

# Load environment variables from .env file
load_dotenv()

# Set up intents
intents = discord.Intents.default()
intents.message_content = True  # Prevents warning, even though we only use slash commands

# Use an unusual prefix since we only use slash commands
bot = commands.Bot(command_prefix="$#!", intents=intents)

# A standard text command to manually sync slash commands
# We use @commands.is_owner() so only YOU can run this command
@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    await ctx.send("Syncing commands...")
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"Successfully synced {len(synced)} slash command(s) globally!")
    except Exception as e:
        await ctx.send(f"Failed to sync commands: {e}")
# This tells the bot to complain if someone other than the owner uses the command
@sync.error
async def sync_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("Error: You are not recognized as the bot owner!")
    else:
        await ctx.send(f"An error occurred: {error}")

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

@bot.tree.command(name="plinko", description="Drop someone's avatar down a Plinko board!")
async def plinko(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    
    try:
        # 1. Fetch and prepare the avatar
        avatar_url = member.display_avatar.with_size(128).url
        response = requests.get(avatar_url)
        avatar_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        
        ball_radius = 20
        img_size = (ball_radius * 2, ball_radius * 2)
        avatar_img = avatar_img.resize(img_size, Image.Resampling.LANCZOS)
        
        mask = Image.new('L', img_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img_size, fill=255)
        avatar_img.putalpha(mask)

        # 2. Setup the Physics Space
        space = pymunk.Space()
        space.gravity = (0, 900)

        # --- DETERMINE DIMENSIONS BASED ON TEXT ---
        font = ImageFont.load_default()
        display_name = member.display_name.lower()
        
        width = 400
        peg_offset_adjustment = 0
        
        # Split into two rows if name is longer than 12 characters
        if len(display_name) > 12:
            lines = [display_name, "plinko"]
            # Larger dimensions for two-row text
            # width = 480
            height = 510
            peg_offset_adjustment = 20  # Push pegs down by the extra height
        else:
            lines = [f"{display_name} plinko"]
            # Original dimensions for single-row text
            height = 460

        # 3. Create the Plinko Pegs
        pegs = []
        spacing = 70
        peg_radius = 14
        
        row_counts = [5, 4, 5, 4, 5]
        
        for row, count in enumerate(row_counts):
            total_row_width = (count - 1) * spacing
            start_x = (width / 2) - (total_row_width / 2)
            
            for col in range(count):
                x = start_x + (col * spacing)
                # Shifted all pegs down by 50 pixels to leave room for text
                y = row * spacing + 150 + peg_offset_adjustment
                
                body = pymunk.Body(body_type=pymunk.Body.STATIC)
                body.position = (x, y)
                shape = pymunk.Circle(body, peg_radius)
                shape.elasticity = 0.6
                space.add(body, shape)
                pegs.append((x, y))

        # 4. Create the Falling Avatar
        mass = 1
        inertia = pymunk.moment_for_circle(mass, 0, ball_radius, (0, 0))
        ball_body = pymunk.Body(mass, inertia)
        
        start_x = (width // 2) + random.uniform(-20, 20)
        # Shifted the ball's start position down by 50 pixels
        ball_body.position = (start_x, 30 + peg_offset_adjustment) 
        
        ball_shape = pymunk.Circle(ball_body, ball_radius)
        ball_shape.elasticity = 0.8
        ball_shape.friction = 0.5
        space.add(ball_body, ball_shape)

        # 5. Setup the Background
        bg_frame = Image.new('RGBA', (width, height), (49, 51, 56, 255))
        bg_draw = ImageDraw.Draw(bg_frame)
        
        for px, py in pegs:
            bg_draw.ellipse(
                [px - peg_radius, py - peg_radius, px + peg_radius, py + peg_radius], 
                fill=(180, 185, 190, 255)
            )

        # --- THE RETRO UPSCALE TEXT TRICK ---
        
        # Calculate bounding box for all lines
        line_heights = []
        try:
            max_width = 0
            for line in lines:
                bbox = bg_draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_height = bbox[3] - bbox[1]
                line_heights.append(line_height)
                max_width = max(max_width, line_width)
            tiny_w = max_width
            tiny_h = sum(line_heights) + (len(lines) - 1) * 2  # 2px spacing between lines
        except AttributeError:
            # Fallback for older PIL versions
            max_width = 0
            for line in lines:
                line_w, line_h = bg_draw.textsize(line, font=font)
                line_heights.append(line_h)
                max_width = max(max_width, line_w)
            tiny_w = max_width
            tiny_h = sum(line_heights) + (len(lines) - 1) * 2
            
        text_canvas = Image.new('RGBA', (tiny_w + 4, tiny_h + 6), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_canvas)
        
        outline_color = (0, 0, 0, 255)
        y_offset = 2
        for i, line in enumerate(lines):
            # Center each line horizontally within the canvas
            try:
                line_bbox = text_draw.textbbox((0, 0), line, font=font)
                line_w = line_bbox[2] - line_bbox[0]
            except AttributeError:
                line_w, _ = text_draw.textsize(line, font=font)
            x_offset = (tiny_w + 4 - line_w) // 2
            
            for adj_x in [-1, 0, 1]:
                for adj_y in [-1, 0, 1]:
                    text_draw.text((x_offset + adj_x, y_offset + adj_y), line, font=font, fill=outline_color)
            # Pure Red Text
            text_draw.text((x_offset, y_offset), line, font=font, fill=(255, 0, 0, 255))
            y_offset += line_heights[i] + 2  # Add line height + spacing
        
        scale_multiplier = 4
        big_text_w = (tiny_w + 4) * scale_multiplier
        big_text_h = (tiny_h + 4) * scale_multiplier
        
        massive_retro_text = text_canvas.resize(
            (big_text_w, big_text_h), 
            resample=Image.Resampling.NEAREST
        )
        
        text_paste_x = (width - big_text_w) // 2
        text_paste_y = 25 

        # 6. Run the Simulation and Record Frames
        frames = []
        fps = 30
        dt = 1.0 / fps
        total_frames = 180  
        
        for _ in range(total_frames):
            space.step(dt)
            frame = bg_frame.copy()

            # --- LAYER ONE: The Text ---
            frame.paste(massive_retro_text, (text_paste_x, text_paste_y), mask=massive_retro_text)
            
            # --- LAYER TWO: The Avatar Ball ---
            bx, by = int(ball_body.position.x), int(ball_body.position.y)
            paste_x = bx - ball_radius
            paste_y = by - ball_radius
            
            if -50 < paste_y < height + 50: 
                angle_deg = math.degrees(-ball_body.angle)
                rotated_avatar = avatar_img.rotate(angle_deg, resample=Image.Resampling.BICUBIC)
                frame.paste(rotated_avatar, (paste_x, paste_y), mask=rotated_avatar)
                
            frames.append(frame)

        # 7. Save and Send the GIF
        output = io.BytesIO()
        frames[0].save(
            output,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=int(1000/fps),
            loop=0,
            disposal=2
        )
        output.seek(0)
        
        file = discord.File(output, filename="plinko.gif")
        await interaction.followup.send(file=file)
        
    except Exception as e:
        await interaction.followup.send(f"Sorry, couldn't create the Plinko simulation: {str(e)}")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set!")
        print("Please set your Discord bot token as an environment variable.")
        exit(1)
    bot.run(token)
