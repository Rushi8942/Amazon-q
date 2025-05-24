import pygame
import sys
import os
import random
import math
import time
from pygame import gfxdraw

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
BOARD_SIZE = 600
BOARD_GRID = 10  # 10x10 grid
TILE_SIZE = BOARD_SIZE // BOARD_GRID
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 100, 255)
GREEN = (50, 200, 50)
YELLOW = (255, 255, 100)
PURPLE = (150, 50, 250)
ORANGE = (255, 165, 0)
TEAL = (0, 175, 175)
PINK = (255, 105, 180)

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

# Create assets directory if it doesn't exist
os.makedirs("assets/images", exist_ok=True)
os.makedirs("assets/sounds", exist_ok=True)
os.makedirs("assets/fonts", exist_ok=True)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake and Ladder - Modern Edition")
clock = pygame.time.Clock()

# Load fonts
try:
    title_font = pygame.font.Font("assets/fonts/Roboto-Bold.ttf", 48)
    button_font = pygame.font.Font("assets/fonts/Roboto-Bold.ttf", 32)
    info_font = pygame.font.Font("assets/fonts/Roboto-Medium.ttf", 24)
    small_font = pygame.font.Font("assets/fonts/Roboto-Regular.ttf", 18)
except:
    # Fallback to system fonts if custom fonts not available
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    button_font = pygame.font.SysFont("Arial", 32, bold=True)
    info_font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 18)

# Define snakes and ladders
snakes = {
    16: 6,
    47: 26,
    49: 11,
    56: 53,
    62: 19,
    64: 60,
    87: 24,
    93: 73,
    95: 75,
    98: 78
}

ladders = {
    1: 38,
    4: 14,
    9: 31,
    21: 42,
    28: 84,
    36: 44,
    51: 67,
    71: 91,
    80: 100
}

# Create game board texture
def create_board_texture():
    texture = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
    texture.fill((240, 240, 255))
    
    # Create a gradient background
    for y in range(BOARD_SIZE):
        color_value = 240 - int(y * 30 / BOARD_SIZE)
        pygame.draw.line(texture, (color_value, color_value, 255), (0, y), (BOARD_SIZE, y))
    
    return texture

# Create dice textures
def create_dice_textures():
    dice_size = 100
    dice_textures = []
    
    for value in range(1, 7):
        dice = pygame.Surface((dice_size, dice_size), pygame.SRCALPHA)
        
        # Draw dice body
        pygame.draw.rect(dice, WHITE, (0, 0, dice_size, dice_size), border_radius=15)
        pygame.draw.rect(dice, (200, 200, 200), (0, 0, dice_size, dice_size), 2, border_radius=15)
        
        # Draw dots
        dot_positions = {
            1: [(dice_size//2, dice_size//2)],
            2: [(dice_size//4, dice_size//4), (3*dice_size//4, 3*dice_size//4)],
            3: [(dice_size//4, dice_size//4), (dice_size//2, dice_size//2), (3*dice_size//4, 3*dice_size//4)],
            4: [(dice_size//4, dice_size//4), (dice_size//4, 3*dice_size//4), 
                (3*dice_size//4, dice_size//4), (3*dice_size//4, 3*dice_size//4)],
            5: [(dice_size//4, dice_size//4), (dice_size//4, 3*dice_size//4), 
                (dice_size//2, dice_size//2),
                (3*dice_size//4, dice_size//4), (3*dice_size//4, 3*dice_size//4)],
            6: [(dice_size//4, dice_size//4), (dice_size//4, dice_size//2), (dice_size//4, 3*dice_size//4),
                (3*dice_size//4, dice_size//4), (3*dice_size//4, dice_size//2), (3*dice_size//4, 3*dice_size//4)]
        }
        
        for pos in dot_positions[value]:
            pygame.draw.circle(dice, BLACK, pos, dice_size//10)
            
        dice_textures.append(dice)
    
    return dice_textures

# Player class
class Player:
    def __init__(self, color, name, token_type=0):
        self.position = 0
        self.target_position = 0
        self.color = color
        self.name = name
        self.won = False
        self.dice_history = []
        self.token_type = token_type
        self.animation_progress = 0
        self.animation_speed = 0.05
        self.is_animating = False
        self.path = []
        self.offset_x = random.randint(-TILE_SIZE//5, TILE_SIZE//5)
        self.offset_y = random.randint(-TILE_SIZE//5, TILE_SIZE//5)
        
    def start_move(self, steps):
        if self.position + steps <= 100:
            self.target_position = self.position + steps
            self.is_animating = True
            self.animation_progress = 0
            self.path = self.calculate_path(self.position, self.target_position)
            return True
        return False
    
    def calculate_path(self, start, end):
        path = []
        current = start
        
        # Add each step to the path
        while current < end:
            current += 1
            path.append(current)
            
        return path
    
    def update_animation(self):
        if not self.is_animating:
            return False
            
        self.animation_progress += self.animation_speed
        
        if self.animation_progress >= 1:
            self.animation_progress = 0
            
            if len(self.path) > 0:
                self.position = self.path.pop(0)
                
                # Check if we've reached the target
                if len(self.path) == 0:
                    self.is_animating = False
                    
                    # Check for snakes and ladders
                    if self.position in snakes:
                        self.start_snake_animation(snakes[self.position])
                    elif self.position in ladders:
                        self.start_ladder_animation(ladders[self.position])
                    
                    # Check if player won
                    if self.position == 100:
                        self.won = True
                        
                    return True  # Movement completed
            
        return False  # Still animating
    
    def start_snake_animation(self, end_position):
        self.target_position = end_position
        self.is_animating = True
        self.animation_progress = 0
        self.path = [end_position]  # Direct jump to end position for snake
        
    def start_ladder_animation(self, end_position):
        self.target_position = end_position
        self.is_animating = True
        self.animation_progress = 0
        self.path = [end_position]  # Direct jump to end position for ladder
    
    def draw(self, surface):
        if self.position <= 0:
            return
            
        x, y = get_coordinates(self.position)
        
        # Add offsets to avoid overlapping
        x += self.offset_x
        y += self.offset_y
        
        # Draw shadow
        pygame.draw.circle(surface, (50, 50, 50, 100), (x+3, y+3), TILE_SIZE//3)
        
        # Draw token based on type
        if self.token_type == 0:  # Circle token
            pygame.draw.circle(surface, self.color, (x, y), TILE_SIZE//3)
            pygame.draw.circle(surface, WHITE, (x-5, y-5), TILE_SIZE//8)  # Highlight
            pygame.draw.circle(surface, BLACK, (x, y), TILE_SIZE//3, 2)  # Border
        elif self.token_type == 1:  # Star token
            self.draw_star(surface, x, y, TILE_SIZE//2.5, self.color)
        elif self.token_type == 2:  # Diamond token
            self.draw_diamond(surface, x, y, TILE_SIZE//2.5, self.color)
            
    def draw_star(self, surface, x, y, size, color):
        points = []
        for i in range(10):
            angle = math.pi/2 + i * 2*math.pi/10
            radius = size if i % 2 == 0 else size/2
            points.append((x + radius * math.cos(angle), y - radius * math.sin(angle)))
            
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 2)
        
    def draw_diamond(self, surface, x, y, size, color):
        points = [
            (x, y - size),
            (x + size, y),
            (x, y + size),
            (x - size, y)
        ]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, BLACK, points, 2)

# Button class for UI
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        
        # Draw button with rounded corners
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        # Draw text
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

# Helper functions
def get_coordinates(position):
    """Convert board position (1-100) to screen coordinates"""
    if position <= 0:
        return (-100, -100)  # Off-screen for position 0
        
    # Calculate board position
    board_x = (SCREEN_WIDTH - BOARD_SIZE) // 2
    board_y = (SCREEN_HEIGHT - BOARD_SIZE) // 2
    
    # Adjust position to 0-based index
    position -= 1
    
    # Calculate row and column
    row = 9 - (position // 10)  # Rows go from bottom to top
    
    # Columns alternate direction by row
    if row % 2 == 1:  # Odd rows go right to left
        col = 9 - (position % 10)
    else:  # Even rows go left to right
        col = position % 10
        
    # Calculate pixel coordinates (center of tile)
    x = board_x + col * TILE_SIZE + TILE_SIZE // 2
    y = board_y + row * TILE_SIZE + TILE_SIZE // 2
    
    return (x, y)

def draw_board(surface, board_texture):
    # Calculate board position
    board_x = (SCREEN_WIDTH - BOARD_SIZE) // 2
    board_y = (SCREEN_HEIGHT - BOARD_SIZE) // 2
    
    # Draw board background
    surface.blit(board_texture, (board_x, board_y))
    
    # Draw tiles
    for i in range(1, 101):
        x, y = get_coordinates(i)
        row = 9 - ((i-1) // 10)
        
        # Calculate tile position
        tile_x = x - TILE_SIZE // 2
        tile_y = y - TILE_SIZE // 2
        
        # Alternate tile colors
        if (row % 2 == 0 and i % 2 == 0) or (row % 2 == 1 and i % 2 == 1):
            color = (200, 230, 255)
        else:
            color = (255, 255, 255)
            
        # Draw tile with rounded corners
        pygame.draw.rect(surface, color, (tile_x, tile_y, TILE_SIZE, TILE_SIZE), border_radius=5)
        pygame.draw.rect(surface, (100, 100, 100), (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 1, border_radius=5)
        
        # Draw number
        number_text = small_font.render(str(i), True, BLACK)
        surface.blit(number_text, (x - number_text.get_width()//2, y - number_text.get_height()//2))
    
    # Draw snakes
    for start, end in snakes.items():
        start_x, start_y = get_coordinates(start)
        end_x, end_y = get_coordinates(end)
        
        # Draw snake body with curve
        points = []
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            # Add some waviness to the snake
            offset_x = 15 * math.sin(t * math.pi * 3)
            x = start_x + (end_x - start_x) * t + offset_x
            y = start_y + (end_y - start_y) * t
            points.append((x, y))
        
        # Draw snake body
        if len(points) > 1:
            # Draw snake with gradient color
            for i in range(len(points)-1):
                ratio = i / (len(points)-1)
                color = (
                    int(100 + 155 * ratio),  # R: 100 to 255
                    int(50 + 50 * (1-ratio)),  # G: 100 to 50
                    int(200 - 150 * ratio)   # B: 200 to 50
                )
                pygame.draw.line(surface, color, points[i], points[i+1], 8)
        
        # Draw snake head
        pygame.draw.circle(surface, RED, (end_x, end_y), 10)
        pygame.draw.circle(surface, BLACK, (end_x, end_y), 10, 2)
        
        # Draw eyes
        pygame.draw.circle(surface, WHITE, (end_x-3, end_y-3), 3)
        pygame.draw.circle(surface, WHITE, (end_x+3, end_y-3), 3)
        pygame.draw.circle(surface, BLACK, (end_x-3, end_y-3), 1)
        pygame.draw.circle(surface, BLACK, (end_x+3, end_y-3), 1)
    
    # Draw ladders
    for start, end in ladders.items():
        start_x, start_y = get_coordinates(start)
        end_x, end_y = get_coordinates(end)
        
        # Calculate ladder sides
        angle = math.atan2(end_y - start_y, end_x - start_x)
        perpendicular = angle + math.pi/2
        offset = 10
        
        x1_start = start_x + offset * math.cos(perpendicular)
        y1_start = start_y + offset * math.sin(perpendicular)
        x1_end = end_x + offset * math.cos(perpendicular)
        y1_end = end_y + offset * math.sin(perpendicular)
        
        x2_start = start_x - offset * math.cos(perpendicular)
        y2_start = start_y - offset * math.sin(perpendicular)
        x2_end = end_x - offset * math.cos(perpendicular)
        y2_end = end_y - offset * math.sin(perpendicular)
        
        # Draw ladder sides with gradient
        for i in range(10):
            t = i / 9
            color = (
                int(255 - 100 * t),  # R: 255 to 155
                int(165 - 65 * t),   # G: 165 to 100
                int(0 + 100 * t)     # B: 0 to 100
            )
            
            x1 = x1_start + (x1_end - x1_start) * t
            y1 = y1_start + (y1_end - y1_start) * t
            x2 = x1_start + (x1_end - x1_start) * (t + 0.1)
            y2 = y1_start + (y1_end - y1_start) * (t + 0.1)
            
            if t < 0.9:
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 5)
                
            x1 = x2_start + (x2_end - x2_start) * t
            y1 = y2_start + (y2_end - y2_start) * t
            x2 = x2_start + (x2_end - x2_start) * (t + 0.1)
            y2 = y2_start + (y2_end - y2_start) * (t + 0.1)
            
            if t < 0.9:
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 5)
        
        # Draw ladder rungs
        dist = ((end_x - start_x)**2 + (end_y - start_y)**2)**0.5
        steps = int(dist / 25) + 2
        for i in range(1, steps):
            ratio = i / steps
            x1 = x1_start + (x1_end - x1_start) * ratio
            y1 = y1_start + (y1_end - y1_start) * ratio
            x2 = x2_start + (x2_end - x2_start) * ratio
            y2 = y2_start + (y2_end - y2_start) * ratio
            pygame.draw.line(surface, (200, 100, 50), (x1, y1), (x2, y2), 3)

def draw_info_panel(surface, players, current_player, dice_value, dice_textures, game_state):
    # Draw player information
    for i, player in enumerate(players):
        y_pos = 100 + i * 120
        
        # Player panel
        panel_rect = pygame.Rect(50, y_pos, 200, 100)
        pygame.draw.rect(surface, player.color, panel_rect, border_radius=15)
        pygame.draw.rect(surface, BLACK, panel_rect, 2, border_radius=15)
        
        # Highlight current player
        if game_state == STATE_PLAYING and i == current_player and not player.is_animating:
            pygame.draw.rect(surface, WHITE, panel_rect.inflate(10, 10), 3, border_radius=20)
        
        # Player name
        name_text = info_font.render(player.name, True, WHITE)
        surface.blit(name_text, (panel_rect.centerx - name_text.get_width()//2, panel_rect.y + 15))
        
        # Player position
        pos_text = title_font.render(str(player.position), True, WHITE)
        surface.blit(pos_text, (panel_rect.centerx - pos_text.get_width()//2, panel_rect.y + 45))
    
    # Draw dice
    if dice_value > 0 and dice_value <= 6:
        dice_x = SCREEN_WIDTH - 150
        dice_y = SCREEN_HEIGHT // 2 - 50
        surface.blit(dice_textures[dice_value-1], (dice_x, dice_y))
    
    # Draw game instructions
    if game_state == STATE_PLAYING:
        if not players[current_player].is_animating:
            instruction = info_font.render("Press SPACE to roll dice", True, BLACK)
            surface.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT - 50))
    elif game_state == STATE_GAME_OVER:
        for player in players:
            if player.won:
                winner_text = title_font.render(f"{player.name} Wins!", True, player.color)
                surface.blit(winner_text, (SCREEN_WIDTH//2 - winner_text.get_width()//2, 50))

def draw_menu(surface):
    # Draw title
    title_text = title_font.render("Snake and Ladder", True, PURPLE)
    surface.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 150))
    
    subtitle_text = info_font.render("Modern Edition", True, ORANGE)
    surface.blit(subtitle_text, (SCREEN_WIDTH//2 - subtitle_text.get_width()//2, 210))
    
    # Draw animated snake
    current_time = pygame.time.get_ticks() / 1000
    for i in range(20):
        t = (current_time + i/10) % 1
        x = SCREEN_WIDTH//2 + math.sin(t * math.pi * 2) * 200
        y = 300 + i * 10
        size = 15 - i/2
        color = (
            int(100 + 155 * (1-i/20)),
            int(50 + 50 * (i/20)),
            int(200 - 150 * (1-i/20))
        )
        pygame.draw.circle(surface, color, (x, y), size)
    
    # Draw animated ladder
    ladder_x = SCREEN_WIDTH//2 - 100
    ladder_y = 400
    for i in range(5):
        rung_y = ladder_y + i * 30
        pygame.draw.line(surface, ORANGE, (ladder_x, rung_y), (ladder_x + 200, rung_y), 5)
    pygame.draw.line(surface, ORANGE, (ladder_x, ladder_y), (ladder_x, ladder_y + 120), 5)
    pygame.draw.line(surface, ORANGE, (ladder_x + 200, ladder_y), (ladder_x + 200, ladder_y + 120), 5)

def roll_dice_animation(surface, board_texture, players, dice_textures):
    for _ in range(10):
        value = random.randint(1, 6)
        
        # Clear screen
        surface.fill((220, 240, 255))
        
        # Draw board and players
        draw_board(surface, board_texture)
        for player in players:
            player.draw(surface)
        
        # Draw dice
        dice_x = SCREEN_WIDTH - 150
        dice_y = SCREEN_HEIGHT // 2 - 50
        surface.blit(dice_textures[value-1], (dice_x, dice_y))
        
        pygame.display.flip()
        pygame.time.delay(100)
    
    return random.randint(1, 6)

def main():
    # Create game assets
    board_texture = create_board_texture()
    dice_textures = create_dice_textures()
    
    # Create players
    players = [
        Player(RED, "Player 1", 0),
        Player(BLUE, "Player 2", 1)
    ]
    
    # Create buttons
    play_button = Button(SCREEN_WIDTH//2 - 100, 500, 200, 60, "Play Game", GREEN, (100, 255, 100))
    quit_button = Button(SCREEN_WIDTH//2 - 100, 580, 200, 60, "Quit", RED, (255, 100, 100))
    menu_button = Button(SCREEN_WIDTH - 120, 20, 100, 40, "Menu", ORANGE, (255, 200, 100))
    
    # Game variables
    current_player = 0
    dice_value = 0
    game_state = STATE_MENU
    
    # Main game loop
    running = True
    while running:
        # Handle events
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_state == STATE_PLAYING:
                    if not players[current_player].is_animating:
                        dice_value = roll_dice_animation(screen, board_texture, players, dice_textures)
                        players[current_player].dice_history.append(dice_value)
                        players[current_player].start_move(dice_value)
                elif event.key == pygame.K_r and game_state == STATE_GAME_OVER:
                    # Reset game
                    for player in players:
                        player.position = 0
                        player.target_position = 0
                        player.won = False
                        player.dice_history = []
                        player.is_animating = False
                    current_player = 0
                    dice_value = 0
                    game_state = STATE_PLAYING
        
        # Clear screen
        screen.fill((220, 240, 255))
        
        # Update game state
        if game_state == STATE_MENU:
            # Update buttons
            play_button.update(mouse_pos)
            quit_button.update(mouse_pos)
            
            # Handle button clicks
            if play_button.is_clicked(mouse_pos, mouse_clicked):
                game_state = STATE_PLAYING
            elif quit_button.is_clicked(mouse_pos, mouse_clicked):
                running = False
                
            # Draw menu
            draw_menu(screen)
            play_button.draw(screen)
            quit_button.draw(screen)
            
        elif game_state == STATE_PLAYING or game_state == STATE_GAME_OVER:
            # Update menu button
            menu_button.update(mouse_pos)
            if menu_button.is_clicked(mouse_pos, mouse_clicked):
                game_state = STATE_MENU
            
            # Update player animation
            if game_state == STATE_PLAYING and players[current_player].is_animating:
                movement_completed = players[current_player].update_animation()
                
                if movement_completed:
                    # Check if player won
                    if players[current_player].won:
                        game_state = STATE_GAME_OVER
                    else:
                        # Switch to next player
                        current_player = (current_player + 1) % len(players)
            
            # Draw game elements
            draw_board(screen, board_texture)
            draw_info_panel(screen, players, current_player, dice_value, dice_textures, game_state)
            
            # Draw players
            for player in players:
                player.draw(screen)
                
            # Draw menu button
            menu_button.draw(screen)
            
            # Draw game over message
            if game_state == STATE_GAME_OVER:
                restart_text = info_font.render("Press R to play again", True, BLACK)
                screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT - 50))
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
