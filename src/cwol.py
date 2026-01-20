import pygame
import numpy as np
import time
import colorsys

# Initialize Pygame
pygame.init()

# Screen dimensions
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    pygame.FULLSCREEN
)

# Colors
WHITE = (128, 128, 128)
BLACK = (25, 25, 25)

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


# ===============================
# Cell class
# ===============================
class Cell:
    def __init__(self, alive=0, energy=0, altruistic=False):
        self.alive = alive
        self.energy = energy
        self.altruistic = altruistic

    def copy(self):
        return Cell(self.alive, self.energy, self.altruistic)


# ===============================
# Grid of cells
# ===============================
grid = np.empty((nxC, nyC), dtype=object)
for x in range(nxC):
    for y in range(nyC):
        grid[x, y] = Cell()


# ===============================
# Gosper Glider Gun
# ===============================
gun = [
    (1,5),(1,6),(2,5),(2,6),
    (11,5),(11,6),(11,7),
    (12,4),(12,8),
    (13,3),(13,9),
    (14,3),(14,9),
    (15,6),
    (16,4),(16,8),
    (17,5),(17,6),(17,7),
    (18,6),
    (21,3),(21,4),(21,5),
    (22,3),(22,4),(22,5),
    (23,2),(23,6),
    (25,1),(25,2),
    (26,1),(26,2)
]

for dx, dy in gun:
    grid[dx + 10, dy + 10].alive = 1


# ===============================
# Random symmetric seed
# ===============================
np.random.seed(1)
for x in range(60, 140):
    for y in range(60, 140):
        if np.random.rand() > 0.85:
            grid[x, y].alive = 1
            grid[nxC-x-1, y].alive = 1
            grid[x, nyC-y-1].alive = 1
            grid[nxC-x-1, nyC-y-1].alive = 1


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

# ===============================
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

                if grid[x, y].alive == 0 and n_neigh == 3:
                    newGrid[x, y].alive = 1
                    newGrid[x, y].energy = 5

                elif grid[x, y].alive == 1 and (n_neigh < 2 or n_neigh > 3):
                    newGrid[x, y].alive = 0

            poly = [
                (offset_x + x * dimCW, offset_y + y * dimCH),
                (offset_x + (x + 1) * dimCW, offset_y + y * dimCH),
                (offset_x + (x + 1) * dimCW, offset_y + (y + 1) * dimCH),
                (offset_x + x * dimCW, offset_y + (y + 1) * dimCH)
            ]

            if newGrid[x, y].alive == 0:
                pygame.draw.polygon(screen, BLACK, poly, 1)
            else:
                pygame.draw.polygon(screen, RAINBOW, poly, 0)

    pygame.display.flip()
    grid = newGrid
