import os
from PIL import Image, ImageDraw
import io

def generate_patpat_gif(avatar_img: Image.Image, patpat_gif_path: str = "patpat.gif") -> io.BytesIO:
    if not os.path.exists(patpat_gif_path):
        raise FileNotFoundError(f"Sorry, {patpat_gif_path} file not found!")
    
    patpat_gif = Image.open(patpat_gif_path)
    gif_width, gif_height = patpat_gif.size
    
    avatar_size = (int(gif_width * 0.65), int(gif_width * 0.65))
    avatar_img = avatar_img.resize(avatar_size, Image.Resampling.LANCZOS)
    
    mask = Image.new('L', avatar_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + avatar_size, fill=255)
    
    avatar_img = avatar_img.convert("RGBA")
    avatar_img.putalpha(mask)
    
    total_frames = 0
    try:
        while True:
            patpat_gif.seek(total_frames)
            total_frames += 1
    except EOFError:
        pass
    
    frames = []
    durations = []
    
    try:
        frame_count = 0
        while frame_count < total_frames:
            patpat_gif.seek(frame_count)
            patpat_frame = patpat_gif.convert('RGBA')
            combined_frame = Image.new('RGBA', (gif_width, gif_height), (0, 0, 0, 0))
            
            if total_frames > 1:
                progress = frame_count / (total_frames - 1)
                if progress <= 0.6:
                    squish_factor = progress * 1.67
                else:
                    squish_factor = (1.0 - progress) * 2.5
                
                squish_factor = max(0, min(1, squish_factor))
                squish_height_reduction = squish_factor * 0.3
                squished_height = int(avatar_size[1] * (1 - squish_height_reduction))
                squished_size = (avatar_size[0], squished_height)
                
                squished_avatar = avatar_img.resize(squished_size, Image.Resampling.LANCZOS)
            else:
                squished_avatar = avatar_img
                squished_size = avatar_size
            
            avatar_x = (gif_width - squished_size[0]) // 2
            avatar_y = gif_height - squished_size[1] - 10
            
            combined_frame.paste(squished_avatar, (avatar_x, avatar_y), squished_avatar)
            combined_frame.paste(patpat_frame, (0, 0), patpat_frame)
            
            frames.append(combined_frame)
            
            try:
                duration = patpat_gif.info['duration']
            except KeyError:
                duration = 100
            durations.append(duration)
            
            frame_count += 1
            
    except EOFError:
        pass
    
    output = io.BytesIO()
    frames[0].save(
        output,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2
    )
    output.seek(0)
    return output
