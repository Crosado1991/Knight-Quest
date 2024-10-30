import pgzrun
import random

GRID_WIDTH = 20  # Width of the grid
GRID_HEIGHT = 15  # Height of the grid
GRID_SIZE = 50  # Size of each grid cell
GUARD_MOVE_INTERVAL = 0.5  # Time interval for guard movement
PLAYER_MOVE_INTERVAL = 0.25  # Time interval for player movement
BACKGROUND_SEED = 123456  # Seed for random background generation

WIDTH = GRID_WIDTH * GRID_SIZE  # Width of the game window
HEIGHT = GRID_HEIGHT * GRID_SIZE  # Height of the game window

# Initialize an empty map with spaces
MAP = [
    " " * GRID_WIDTH
    for _ in range(GRID_HEIGHT)
]


def screen_coords(x, y):
    # Convert grid coordinates to screen coordinates
    return (x * GRID_SIZE, y * GRID_SIZE)


def grid_coords(actor):
    # Convert actor's screen coordinates to grid coordinates
    return (round(actor.x / GRID_SIZE), round(actor.y / GRID_SIZE))


def setup_game():
    global game_over, player_won, player, keys_to_collect, guards
    game_over = False  # Initialize game over state
    player_won = False  # Initialize player won state
    player = Actor("player", anchor=("left", "top"))  # Create player actor
    keys_to_collect = []  # List to store key actors
    guards = []  # List to store guard actors

    # Generate random walls
    random.seed(BACKGROUND_SEED)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if random.random() < 0.2:  # 20% chance to be a wall
                MAP[y] = MAP[y][:x] + "W" + MAP[y][x + 1:]

    # Ensure the borders are walls
    for y in range(GRID_HEIGHT):
        MAP[y] = "W" + MAP[y][1:-1] + "W"
    MAP[0] = "W" * GRID_WIDTH
    MAP[-1] = "W" * GRID_WIDTH

    # Place player, keys, and guards randomly
    place_randomly(player, 'P')
    for _ in range(3):  # Number of keys
        key = Actor("key", anchor=("left", "top"))
        place_randomly(key, 'K')
        keys_to_collect.append(key)
    for _ in range(2):  # Number of guards
        guard = Actor("guard", anchor=("left", "top"))
        place_randomly(guard, 'G')
        guards.append(guard)

    # Ensure the exit door is placed in an empty spot
    place_door()


def place_randomly(actor, type):
    # Place actor randomly in a non-wall space
    while True:
        x = random.randint(1, GRID_WIDTH - 2)
        y = random.randint(1, GRID_HEIGHT - 2)
        if MAP[y][x] == ' ':
            actor.pos = screen_coords(x, y)
            if type == 'P':
                MAP[y] = MAP[y][:x] + 'P' + MAP[y][x + 1:]
            elif type == 'K':
                MAP[y] = MAP[y][:x] + 'K' + MAP[y][x + 1:]
            elif type == 'G':
                MAP[y] = MAP[y][:x] + 'G' + MAP[y][x + 1:]
            break


def place_door():
    # Place door randomly in a non-wall space
    while True:
        x = random.randint(1, GRID_WIDTH - 2)
        y = random.randint(1, GRID_HEIGHT - 2)
        if MAP[y][x] == ' ':
            MAP[y] = MAP[y][:x] + 'D' + MAP[y][x + 1:]
            break


def draw_background():
    # Draw the background with random cracks
    screen.fill((0, 0, 0))
    random.seed(BACKGROUND_SEED)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if x % 2 == y % 2:
                screen.blit("floor1", screen_coords(x, y))
            else:
                screen.blit("floor2", screen_coords(x, y))

            n = random.randint(0, 99)
            if n < 5:
                screen.blit("crack1", screen_coords(x, y))
            elif n < 10:
                screen.blit("crack2", screen_coords(x, y))


def draw_scenery():
    # Draw the walls and door
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            square = MAP[y][x]
            if square == "W":
                screen.blit("wall", screen_coords(x, y))
            elif square == "D" and len(keys_to_collect) > 0:
                screen.blit("door", screen_coords(x, y))


def draw_actors():
    # Draw the player, keys, and guards
    player.draw()
    for key in keys_to_collect:
        key.draw()
    for guard in guards:
        guard.draw()


def draw_game_over():
    # Draw game over screen
    screen_middle = (WIDTH / 2, HEIGHT / 2)
    screen.draw.text("GAME OVER", midbottom=screen_middle, fontsize=GRID_SIZE, color="cyan", owidth=1)

    if player_won:
        screen.draw.text("You won!", midtop=screen_middle, fontsize=GRID_SIZE, color="green", owidth=1)
    else:
        screen.draw.text("You lost!", midtop=screen_middle, fontsize=GRID_SIZE, color="red", owidth=1)

    screen.draw.text("Press SPACE to play again", midtop=(WIDTH / 2, HEIGHT / 2 + GRID_SIZE), fontsize=GRID_SIZE / 2,
                     color="cyan", owidth=1)


def draw():
    # Draw everything
    draw_background()
    draw_scenery()
    draw_actors()
    if game_over:
        draw_game_over()


def on_key_up(key):
    # Restart game on space key up
    if key == keys.SPACE and game_over:
        setup_game()


def on_key_down(key):
    # Move player based on arrow keys
    if key == keys.LEFT:
        move_player(-1, 0)
    elif key == keys.UP:
        move_player(0, -1)
    elif key == keys.RIGHT:
        move_player(1, 0)
    elif key == keys.DOWN:
        move_player(0, 1)


def move_player(dx, dy):
    # Move the player and handle game logic
    global game_over, player_won
    if game_over:
        return
    (x, y) = grid_coords(player)
    x += dx
    y += dy
    square = MAP[y][x]
    if square == "W":
        return
    elif square == "D":
        if len(keys_to_collect) > 0:
            return
        else:
            game_over = True
            player_won = True
    for key in keys_to_collect:
        (key_x, key_y) = grid_coords(key)
        if x == key_x and y == key_y:
            keys_to_collect.remove(key)
            break
    animate(player, pos=screen_coords(x, y), duration=PLAYER_MOVE_INTERVAL, on_finished=repeat_player_move)


def repeat_player_move():
    # Repeat player movement for continuous input
    if keyboard.left:
        move_player(-1, 0)
    elif keyboard.up:
        move_player(0, -1)
    elif keyboard.right:
        move_player(1, 0)
    elif keyboard.down:
        move_player(0, 1)


def move_guard(guard):
    # Move guards towards the player
    global game_over, player_won
    if game_over:
        return
    (player_x, player_y) = grid_coords(player)
    (guard_x, guard_y) = grid_coords(guard)
    if player_x > guard_x and MAP[guard_y][guard_x + 1] != "W":
        guard_x += 1
    elif player_x < guard_x and MAP[guard_y][guard_x - 1] != "W":
        guard_x -= 1
    elif player_y > guard_y and MAP[guard_y + 1][guard_x] != "W":
        guard_y += 1
    elif player_y < guard_y and MAP[guard_y - 1][guard_x] != "W":
        guard_y -= 1
    animate(guard, pos=screen_coords(guard_x, guard_y), duration=GUARD_MOVE_INTERVAL)
    if guard_x == player_x and guard_y == player_y:
        game_over = True
        player_won = False


def move_guards():
    # Move all guards
    if not game_over:
        for guard in guards:
            move_guard(guard)


setup_game()
clock.schedule_interval(move_guards, GUARD_MOVE_INTERVAL)
pgzrun.go()
