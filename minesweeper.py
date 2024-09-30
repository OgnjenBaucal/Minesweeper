from constants import *
import pygame
import time
import random

class Block:
    def __init__(self):
        self.value = 0
        self.visible = False
        self.flagged = False

screen = None
best_record = None
flags = 0
start_timer = None
board = []

flagged_image = pygame.image.load(r'Images\flagged.png')
hidden_image = pygame.image.load(r'Images\hidden.png')
mine_image = pygame.image.load(r'Images\mine.png')
number_images = [ pygame.image.load(r'Images\zero.png'), 
                  pygame.image.load(r'Images\one.png'), 
                  pygame.image.load(r'Images\two.png'), 
                  pygame.image.load(r'Images\three.png'), 
                  pygame.image.load(r'Images\four.png'), 
                  pygame.image.load(r'Images\five.png'), 
                  pygame.image.load(r'Images\six.png'), 
                  pygame.image.load(r'Images\seven.png'), 
                  pygame.image.load(r'Images\eight.png')]


def write_best_record():
    with open("record.txt", 'w') as file:
        file.write(str(best_record))

def read_best_record():
    global best_record
    with open("record.txt", 'r') as file:
        best_record = float(file.readline())

def validIndex(i, j):
    return i >= 0 and i < DIMENSION and j >= 0 and j < DIMENSION

def generate():
    global board
    list = []
    board = []
    for i in range(0, DIMENSION):
        dummy = []
        for j in range(0, DIMENSION):
            list.append((i, j))
            dummy.append(Block())
        board.append(dummy)

    for _ in range(0, MAX_MINES):
        index = random.randint(0, len(list) - 1)
        i, j = list.pop(index)
        board[i][j].value = -1
        for k in range(-1, 2):
            for l in range(-1, 2):
                if k == 0 and l == 0:
                    continue
                
                if validIndex(i + k, j + l) and board[i+k][j+l].value != -1:
                    board[i+k][j+l].value += 1

def reveal_mines():
    for i in range(0, DIMENSION):
        for j in range(0, DIMENSION):
            if board[i][j].value == -1:
                board[i][j].visible = True

def over():
    global board
    revealed = 0
    for i in range(0, DIMENSION):
        for j in range(0, DIMENSION):
            if board[i][j].visible:
                revealed += 1
                if board[i][j].value == -1:
                    return 'lost'
    
    if revealed == DIMENSION*DIMENSION - MAX_MINES:
        return 'won'
    
    return None

def draw():
    for i in range(0, DIMENSION):
        for j in range(0, DIMENSION):
            draw_block(i, j)

def draw_block(i, j):
    global board, screen
    if validIndex(i, j):
        offset = HEIGHT - WIDTH
        if board[i][j].visible:
            if board[i][j].value == -1:
                screen.blit(mine_image, (j*SIZE, offset + i*SIZE))
            else:
                screen.blit(number_images[board[i][j].value], (j*SIZE, offset + i*SIZE))
        elif board[i][j].flagged:
            screen.blit(flagged_image, (j*SIZE, offset + i*SIZE))
        else:
            screen.blit(hidden_image, (j*SIZE, offset + i*SIZE))

def reveal(i, j):
    global board, flags

    if not validIndex(i, j) or board[i][j].visible:
        return

    board[i][j].visible = True
    if board[i][j].flagged:
        board[i][j].flagged = False
        flags -= 1
    
    if board[i][j].value == 0:
        for k in range(-1, 2):
            for l in range(-1, 2):
                if k == 0 and l == 0:
                    continue
                reveal(i+k, j+l)

def game():
    global board, start_timer, flags, best_record
    generate()
    flags = 0

    # Display
    screen.fill(BACKGROUND_COLOR)
    draw()
    font = pygame.font.SysFont("timenewroman", 80)
    text = font.render(f"Flags: {flags}/{MAX_FLAGS}", 1, 'gray')
    screen.blit(text, (10, 10))
    pygame.display.flip()

    start_timer = time.time()
    state = over()

    while state == None:
        mouse_position = None
        click = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                if mouse_position[1] < HEIGHT - WIDTH:
                    continue
                if pygame.mouse.get_pressed()[0]: # Left click
                    click = 'left'
                elif pygame.mouse.get_pressed()[2]: # Right click
                    click = 'right'

        if click != None:
            j, i = mouse_position
            i = int((i - HEIGHT + WIDTH) / SIZE)
            j = int(j / SIZE)
    
            # Update
            if not board[i][j].visible:
                if click == 'left':
                    if not board[i][j].flagged:
                        reveal(i, j)
                else: # click == 'right'
                    if board[i][j].flagged:
                        board[i][j].flagged = False
                        flags -= 1
                    elif flags < MAX_FLAGS: # not board[i][j].flagged
                        board[i][j].flagged = True
                        flags += 1

                state = over()

            # Display
            screen.fill(BACKGROUND_COLOR)
            draw()
            text = font.render(f"Flags: {flags}/{MAX_FLAGS}", 1, 'gray')
            screen.blit(text, (10, 10))
            pygame.display.flip()

    if state == 'won':
        record = round(time.time() - start_timer, 3)
        if record < best_record:
            best_record = record
            write_best_record()
        
        return post_game_screen(state, record)
    else:
        reveal_mines()

        # Display
        screen.fill(BACKGROUND_COLOR)
        draw()
        text = font.render(f"Flags: {flags}/{MAX_FLAGS}", 1, 'gray')
        screen.blit(text, (10, 10))
        pygame.display.flip()

        # Wait
        time.sleep(1)
        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    run = False
                    break

        return post_game_screen(state, None)

def post_game_screen(state, record):
    # Display
    screen.fill(BACKGROUND_COLOR)

    font1 = pygame.font.SysFont("timenewroman", 110)
    font2 = pygame.font.SysFont("timesnewroman", 60)
    font3 = pygame.font.SysFont("timesnewroman", 60)

    title = font1.render("Game lost", 1, 'gray')
    if state == 'won':
        title = font1.render("Game won", 1, 'gray')

    score = font2.render("Score: " + str(record) + "s", 1, 'gray')
    button = font3.render("Restart", 1, 'white')

    screen.blit(title, (WIDTH/2 - title.get_width()/2, 150))
    if state == 'won':
        screen.blit(score, (WIDTH/2 - score.get_width()/2, 300))
    screen.blit(button, (WIDTH/2 - button.get_width()/2, 500))
    
    rect = pygame.Rect(WIDTH/2 - button.get_width()/2 - 40, 490, button.get_width() + 80, 90)
    pygame.draw.rect(screen, 'white', rect, 1)

    pygame.display.flip()

    mouse_position = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_position = pygame.mouse.get_pos()
        
        if mouse_position != None:
            x, y = mouse_position
            if x > rect.left and x < rect.left + rect.width and y > rect.top and y < rect.top + rect.height:
                return True

def menu():
    # Display
    screen.fill(BACKGROUND_COLOR)

    font1 = pygame.font.SysFont("timenewroman", 110)
    title = font1.render("Minesweeper", 1, 'gray')
    screen.blit(title, (WIDTH/2 - title.get_width()/2, 150))

    font2 = pygame.font.SysFont("timesnewroman", 60)
    text = font2.render("Record: " + str(best_record) + "s", 1, 'gray')
    screen.blit(text, (WIDTH/2 - text.get_width()/2, 300))

    font3 = pygame.font.SysFont("timesnewroman", 60)
    button = font3.render("Start", 1, 'white')
    screen.blit(button, (WIDTH/2 - button.get_width()/2, 500))

    rect = pygame.Rect(WIDTH/2 - button.get_width()/2 - 40, 490, button.get_width() + 80, 90)
    pygame.draw.rect(screen, 'white', rect, 1)

    pygame.display.flip()

    mouse_position = None
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_position = pygame.mouse.get_pos()
        
        if mouse_position != None:
            x, y = mouse_position
            if x > rect.left and x < rect.left + rect.width and y > rect.top and y < rect.top + rect.height:
                return game()

def main():
    global screen, font, best_record

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Minesweeper")
    icon = pygame.image.load('icon.ico')
    pygame.display.set_icon(icon)
    pygame.font.init()
    
    read_best_record()

    run = True
    while run:
        run = menu()
    
    pygame.quit()

main()
