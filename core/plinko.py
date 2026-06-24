import pymunk
import random
import math
from PIL import Image, ImageDraw, ImageFont
import io

def generate_plinko_gif(avatar_img: Image.Image, display_name: str) -> io.BytesIO:
    ball_radius = 20
    img_size = (ball_radius * 2, ball_radius * 2)
    avatar_img = avatar_img.resize(img_size, Image.Resampling.LANCZOS)
    
    mask = Image.new('L', img_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img_size, fill=255)
    avatar_img.putalpha(mask)

    space = pymunk.Space()
    space.gravity = (0, 900)

    font = ImageFont.load_default()
    display_name = display_name.lower()
    
    width = 400
    peg_offset_adjustment = 0
    
    if len(display_name) > 12:
        lines = [display_name, "plinko"]
        height = 510
        peg_offset_adjustment = 20
    else:
        lines = [f"{display_name} plinko"]
        height = 460

    pegs = []
    spacing = 70
    peg_radius = 14
    
    row_counts = [5, 4, 5, 4, 5]
    
    for row, count in enumerate(row_counts):
        total_row_width = (count - 1) * spacing
        start_x = (width / 2) - (total_row_width / 2)
        
        for col in range(count):
            x = start_x + (col * spacing)
            y = row * spacing + 150 + peg_offset_adjustment
            
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (x, y)
            shape = pymunk.Circle(body, peg_radius)
            shape.elasticity = 0.6
            space.add(body, shape)
            pegs.append((x, y))

    mass = 1
    inertia = pymunk.moment_for_circle(mass, 0, ball_radius, (0, 0))
    ball_body = pymunk.Body(mass, inertia)
    
    start_x = (width // 2) + random.uniform(-20, 20)
    ball_body.position = (start_x, 30 + peg_offset_adjustment) 
    
    ball_shape = pymunk.Circle(ball_body, ball_radius)
    ball_shape.elasticity = 0.8
    ball_shape.friction = 0.5
    space.add(ball_body, ball_shape)

    bg_frame = Image.new('RGBA', (width, height), (49, 51, 56, 255))
    bg_draw = ImageDraw.Draw(bg_frame)
    
    for px, py in pegs:
        bg_draw.ellipse(
            [px - peg_radius, py - peg_radius, px + peg_radius, py + peg_radius], 
            fill=(180, 185, 190, 255)
        )

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
        tiny_h = sum(line_heights) + (len(lines) - 1) * 2
    except AttributeError:
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
        try:
            line_bbox = text_draw.textbbox((0, 0), line, font=font)
            line_w = line_bbox[2] - line_bbox[0]
        except AttributeError:
            line_w, _ = text_draw.textsize(line, font=font)
        x_offset = (tiny_w + 4 - line_w) // 2
        
        for adj_x in [-1, 0, 1]:
            for adj_y in [-1, 0, 1]:
                text_draw.text((x_offset + adj_x, y_offset + adj_y), line, font=font, fill=outline_color)
        text_draw.text((x_offset, y_offset), line, font=font, fill=(255, 0, 0, 255))
        y_offset += line_heights[i] + 2
    
    scale_multiplier = 4
    big_text_w = (tiny_w + 4) * scale_multiplier
    big_text_h = (tiny_h + 4) * scale_multiplier
    
    massive_retro_text = text_canvas.resize(
        (big_text_w, big_text_h), 
        resample=Image.Resampling.NEAREST
    )
    
    text_paste_x = (width - big_text_w) // 2
    text_paste_y = 25 

    frames = []
    fps = 30
    dt = 1.0 / fps
    total_frames = 180  
    
    for _ in range(total_frames):
        space.step(dt)
        frame = bg_frame.copy()

        frame.paste(massive_retro_text, (text_paste_x, text_paste_y), mask=massive_retro_text)
        
        bx, by = int(ball_body.position.x), int(ball_body.position.y)
        paste_x = bx - ball_radius
        paste_y = by - ball_radius
        
        if -50 < paste_y < height + 50: 
            angle_deg = math.degrees(-ball_body.angle)
            rotated_avatar = avatar_img.rotate(angle_deg, resample=Image.Resampling.BICUBIC)
            frame.paste(rotated_avatar, (paste_x, paste_y), mask=rotated_avatar)
            
        frames.append(frame)

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
    return output
