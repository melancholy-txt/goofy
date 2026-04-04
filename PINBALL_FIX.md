# Pinball Collision Handler Fix

## Problem

The `/pinball` command was failing with error: `'Space' object has no attribute 'add_collision_handler'`

This error occurred because the code was using pymunk's collision handler API which can be problematic across different pymunk versions.

## Solution

Replaced the pymunk collision handler system with **distance-based collision detection**, similar to how the `/plinko` command handles physics interactions.

## Changes Made

### 1. Removed collision_type from bumper shapes (line 482)

**Before:**

```python
bumper_shape.collision_type = i + 1  # Unique collision type per bumper
```

**After:**

```python
# Removed - no longer needed for distance-based detection
```

### 2. Removed collision handler setup (lines 513-529)

**Before:**

```python
# 7. Collision handler for scoring
def bumper_hit_handler(arbiter, space, data):
    nonlocal score
    collision_type = arbiter.shapes[1].collision_type
    if collision_type > 0:
        bumper_idx = collision_type - 1
        bumper_hit_frames[bumper_idx] = frame_counter
        score += 100
        # Apply impulse to ball
        ball_shape = arbiter.shapes[0]
        impulse_direction = (ball_body.position - bumpers[bumper_idx][:2]).normalized()
        ball_body.apply_impulse_at_world_point(impulse_direction * 800, ball_body.position)
    return True

for i in range(len(bumpers)):
    handler = space.add_collision_handler(0, i + 1)
    handler.begin = bumper_hit_handler
```

**After:**

```python
# Removed - replaced with distance-based detection in main loop
```

### 3. Added distance-based collision detection (lines 524-541)

**New code in simulation loop:**

```python
# Check for bumper collisions (distance-based detection)
ball_pos = ball_body.position
for bx, by, idx in bumpers:
    distance = math.sqrt((ball_pos.x - bx)**2 + (ball_pos.y - by)**2)
    collision_threshold = ball_radius + bumper_radius

    # Check if ball is colliding with bumper and hasn't scored recently
    if distance < collision_threshold and frame_counter - bumper_hit_frames[idx] > 5:
        bumper_hit_frames[idx] = frame_counter
        score += 100

        # Apply impulse away from bumper
        dx = ball_pos.x - bx
        dy = ball_pos.y - by
        distance_safe = max(distance, 0.1)  # Avoid division by zero
        impulse_x = (dx / distance_safe) * 800
        impulse_y = (dy / distance_safe) * 800
        ball_body.apply_impulse_at_world_point((impulse_x, impulse_y), ball_body.position)
```

## Benefits

1. **Cross-version compatibility**: Works with any pymunk version
2. **Simpler code**: No complex collision handler callbacks
3. **More control**: Direct distance calculation with debouncing (5 frame cooldown)
4. **Proven approach**: Same pattern used successfully in `/plinko` command
5. **Better impulse calculation**: Manual impulse direction calculation for consistent behavior

## Testing

To test the fix:

1. Run the bot: `uv run main.py` or `docker-compose up`
2. Use `/pinball @username` in Discord
3. The command should generate a GIF with scoring when the ball hits bumpers
4. Bumpers should flash yellow when hit and add 100 points to the score

## Technical Details

- **Collision detection**: Euclidean distance between ball center and bumper center
- **Collision threshold**: Sum of ball radius (15px) and bumper radius (25px) = 40px
- **Debouncing**: 5-frame cooldown prevents duplicate scoring on same bumper
- **Impulse force**: 800 units applied in direction away from bumper center
- **Safety**: Division by zero prevented with `max(distance, 0.1)`
