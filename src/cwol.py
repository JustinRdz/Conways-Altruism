import random
import pygame
import numpy as np
import time
import colorsys
import matplotlib.pyplot as plt

def energy_to_color(energy, max_energy=10):
    """
    Maps energy to a color:
    low energy -> red/dark
    high energy -> green/bright
    """
    
    e = max(0, min(energy, max_energy)) / max_energy
    hue = 0.33 * e        # 0 = red, 0.33 = green
    value = 0.3 + 0.7 * e # avoid pure black
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, value)
    return (int(r * 255), int(g * 255), int(b * 255))

# Initialize Pygame
pygame.init()
font = pygame.font.SysFont("monospace", 24)
generation = 0
altruistic_count = 0
altruism_rate = 0.5
altruism_history = []
generation_history = []

# Screen dimensions
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

# Colors
WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
GREEN = (0, 255, 0)

pygame.display.set_caption("CWOL")
t = 0
screen.fill(BLACK)

nxC, nyC = 200, 200

cell_size = min(SCREEN_WIDTH // nxC, SCREEN_HEIGHT // nyC)
dimCW = dimCH = cell_size

map_width  = nxC * cell_size
map_height = nyC * cell_size

offset_x = (SCREEN_WIDTH  - map_width)  // 2
offset_y = (SCREEN_HEIGHT - map_height) // 2


# Cell class
class Cell:
    def __init__(self, alive=0, energy=0, altruistic=False):
        self.alive = alive
        self.energy = energy
        self.altruistic = altruistic

    def copy(self):
        return Cell(self.alive, self.energy, self.altruistic)


# Grid of cells
grid = np.empty((nxC, nyC), dtype=object)
for x in range(nxC):
    for y in range(nyC):
        grid[x, y] = Cell()
        grid[x, y].energy = 5
        # if random.random() < altruism_rate:
        #     grid[x, y].altruistic = True
        #     altruistic_count += 1

# Energy baseline
INITIAL_TOTAL_ENERGY = nxC * nyC * 5

# # Random symmetric seed
# # ===============================
# np.random.seed(1)
# for x in range(60, 140):
#     for y in range(60, 140):
#         if np.random.rand() > 0.85:
#             grid[x, y].alive = 1
#             grid[nxC-x-1, y].alive = 1
#             grid[x, nyC-y-1].alive = 1
#             grid[nxC-x-1, nyC-y-1].alive = 1


# Automata palo
grid[5, 3].alive = 1
grid[5, 4].alive = 1
grid[5, 5].alive = 1

# Automata planeador
grid[21, 21].alive = 1
grid[22, 22].alive = 1
grid[22, 23].alive = 1
grid[21, 23].alive = 1
grid[20, 23].alive = 1


pauseExect = False

# Main loop
# ===============================
while True:

    newGrid = np.empty((nxC, nyC), dtype=object)
    for x in range(nxC):
        for y in range(nyC):
            newGrid[x, y] = grid[x, y].copy()

    screen.fill(BLACK)
    time.sleep(0.001)
    t += 1
    generation += 1

    hue = (t % 360) / 360.0
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    RAINBOW = (int(r * 255), int(g * 255), int(b * 255))

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pauseExect = not pauseExect
            elif event.key == pygame.K_p:
                plt.plot(generation_history, altruism_history)
                plt.xlabel("Generation")
                plt.ylabel("Altruistic Cell Count")
                plt.title("Altruism Over Generations")
                plt.show()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()

        mouseClick = pygame.mouse.get_pressed()
        if sum(mouseClick) > 0:
            posX, posY = pygame.mouse.get_pos()
            if (
                offset_x <= posX < offset_x + map_width and
                offset_y <= posY < offset_y + map_height
            ):
                celX = int((posX - offset_x) / dimCW)
                celY = int((posY - offset_y) / dimCH)
                newGrid[celX, celY].alive = not mouseClick[2]

    current_total_energy = 0

    for y in range(nyC):
        for x in range(nxC):

            if not pauseExect:
                n_neigh = (
                    grid[(x - 1) % nxC, (y - 1) % nyC].alive +
                    grid[(x    ) % nxC, (y - 1) % nyC].alive +
                    grid[(x + 1) % nxC, (y - 1) % nyC].alive +
                    grid[(x - 1) % nxC, (y    ) % nyC].alive +
                    grid[(x + 1) % nxC, (y    ) % nyC].alive +
                    grid[(x - 1) % nxC, (y + 1) % nyC].alive +
                    grid[(x    ) % nxC, (y + 1) % nyC].alive +
                    grid[(x + 1) % nxC, (y + 1) % nyC].alive
                )
                # Rules
                if grid[x, y].alive == 0 and n_neigh == 3:
                    newGrid[x, y] = Cell(alive=1, energy=5, altruistic=(random.random() < altruism_rate))

                # elif grid[x, y].alive == 1 and (n_neigh < 2 or n_neigh > 3):
                #     newGrid[x, y].alive = 0
                
                # Energy decay and death
                elif grid[x, y].alive == 1:
                    newGrid[x, y].energy -= 1
                    if newGrid[x, y].energy <= 0:
                        newGrid[x, y].alive = 0
                        newGrid[x, y].energy = 0
                
                # Altruistic energy                
                if grid[x, y].altruistic and grid[x, y].alive:
                    neighbors = []
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx = (x + dx) % nxC
                            ny = (y + dy) % nyC
                            if (grid[nx, ny].alive and newGrid[nx, ny].energy > newGrid[x, y].energy):
                                newGrid[nx, ny].energy += 1
                                newGrid[x, y].energy -= 1
                                break

            current_total_energy += max(newGrid[x, y].energy, 0)
                

            poly = [
                (offset_x + x * dimCW, offset_y + y * dimCH),
                (offset_x + (x + 1) * dimCW, offset_y + y * dimCH),
                (offset_x + (x + 1) * dimCW, offset_y + (y + 1) * dimCH),
                (offset_x + x * dimCW, offset_y + (y + 1) * dimCH)
            ]

            if newGrid[x, y].alive == 0:
                pygame.draw.polygon(screen, BLACK, poly, 1)
            else:
                color = energy_to_color(newGrid[x, y].energy)

                pygame.draw.polygon(screen, color, poly, 0)

                # Optional: altruistic cells get a white outline
                if newGrid[x, y].altruistic:
                    pygame.draw.polygon(screen, WHITE, poly, 1)

    while current_total_energy < INITIAL_TOTAL_ENERGY:
        rx = random.randrange(nxC)
        ry = random.randrange(nyC)
        if newGrid[rx, ry].alive == 1:
            newGrid[rx, ry].energy += 1
            current_total_energy += 1

    altruistic_count = 0
    for x in range(nxC):
        for y in range(nyC):
            if grid[x, y].alive and grid[x, y].altruistic:
                altruistic_count += 1

    alive_count = sum(
    1 for x in range(nxC) for y in range(nyC)
    if grid[x, y].alive)

    altruist_fraction = altruistic_count / max(alive_count, 1)


    altruism_history.append(altruistic_count)
    generation_history.append(generation)

    gen_text = font.render(f"Generation: {generation}", True, WHITE)
    screen.blit(gen_text, (20, 20))
    gen_text = font.render(f"Altruism Count: {altruistic_count}", True, WHITE)
    screen.blit(gen_text, (20, 40))

    pygame.display.flip()
    grid = newGrid
