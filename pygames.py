import pygame
import random

pygame.init()

screen = pygame.display.set_mode((800, 600))
star = pygame.image.load("star_sprite.png").convert_alpha()
star_rect = star.get_rect()
stars = []

for i in range(100):
    x = random.randint(0, 800)
    y = random.randint(0, 600)
    stars.append((x, y))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    for i, (x, y) in enumerate(stars):
        x -= 1
        if x < -star_rect.width:
            x = 800
        stars[i] = (x, y)

    for x, y in stars:
        screen.blit(star, (x, y))

    pygame.display.update()
    pygame.time.wait(10)