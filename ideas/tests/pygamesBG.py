import pygame
import random

pygame.init()

screen = pygame.display.set_mode((800, 600))
star = pygame.image.load("star_sprite.png").convert_alpha()
star_rect = star.get_rect()
stars = []

speed1 = 0.8
speed2 = 1.2

for i in range(100):
    x = random.randint(0, 800)
    y = random.randint(0, 600)
    speed = speed1 if random.random() < 0.5 else speed2
    stars.append((x, y, speed))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    for i, (x, y, speed) in enumerate(stars):
        x -= speed
        if x < -star_rect.width:
            x = 800
        stars[i] = (x, y, speed)

    for x, y, speed in stars:
        screen.blit(star, (x, y))

    pygame.display.update()
    pygame.time.wait(10)
