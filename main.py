# Name: Kevin D
# Date: June 7th 2021
# Course: ICS3U1-11
# Teacher: Mr. Shaft
# Purpose: A basic paint program that allows you to draw pictures, shapes, and save & open images.

# References:
# - https://www.pygame.org/docs/ (Pygame documentation and examples from Github)
# - https://docs.google.com/document/d/1bHBvrP2J9g3_8bTwlSpyZ2wVILb1z3Zii1P7S8_pWBM/edit (Starter code)
# - https://www.pygame.org/docs/ref/mouse.html (Mouse scrolling)
# - https://stackoverflow.com/questions/17267395/how-to-take-screenshot-of-certain-part-of-screen-in-pygame (Saving screenshots)


# Challenges
# 1. Circles would overlap onto the background instead of staying on the canvas
# - Redraws a frame around the canvas everytime so that the paint doesn't leak out
# 2. Couldn't figure out how to make a bunch of buttons using "clean" code
# - Used two aligned lists for the rects and their colours
# - Struggled a while with dictionaries, talk about that
# 3. Don't name your own functions after a library, like random... do something like random_colours instead.
# 4. Saved images weren't jpgs
# - https://github.com/search?q=pygame.image.save&type=Code&l=Python (Examples via pygame documentation)
# 5. Tool selection
# - So essentially the issue came from the order of the functions called. Let's say I called paintbrush tool first
# and I click on the rectangle tool to change it. Well, since I called paintbrush tool first, when IT is checking the
# draw mode, draw_mode still == PAINT. Therefore it'll draw the outline, as it should. But then the signal reaches
# rect tool AFTERWARDS and turns draw_mode into rect, but it's too late because the outline was already drawn around
# the brush tool. It would require another click for the paint tool to actually update.
# - Solution? Create a separate function to check state first before drawing
# 6. Talk about how got inspiration for colour squares from sprite sheet code, the mod part

# Controls!
# - Click and hold on canvas to paint, or draw shapes depending on the tool selected. Use right click to erase.
# - Click the icons on the right side to change tools
# - Left clicking on the colour palette will change brush colour, right clicking will change background colour. Same for random.
# - The current brush colour and size are displayed at the bottom right
# - To save an image, click the floppy disk icon on the top right and enter the desired file name in the prompt in the console
#   - You can save a new image or update an existing one.
# - To open a saved image, click the folder icon on the top right and enter the file name into the prompt

import pygame
import random
pygame.init()

# Setup
size = width, height = 800, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Dream Painter")
button = 0
click = pygame.mixer.Sound("Click.wav")
pygame.mixer.Sound.set_volume(click, 0.7)
running = True
setup = False
myClock = pygame.time.Clock()

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (64, 64, 64)
MENU_COLOUR = (10, 41, 0)
screen.fill(MENU_COLOUR)

# Colour palette stolen from Microsoft Paint
colours = [(0, 0, 0), (127, 127, 127), (136, 0, 21), (237, 28, 36), (255, 127, 39), (255, 242, 0), (34, 177, 76), (0, 162, 232),
           (63, 72, 204), (163, 73, 164), (255, 255, 255), (195, 195, 195), (185, 122, 87), (255, 174, 201), (255, 201, 14),
           (239, 228, 136), (181, 230, 29), (153, 217, 234), (112, 146, 190), (200, 191, 231)]
colour_rects = []  # Will be useful later
FOREGROUND = BLACK
BACKGROUND = WHITE
on_canvas = False
brush_size = 10
MAX = 25
MIN = 5

# Paint states
PAINT = 0
RECT = 1
ELLI = 2
draw_mode = PAINT


def display_coordinates(screen):  # Borrowed from pygame basic setup
    fontCoords = pygame.font.SysFont("arial", 14)
    textCoords = fontCoords.render(str(pygame.mouse.get_pos()), True, RED)
    textRect = textCoords.get_rect()
    textRect.topleft=(0, 0)
    screen.blit(textCoords, textRect)


def getVal(tup):
    """ getVal returns the (position+1) of the first 1 within a tuple.
        This is used because MOUSEBUTTONDOWN and MOUSEMOTION deal with
        mouse events differently """
    for i in range(3):
        if tup[i] == 1:
            return i+1
    return 0


def draw_canvas(screen):  # Initializes canvas
    global canvas  # Makes canvas a global variable so that it can be checked/used in other functions
    canvas = pygame.Rect(30, 30, 500, 540)
    pygame.draw.rect(screen, BACKGROUND, canvas)


def check_canvas(mx, my):
    global on_canvas
    if pygame.Rect.collidepoint(canvas, (mx, my)):  # Checks if the mouse cursor is on the canvas
        on_canvas = True
    else:
        on_canvas = False


def drawing(screen, button):
    if on_canvas and draw_mode == PAINT:  # Only paints if the cursor is on canvas, and the current draw mode is set to paint
        if button == 1:  # Left mouse is the paintbrush
            pygame.draw.circle(screen, FOREGROUND, (mx, my), brush_size)
        if button == 3:  # Right mouse paints the current background colour, like an eraser
            pygame.draw.circle(screen, BACKGROUND, (mx, my), brush_size)

    # Redraws a "frame" around the canvas so that paint can't get outside of it
    pygame.draw.rect(screen, MENU_COLOUR, (0, 0, 560, 30))
    pygame.draw.rect(screen, MENU_COLOUR, (0, 570, 560, 30))
    pygame.draw.rect(screen, MENU_COLOUR, (0, 30, 30, 540))
    pygame.draw.rect(screen, MENU_COLOUR, (530, 30, 30, 540))


def colour_squares(screen, width, height, column_height):  # Draws the coloured squares for colour selection
    global colour_rects

    # The starting positions of the first square
    squareX = 560
    squareY = 90
    for i in range(len(colours)):  # Loops through all the colours
        temp_rect = pygame.Rect(squareX, squareY, width, height)  # Creates a rect object that is stored into colour_rects to later be used for mouse interaction
        pygame.draw.rect(screen, colours[i], temp_rect)  # Draws the rectangle to screen
        colour_rects.append(temp_rect)
        squareY += height  # Moves lower to the spot of the next rect
        if (i+1) % column_height == 0:  # When the current index + 1 (how many times the loop has run) is a multiple of
            # the column height, start a new column
            squareX += width
            squareY = 90


def colourful_buttons(mouse_rect):
    global FOREGROUND, BACKGROUND
    if pygame.Rect.collidelist(mouse_rect, colour_rects) != -1 and button == 1:  # Checks if the mouse is on any of the rects
        FOREGROUND = colours[pygame.Rect.collidelist(mouse_rect, colour_rects)]  # If the user left clicks, it sets the foreground
        # colour to the same one as the rect, because the lists "colour_rects" and "colours" are aligned. So for example if
        # the rect object for the red coloured box is in index 4 of colour_rects, then the tuple for its red colour will
        # also be in index 4 of colours. So collidelist will return the index of the rectangle that was clicked in "colour_rects",
        # which in turn is the index of that rectangle's colour in the list "colours".
        click.play()
    elif pygame.Rect.collidelist(mouse_rect, colour_rects) != -1 and button == 3:  # If the user right clicks, set the background to that colour
        BACKGROUND = colours[pygame.Rect.collidelist(mouse_rect, colour_rects)]
        draw_canvas(screen)  # Update canvas
        click.play()


# Creates the actual button
# x = 560, y = 50, w = 60, h = 30
text_font = pygame.font.SysFont("Times new roman", 20)
clear_text = text_font.render("Clear", True, WHITE)
cleartext_rect = clear_text.get_rect(center = (560 + 60/2, 50 + 30/2))  # Creates a centered rect for the text
clear_rect = pygame.Rect(560, 50, 60, 30)  # Creates the button background
pygame.draw.rect(screen, GRAY, clear_rect)
screen.blit(clear_text, cleartext_rect)
def clear(mouse_rect):
    # Detects clicks
    if pygame.Rect.colliderect(mouse_rect, clear_rect):
        draw_canvas(screen)  # If the user clicks on "clear", it'll call on the "canvas" function to redraw it
        click.play()


# x = 635, y = 50, w = 60, h = 30
text_font = pygame.font.SysFont("Times new roman", 16)
random_text = text_font.render("Random", True, WHITE)
randomtext_rect = random_text.get_rect(center = (635 + 60/2, 50 + 30/2))
random_rect = pygame.Rect(635, 50, 60, 30)
pygame.draw.rect(screen, GRAY, random_rect)
screen.blit(random_text, randomtext_rect)
def random_colour(mouse_rect):
    global FOREGROUND, BACKGROUND

    # Detects clicks
    if pygame.Rect.colliderect(mouse_rect, random_rect) and button == 1:  # If the user left clicks, give a random foreground colour
        random_colour = random.randint(0, len(colours) - 1)
        FOREGROUND = colours[random_colour]
        click.play()
    elif pygame.Rect.colliderect(mouse_rect, random_rect) and button == 3:  # If the user right clicks, give a random background colour
        random_colour = random.randint(0, len(colours) - 1)
        BACKGROUND = colours[random_colour]
        click.play()
        draw_canvas(screen)  # Updates canvas


# x = 700, y = 40, w = 50, h = 50
save_icon = pygame.image.load("Save icon.png")
save_icon = pygame.transform.scale(save_icon, (50, 50))
save_rect = save_icon.get_rect()
save_rect.topleft = (700, 40)
screen.blit(save_icon, save_rect)
def save_image(mouse_rect):
    if pygame.Rect.colliderect(mouse_rect, save_rect):  # If the user clicks on the save icon
        image_name = input("Please enter the name of this image: ")  # Asks for a file name
        screenshot = screen.subsurface(canvas)  # Takes the canvas as a subsurface
        pygame.image.save(screenshot, image_name + ".jpg")  # Saves that subsurface as a .jpg file, using the name given

        # Saves the name of the file in a text file called "pictures"
        pictures = open("Pictures.txt", "r")  # First opens the file as read mode to check
        update = False  # Uses a boolean to check if the user wants to update or save a new file
        for picture in pictures:
            if picture.rstrip() == image_name:  # If the user is saving a file under an existing name they're updating an existing file,
            # we don't need its file name twice
                update = True
        pictures.close()
        if update == False:  # The file name entered doesn't already exist, the user wants to save a new file
            pictures = open("Pictures.txt", "a")  # Opens the file again, this time in append mode
            pictures.write("\n" + image_name)  # Adds name
            pictures.close()


# x = 755, y = 48, w = 40, h = 30
open_icon = pygame.image.load("Open icon.png")
open_icon = pygame.transform.scale(open_icon, (40, 30))
open_rect = open_icon.get_rect()
open_rect.topleft = (755, 48)
screen.blit(open_icon, open_rect)
def open_image(mouse_rect):
    if pygame.Rect.colliderect(mouse_rect, open_rect):  # If the user clicks on the open icon
        print("Greetings! Here are the pictures you have saved: ")  # First print out all the file names stored in the .txt file "pictures"
        pictures = open("Pictures.txt", "r")
        image_names = []  # Creates a list to check if an image with that name actually exists
        for picture in pictures:
            print(picture.rstrip())
            image_names.append(picture.rstrip())
        pictures.close()
        open_this = input("Please enter the name of the file you'd like to open: ")  # Asks the user which file they'd like to open
        while open_this not in image_names:  # Stops user from crashing program because they entered a file name that doesn't exist
            print("Sorry! The file you're looking for does not exist.")
            open_this = input("Please enter the name of the file you'd like to open: ")
        open_picture = pygame.image.load(open_this + ".jpg")
        screen.blit(open_picture, canvas)  # Opens the file and blits it to canvas


def check_mode(mouse_rect):  # Checks what the current drawing mode is
    global draw_mode

    if pygame.Rect.colliderect(mouse_rect, paint_rect):  # If user clicked on paint icon, change mode to paint
        draw_mode = PAINT
        click.play()
    elif pygame.Rect.colliderect(mouse_rect, rectool_rect):  # If use clicked on rect icon, change mode to rect
        draw_mode = RECT
        click.play()
    elif pygame.Rect.colliderect(mouse_rect, ellipse_rect):  # If use clicked on ellipse icon, change mode to ellipse
        draw_mode = ELLI
        click.play()


def paint_tool(screen, x, y, w, h, draw_mode):
    global paint_rect

    pygame.draw.rect(screen, MENU_COLOUR, (x - 5, y - 5, w + 10, h + 10))  # Redraws over the area of the icon to remove any previous traces
    paint_rect = pygame.Rect(x, y, w, h)
    paint_brush = pygame.image.load("Paint brush.png")
    paint_brush = pygame.transform.scale(paint_brush, (w, h))
    screen.blit(paint_brush, paint_rect)
    if draw_mode == PAINT:  # If in paint mode, draw a white outline around the icon to indicate it is selected
        pygame.draw.rect(screen, WHITE, paint_rect, 3)


# The other tools uses essentially the same code as the paint tool
def rect_tool(screen, x, y, w, h, draw_mode):
    global rectool_rect

    pygame.draw.rect(screen, MENU_COLOUR, (x - 5, y - 5, w + 10, h + 10))
    rectool_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, RED, rectool_rect)
    if draw_mode == RECT:
        pygame.draw.rect(screen, WHITE, rectool_rect, 3)


def ellipse_tool(screen, x, y, w, h, draw_mode):
    global ellipse_rect

    pygame.draw.rect(screen, MENU_COLOUR, (x - 5, y - 5, w + 10, h + 10))
    ellipse_rect = pygame.Rect(x, y, w, h)
    pygame.draw.ellipse(screen, RED, ellipse_rect)
    if draw_mode == ELLI:
        pygame.draw.rect(screen, WHITE, ellipse_rect, 3)


def brush(screen, brush_size, FOREGROUND, x, y):  # Creates a "brush" so the user will have an idea how big and what colour their brush is
    text_font = pygame.font.SysFont("Times new roman", 18)
    brush_text = text_font.render("Brush size:", True, WHITE)
    brush_rect = brush_text.get_rect()
    brush_rect.topleft = (x, y)
    pygame.draw.rect(screen, MENU_COLOUR, (x-5, y-5, 100, 125))  # Draws a background behind the "brush" so the user can see it increasing and decreasing in size, instead of a smear
    screen.blit(brush_text, brush_rect)
    pygame.draw.circle(screen, FOREGROUND, (x+40, y+70), brush_size)  # Draws a circle to simulate the brush


drag = False
shape_start = [0, 0]  # Creates lists that will be used later
shape_end = [0, 0]
def drawing_shapes(screen, shape_start, shape_end, shape):
    # Draws the shape
    x = shape_start[0]
    y = shape_start[1]
    width = shape_end[0] - shape_start[0]  # x2 - x1
    height = shape_end[1] - shape_start[1]  # y2 - y1
    if shape == "Rect":
        pygame.draw.rect(screen, FOREGROUND, (x, y, width, height))  # If in rect mode, draw a rect
    else:
        pygame.draw.ellipse(screen, FOREGROUND, (x, y, width, height))  # Otherwise we must be in ellipse mode


def draw_menu(screen):  # Function to organize the menu
    draw_canvas(screen)
    mouse_rect = pygame.Rect(0, 0, 0, 0)
    clear(mouse_rect)
    random_colour(mouse_rect)
    save_image(mouse_rect)
    open_image(mouse_rect)
    colour_squares(screen, 70, 48, 10)
    brush(screen, brush_size, FOREGROUND, 710, 475)
    paint_tool(screen, 725, 120, 50, 50, draw_mode)
    rect_tool(screen, 725, 200, 50, 50, draw_mode)
    ellipse_tool(screen, 725, 280, 50, 50, draw_mode)


draw_menu(screen)
# Game Loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Quits if the user closes the window
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            button = event.button
            check_canvas(mx, my)  # The mouse must be on canvas for drawing to happen
            mouse_rect = pygame.Rect(mx, my, 1, 1)  # Creates a rect around the mouse, used in all button interactions

            colourful_buttons(mouse_rect)  # Checks if the user presses any buttons
            clear(mouse_rect)
            random_colour(mouse_rect)
            save_image(mouse_rect)
            open_image(mouse_rect)
            brush(screen, brush_size, FOREGROUND, 710, 475)  # Updates the little brush at the bottom right so users can
            # see their current colour

            check_mode(mouse_rect)  # Updates the draw mode first, so that all of the tool icons will change appearance based on the updated state
            paint_tool(screen, 725, 120, 50, 50, draw_mode)
            rect_tool(screen, 725, 200, 50, 50, draw_mode)
            ellipse_tool(screen, 725, 280, 50, 50, draw_mode)

            if draw_mode != PAINT and on_canvas:  # User wants to create a shape
                shape_start[0] = mx  # Specifies start position
                shape_start[1] = my
                drag = True  # Turns "drag" to true to keep track that the user has started dragging

        if event.type == pygame.MOUSEBUTTONUP:
            mx, my = event.pos
            if draw_mode != PAINT and drag and on_canvas:  # The "drag" is to check if the user is currently dragging and wants to release
                shape_end[0] = mx  # Specifies end position
                shape_end[1] = my
                if draw_mode == RECT:
                    drawing_shapes(screen, shape_start, shape_end, "Rect")  # Draws the rect
                else:
                    drawing_shapes(screen, shape_start, shape_end, "Ellipse")  # Draws the ellipse
            drag = False  # Sets drag to false to prepare for the next shape

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            button = getVal(event.buttons)  # Finds the first pushed down value
            check_canvas(mx, my)

        if event.type == pygame.MOUSEWHEEL:  # If the user is scrolling on their mouse wheel
            if brush_size <= MAX and event.y == 1:  # If the brush is at max size, then don't allow brush size to increase more
                brush_size += 2  # Scrolling up, we should increase brush size
            if brush_size >= MIN and event.y == -1:  # If at min size, don't allow further decrease
                brush_size -= 2  # Scrolling down, decrease brush size
            brush(screen, brush_size, FOREGROUND, 710, 475)  # Updates the brush at the bottom right

    drawing(screen, button)
    display_coordinates(screen)
    pygame.display.flip()
    myClock.tick(100)  # Waits long enough to have 60 fps
quit()
