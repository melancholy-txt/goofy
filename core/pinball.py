import pymunk
import random
import math
from PIL import Image, ImageDraw, ImageFont
import io

def generate_pinball_gif(avatar_img: Image.Image, display_name: str) -> tuple[io.BytesIO, int]:
    ball_radius = 15
    img_size = (ball_radius * 2, ball_radius * 2)
    avatar_img = avatar_img.resize(img_size, Image.Resampling.LANCZOS)
    
    mask = Image.new('L', img_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img_size, fill=255)
    avatar_img.putalpha(mask)

    space = pymunk.Space()
    space.gravity = (0, 1200)
    
    width = 400
    height = 600
    
    mass = 1
    inertia = pymunk.moment_for_circle(mass, 0, ball_radius, (0, 0))
    ball_body = pymunk.Body(mass, inertia)
    random_x = random.randint(80, width - 80)
    ball_body.position = (random_x, 50)
    ball_body.velocity = (random.uniform(-100, 100), random.uniform(-300, -100))
    
    ball_shape = pymunk.Circle(ball_body, ball_radius)
    ball_shape.elasticity = 0.7
    ball_shape.friction = 0.3
    space.add(ball_body, ball_shape)
    
    wall_thickness = 10
    walls = []
    
    left_wall = pymunk.Segment(space.static_body, (wall_thickness, 0), (wall_thickness, height), wall_thickness)
    left_wall.elasticity = 0.8
    walls.append(left_wall)
    
    right_wall = pymunk.Segment(space.static_body, (width - wall_thickness, 0), (width - wall_thickness, height), wall_thickness)
    right_wall.elasticity = 0.8
    walls.append(right_wall)
    
    top_wall = pymunk.Segment(space.static_body, (0, wall_thickness), (width, wall_thickness), wall_thickness)
    top_wall.elasticity = 0.8
    walls.append(top_wall)
    
    left_guide = pymunk.Segment(space.static_body, (wall_thickness, 80), (80, 150), 5)
    left_guide.elasticity = 0.9
    walls.append(left_guide)
    
    right_guide = pymunk.Segment(space.static_body, (width - wall_thickness, 80), (width - 80, 150), 5)
    right_guide.elasticity = 0.9
    walls.append(right_guide)
    
    space.add(*walls)
    
    bumpers = []
    bumper_radius = 25
    base_positions = [
        (120, 220),
        (280, 220),
        (200, 300),
        (120, 380),
        (280, 380),
    ]
    bumper_positions = [
        (x + random.randint(-20, 20), y + random.randint(-15, 15))
        for x, y in base_positions
    ]
    
    bumper_hit_frames = {}
    score = 0
    
    for i, (bx, by) in enumerate(bumper_positions):
        bumper_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        bumper_body.position = (bx, by)
        bumper_shape = pymunk.Circle(bumper_body, bumper_radius)
        bumper_shape.elasticity = random.uniform(1.3, 1.7)
        space.add(bumper_body, bumper_shape)
        bumpers.append((bx, by, i))
        bumper_hit_frames[i] = -999
    
    flipper_width = 90
    flipper_height = 8
    flipper_y = height - 80
    
    left_flipper_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    left_flipper_pivot = (50, flipper_y)
    left_flipper_body.position = left_flipper_pivot
    left_flipper_shape = pymunk.Segment(left_flipper_body, (0, 0), (flipper_width, 0), flipper_height)
    left_flipper_shape.elasticity = 0.95
    space.add(left_flipper_body, left_flipper_shape)
    
    right_flipper_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    right_flipper_pivot = (350, flipper_y)
    right_flipper_body.position = right_flipper_pivot
    right_flipper_shape = pymunk.Segment(right_flipper_body, (0, 0), (-flipper_width, 0), flipper_height)
    right_flipper_shape.elasticity = 0.95
    space.add(right_flipper_body, right_flipper_shape)
    
    flipper_state = "down"
    flipper_cooldown = 0
    
    font = ImageFont.load_default()
    
    frames = []
    fps = 30
    dt = 1.0 / fps
    total_frames = 180
    
    for frame_counter in range(total_frames):
        ball_pos = ball_body.position
        for bx, by, idx in bumpers:
            distance = math.sqrt((ball_pos.x - bx)**2 + (ball_pos.y - by)**2)
            collision_threshold = ball_radius + bumper_radius
            
            if distance < collision_threshold and frame_counter - bumper_hit_frames[idx] > 5:
                bumper_hit_frames[idx] = frame_counter
                score += 100
                
                dx = ball_pos.x - bx
                dy = ball_pos.y - by
                distance_safe = max(distance, 0.1)
                impulse_x = (dx / distance_safe) * 400
                impulse_y = (dy / distance_safe) * 400
                ball_body.apply_impulse_at_world_point((impulse_x, impulse_y), ball_body.position)
        
        if flipper_cooldown <= 0:
            ball_y = ball_body.position.y
            if ball_y > flipper_y - 100 and ball_body.velocity.y > 0:
                flipper_state = "up"
                flipper_cooldown = 20
                
        if flipper_cooldown > 0:
            flipper_cooldown -= 1
            if flipper_cooldown == 0:
                flipper_state = "down"
        
        if flipper_state == "up":
            left_flipper_body.angle = math.radians(45)
            right_flipper_body.angle = math.radians(-45)
        else:
            left_flipper_body.angle = 0
            right_flipper_body.angle = 0
        
        space.step(dt)
        
        frame = Image.new('RGBA', (width, height), (35, 39, 42, 255))
        frame_draw = ImageDraw.Draw(frame)
        
        frame_draw.rectangle([0, 0, wall_thickness * 2, height], fill=(100, 100, 100, 255))
        frame_draw.rectangle([width - wall_thickness * 2, 0, width, height], fill=(100, 100, 100, 255))
        frame_draw.rectangle([0, 0, width, wall_thickness * 2], fill=(100, 100, 100, 255))
        
        frame_draw.line([(wall_thickness, 80), (80, 150)], fill=(120, 120, 120, 255), width=8)
        frame_draw.line([(width - wall_thickness, 80), (width - 80, 150)], fill=(120, 120, 120, 255), width=8)
        
        for bx, by, idx in bumpers:
            frames_since_hit = frame_counter - bumper_hit_frames[idx]
            if frames_since_hit < 5:
                color = (255, 255, 0, 255)
            else:
                color = (255, 100, 100, 255)
            frame_draw.ellipse(
                [bx - bumper_radius, by - bumper_radius, bx + bumper_radius, by + bumper_radius],
                fill=color
            )
        
        def draw_flipper(body, pivot, length, is_left):
            angle = body.angle
            end_x = pivot[0] + length * math.cos(angle) * (1 if is_left else -1)
            end_y = pivot[1] + length * math.sin(angle) * (1 if is_left else -1)
            frame_draw.line([pivot, (end_x, end_y)], fill=(100, 150, 255, 255), width=flipper_height * 2)
            
        draw_flipper(left_flipper_body, left_flipper_pivot, flipper_width, True)
        draw_flipper(right_flipper_body, right_flipper_pivot, flipper_width, False)
        
        bx, by = int(ball_body.position.x), int(ball_body.position.y)
        paste_x = bx - ball_radius
        paste_y = by - ball_radius
        
        if 0 < paste_y < height:
            angle_deg = math.degrees(-ball_body.angle)
            rotated_avatar = avatar_img.rotate(angle_deg, resample=Image.Resampling.BICUBIC)
            frame.paste(rotated_avatar, (paste_x, paste_y), mask=rotated_avatar)
        
        score_text = f"SCORE: {score}"
        name_text = display_name.upper()
        
        try:
            name_bbox = frame_draw.textbbox((0, 0), name_text, font=font)
            score_bbox = frame_draw.textbbox((0, 0), score_text, font=font)
            text_w = max(name_bbox[2] - name_bbox[0], score_bbox[2] - score_bbox[0])
            text_h = (name_bbox[3] - name_bbox[1]) + (score_bbox[3] - score_bbox[1]) + 12
        except AttributeError:
            name_w, name_h = frame_draw.textsize(name_text, font=font)
            score_w, score_h = frame_draw.textsize(score_text, font=font)
            text_w = max(name_w, score_w)
            text_h = name_h + score_h + 2
        
        text_canvas = Image.new('RGBA', (text_w + 4, text_h + 4), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_canvas)
        
        name_height = name_bbox[3] - name_bbox[1] if hasattr(frame_draw, 'textbbox') else name_h
        score_y = name_height + 8
        for adj_x in [-1, 0, 1]:
            for adj_y in [-1, 0, 1]:
                text_draw.text((2 + adj_x, 2 + adj_y), name_text, font=font, fill=(0, 0, 0, 255))
                text_draw.text((2 + adj_x, score_y + 2 + adj_y), score_text, font=font, fill=(0, 0, 0, 255))
        
        text_draw.text((2, 2), name_text, font=font, fill=(255, 215, 0, 255))
        text_draw.text((2, score_y + 2), score_text, font=font, fill=(255, 255, 255, 255))
        
        big_text = text_canvas.resize((text_w * 3, text_h * 3), resample=Image.Resampling.NEAREST)
        text_x = (width - text_w * 3) // 2
        frame.paste(big_text, (text_x, 10), mask=big_text)
        
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
    return output, score
