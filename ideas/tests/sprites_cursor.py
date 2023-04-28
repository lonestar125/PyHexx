import pygame, sys

class Cursor(pygame.sprite.Sprite):
    def __init__(self, picture_path):
        super().__init__()
        self.image = pygame.image.load(picture_path)
        self.rect = self.image.get_rect()
    def update(self):
        self.rect.center = pygame.mouse.get_pos()


# Genral Setup
pygame.init()
clock = pygame.time.Clock()


# Game Screen
S_WIDTH = 900
S_HIGHT = 500
FPS = 60
screen = pygame.display.set_mode((S_WIDTH,S_HIGHT))
white = [255, 255, 255]
pygame.mouse.set_visible(False)

# Cursor
cursor = Cursor("Sprites/cursor.png")
cursor_group =pygame.sprite.Group()
cursor_group.add(cursor)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.flip()
    screen.fill(white)
    cursor_group.draw(screen)
    cursor_group.update()
    clock.tick(FPS)