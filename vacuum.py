import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen Setup
WIDTH, HEIGHT = 1100, 650
SIDE_PANEL_WIDTH = 300
GAME_WIDTH = WIDTH - SIDE_PANEL_WIDTH
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Vacuum Cleaner - Pro Simulation")

# Colors
WHITE, DARK_GREY, GREEN, YELLOW, RED, BLACK = (255,255,255), (30,30,30), (46,204,113), (241,196,15), (231,76,60), (0,0,0)
BLUE = (52, 152, 219)

# Function to load images
def load_scaled_transparent(path, size):
    try:
        img = pygame.image.load(path).convert_alpha() 
        return pygame.transform.scale(img, size)
    except:
        img = pygame.Surface(size).convert(); img.fill(RED); return img

# Load Images
bed_img = load_scaled_transparent('bed.png', (300, 220))       
sofa_img = load_scaled_transparent('sofa.png', (200, 120))
chairs_img = load_scaled_transparent('chairs.png', (140, 110))
wardrobe_img = load_scaled_transparent('wardrobe.png', (130, 180)) 
vacuum_img = load_scaled_transparent('vaccum1.png', (70, 70))

try:
    floor_img = pygame.image.load('floor.png').convert() 
    floor_img = pygame.transform.scale(floor_img, (GAME_WIDTH, HEIGHT))
except:
    floor_img = pygame.Surface((GAME_WIDTH, HEIGHT)); floor_img.fill(WHITE)

# Furniture Rects 
furniture_rects = [
    pygame.Rect(80, 40, 130, 170),
    pygame.Rect(500, 100, 140, 100),
    pygame.Rect(0, 500, 200, 110),
    pygame.Rect(480, 410, 300, 210)
]

def spawn_dirt(count):
    new_list = []
    while len(new_list) < count:
        rx, ry = random.randint(120, GAME_WIDTH - 150), random.randint(120, HEIGHT - 150)
        d_rect = pygame.Rect(rx, ry, 12, 12)
        if not any(d_rect.colliderect(f.inflate(60, 60)) for f in furniture_rects): 
            new_list.append(d_rect)
    return new_list

# Variables
vac_x, vac_y = 400, 300
vac_speed = 4
num_dirt = 15
dirt_list = spawn_dirt(num_dirt)
cleaned_dirt, is_paused = 0, True 

# UI Setup
font = pygame.font.SysFont("Trebuchet MS", 22, bold=True)
btn_font = pygame.font.SysFont("Trebuchet MS", 26, bold=True)
panel_x = GAME_WIDTH + 20

# UI Components
start_btn = pygame.Rect(panel_x, 250, 250, 50)
pause_btn = pygame.Rect(panel_x, 320, 250, 50)
reset_btn = pygame.Rect(panel_x, 390, 250, 50)
slider_rect = pygame.Rect(panel_x, 520, 250, 10)
slider_handle = pygame.Rect(panel_x + 100, 510, 20, 30)
dragging_slider = False

running = True
clock = pygame.time.Clock()

while running:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn.collidepoint(mouse_pos): is_paused = False
            if pause_btn.collidepoint(mouse_pos): is_paused = True
            if reset_btn.collidepoint(mouse_pos):
                vac_x, vac_y, cleaned_dirt, is_paused = 400, 300, 0, True
                dirt_list = spawn_dirt(num_dirt)
            if slider_handle.collidepoint(mouse_pos): dragging_slider = True
        if event.type == pygame.MOUSEBUTTONUP: dragging_slider = False

    if dragging_slider:
        new_x = max(panel_x, min(mouse_pos[0], panel_x + 250))
        slider_handle.x = new_x - 10
        vac_speed = 1 + ((new_x - panel_x) / 250) * 9

    # --- UPDATED STUCK-PROOF NAVIGATION ---
    if not is_paused and dirt_list:
        vac_center = pygame.math.Vector2(vac_x + 35, vac_y + 35)
        nearest = min(dirt_list, key=lambda d: vac_center.distance_to(pygame.math.Vector2(d.centerx, d.centery)))
        target_vec = pygame.math.Vector2(nearest.centerx, nearest.centery)
        
        if vac_center.distance_to(target_vec) > 2:
            direction = (target_vec - vac_center).normalize()
            
            # --- X Movement ---
            next_x = vac_x + direction.x * vac_speed
            rect_x = pygame.Rect(next_x, vac_y, 60, 60) # Chota rect for collision
            if not any(rect_x.colliderect(f) for f in furniture_rects):
                vac_x = next_x
            
            # --- Y Movement ---
            next_y = vac_y + direction.y * vac_speed
            rect_y = pygame.Rect(vac_x, next_y, 60, 60)
            if not any(rect_y.colliderect(f) for f in furniture_rects):
                vac_y = next_y
            
            # --- Escape Logic ---
            
            if any(rect_x.colliderect(f) for f in furniture_rects) and any(rect_y.colliderect(f) for f in furniture_rects):
                vac_x += random.choice([-2, 2])
                vac_y += random.choice([-2, 2])
                # Skip target for a while
                if random.random() < 0.05:
                    dirt_list.append(dirt_list.pop(dirt_list.index(nearest)))
        
        # Cleaning (Bigger Radius)
        vac_rect = pygame.Rect(vac_x, vac_y, 70, 70)
        for d in dirt_list[:]:
            if vac_rect.inflate(35, 35).colliderect(d):
                dirt_list.remove(d); cleaned_dirt += 1

    # Drawing
    screen.fill(WHITE); screen.blit(floor_img, (0, 0)) 
    for d in dirt_list: pygame.draw.circle(screen, (139, 69, 19), (d.centerx, d.centery), 6) 
    
    screen.blit(wardrobe_img, (80, 40))
    screen.blit(chairs_img, (500, 100))
    screen.blit(sofa_img, (0, 500))
    screen.blit(bed_img, (480, 410))
    screen.blit(vacuum_img, (vac_x, vac_y))

    # UI Panel
    pygame.draw.rect(screen, DARK_GREY, (GAME_WIDTH, 0, SIDE_PANEL_WIDTH, HEIGHT))
    screen.blit(font.render(f"Cleaned Dirt: {cleaned_dirt}", True, GREEN), (panel_x, 100))
    screen.blit(font.render(f"Remaining: {len(dirt_list)}", True, RED), (panel_x, 140))
    
    pygame.draw.rect(screen, GREEN, start_btn, border_radius=10); screen.blit(btn_font.render("START", True, BLACK), (panel_x + 85, 260))
    pygame.draw.rect(screen, YELLOW, pause_btn, border_radius=10); screen.blit(btn_font.render("PAUSE", True, BLACK), (panel_x + 85, 330))
    pygame.draw.rect(screen, RED, reset_btn, border_radius=10); screen.blit(btn_font.render("RESET", True, BLACK), (panel_x + 85, 400))

    screen.blit(font.render(f"Speed Control: {int(vac_speed)}", True, WHITE), (panel_x, 480))
    pygame.draw.rect(screen, BLACK, slider_rect); pygame.draw.rect(screen, BLUE, slider_handle, border_radius=5)

    pygame.display.flip(); clock.tick(60)

pygame.quit()