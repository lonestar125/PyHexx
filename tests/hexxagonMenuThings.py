import pygame
import pygame_menu 

mode = 1

def set_mode(value, mod):
    global mode
    mode = mod
    print(mode)

def start_game():
    global difficulty
    print("started with mode", mode)

pygame.init()
surface = pygame.display.set_mode((800, 800))
mytheme = pygame_menu.Theme(background_color = (pygame.Color(82, 46, 168)), 
                            title_background_color=(4, 47, 126), 
                            title_font_shadow=True, widget_padding = 2, 
                            title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_UNDERLINE_TITLE,
                            title_close_button = True,
                            border_width = 5,
                            border_color = ((pygame.Color(82, 46, 168))))

menu = pygame_menu.Menu('Welcome', 800, 600, theme = mytheme)
menu.add.text_input('Name :', default='John Pork')
menu.add.selector('Game Mode :', [('Single Player Hard af (litearlly me)', 1), ('Single Player soft (flacid moment)', 2), ('Two players(go get a gf)', 3)], onchange = set_mode)
menu.add.button('Play', start_game)
menu.add.button('Quit', pygame_menu.events.EXIT)
menu.mainloop(surface)