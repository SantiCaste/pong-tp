import socket
import threading
import pygame
import pygame.draw
from pygame._sdl2 import Window
import sys

WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BUFFER = 1024
XL=20
XR=30
NONE = -1
ZERO = 0
PLAYER_ONE = 0
PLAYER_TWO = 1
PORT = 5555
IP = "127.0.0.1"
BUFFER = 1024
MIDDLE = 2
DISPLAY_PLAYER_1 = (100, 200)
DISPLAY_PLAYER_2 = (WIDTH + 200, 200)
DISPLAY_CENTER = (WIDTH, 200)
CLOCK = 60
SIZE_FONT = 74
CORDXL = 250
CORDY= 10
CORDXR = 510
FAIL = 2
WINNER_POS = 250
MENU_TEXT_SIZE = 100
MENU_TEXT_X=400
MENU_TEXT_Y = 100
PLAY_LAN_BUTTON_X = 400
PLAY_LAN_BUTTON_Y = 250
FONT_SIZE = 75
QUIT_BUTTON_X = 400
QUIT_BUTTON_Y = 400
LOADING_TEXT_FONT_SIZE = 100
LOADING_TEXT_X = 400
LOADING_TEXT_Y = 300
FAIL_TEXT_X = 400
FAIL_TEXT_Y = 300
FAIL_TEXT_FONT_SIZE = 25

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Client")

class Paddle_Client:
    def __init__(self, ip, port):
        global screen
        self.clock=pygame.time.Clock()
        self.ip = ip
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.ip, self.port))
        self.player = int(self.client.recv(BUFFER).decode())
        self.set_display()
        window = Window.from_display_module()
        window.position = (self.display_x,self.display_y) 
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong Client")        
        self.screen = screen
        self.set_paddle()
        self.ball = Ball()
        self.running = True
        self.score = [ZERO, ZERO]
        self.winner = NONE

    def set_display(self): 
        print(self.player)   
        if self.player == PLAYER_ONE:
            self.display_x, self.display_y = DISPLAY_CENTER
        else:
            self.display_x, self.display_y = DISPLAY_CENTER
    
    def set_paddle(self):    
        if self.player == PLAYER_ONE:
            self.paddleL = Paddle(XL, BLUE)
            self.paddleR = Paddle(WIDTH - XR, RED)
        else:
            self.paddleL = Paddle(XL, RED)
            self.paddleR = Paddle(WIDTH - XR, BLUE)
        
    def start_game(self):
        threading.Thread(target=self.receive_data).start()
        self.handle_client()
        return
    
    def receive_data(self):
        while self.running:
            try:
                data = self.client.recv(BUFFER).decode()
                if data:
                    p1_y, p2_y, ball_x, ball_y, score1, score2, self.winner = map(int, data.split(','))
                    self.paddleL.update(p1_y)
                    self.paddleR.update(p2_y)
                    self.ball.update(ball_x, ball_y)
                    self.score = [score1, score2]
            except:
                continue
            
    def handle_key_events_lan(self):
        self.check_quit_event()
        self.handle_keyboard_input()

    def check_quit_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

    def handle_keyboard_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            self.send_quit_signal()
        elif keys[pygame.K_UP]:
            self.send_move_signal('UP')
        elif keys[pygame.K_DOWN]:
            self.send_move_signal('DOWN')

    def quit_game(self):
        self.running = False
        self.client.close()
        pygame.quit()
        quit()

    def send_quit_signal(self):
        self.running = False
        self.client.send(str.encode('QUIT'))

    def send_move_signal(self, direction):
        self.client.send(str.encode(direction))

    def handle_client(self):
        while self.running:
            self.handle_key_events_lan()
            self.update_screen()
            pygame.display.update()
            self.clock.tick(CLOCK)

    def update_screen(self):
        self.screen.fill(BLACK)
        self.draw_objects()
        self.show_score()
        self.show_winner()

    def draw_objects(self):
        self.ball.draw()
        self.paddleL.draw()
        self.paddleR.draw()

    def show_score(self):
       
        font = pygame.font.Font(None, SIZE_FONT)
        score_left = font.render(str(self.score[0]), True, WHITE)
        score_right = font.render(str(self.score[1]), True, WHITE)
        self.screen.blit(score_left, (CORDXL, CORDY))
        self.screen.blit(score_right, (CORDXR, CORDY))

    def show_winner(self):
        if self.winner != NONE:
            font = pygame.font.Font(None, SIZE_FONT)
            if self.winner == PLAYER_ONE:
                winner_color = (RED if self.player == PLAYER_ONE else BLUE)
                text_to_show = "Right player Wins"
            else:
                winner_color = (RED if self.player == PLAYER_TWO else BLUE)
                text_to_show = "Left player Wins"
            
            winner_text = font.render(text_to_show, True, winner_color)
            self.screen.blit(winner_text, (WINNER_POS, WINNER_POS))

class Ball:
    def __init__(self):
        self.x = WIDTH // MIDDLE
        self.y = HEIGHT // MIDDLE

    def update(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), BALL_RADIUS)

class Paddle:
    def __init__(self, x, color):
        self.x = x
        self.y = HEIGHT // MIDDLE - PADDLE_HEIGHT // MIDDLE
        self.color = color

    def update(self, y):
        self.y = y

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT))

class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

def draw_menu_text():
   
    MENU_TEXT = pygame.font.Font("Tiny5-regular.ttf", MENU_TEXT_SIZE).render("PONG", True, "#b68f40")
    MENU_RECT = MENU_TEXT.get_rect(center=(MENU_TEXT_X, MENU_TEXT_Y))
    screen.blit(MENU_TEXT, MENU_RECT)

def create_buttons():
   
    PLAY__LAN_BUTTON = Button(None, pos=(PLAY_LAN_BUTTON_X, PLAY_LAN_BUTTON_Y), 
                        text_input="JUGAR EN LAN", font=pygame.font.Font("Tiny5-regular.ttf", FONT_SIZE), base_color="#d7fcd4", hovering_color="White")
    QUIT_BUTTON = Button(None, pos=(QUIT_BUTTON_X, QUIT_BUTTON_Y), 
                        text_input="QUIT", font=pygame.font.Font("Tiny5-regular.ttf", FONT_SIZE), base_color="#d7fcd4", hovering_color="White")
    return [PLAY__LAN_BUTTON, QUIT_BUTTON]

def update_buttons(buttons, mouse_pos):
    for button in buttons:
        button.changeColor(mouse_pos)
        button.update(screen)

def handle_events(buttons, mouse_pos):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if buttons[0].checkForInput(mouse_pos):
                play_lan()
            if buttons[1].checkForInput(mouse_pos):
                pygame.quit()
                sys.exit()

def main_menu(): 
    while True:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

        draw_menu_text()
        buttons = create_buttons()
        update_buttons(buttons, mouse_pos)
        handle_events(buttons, mouse_pos)
        
        pygame.display.update()


def show_loading_screen():
    screen.fill(BLACK)
    
    LOADING_TEXT = pygame.font.Font("Tiny5-regular.ttf", LOADING_TEXT_FONT_SIZE).render("Loading...", True, "#b68f40")
    LOADING_RECT = LOADING_TEXT.get_rect(center=(LOADING_TEXT_X, LOADING_TEXT_Y))
    screen.blit(LOADING_TEXT, LOADING_RECT)
    pygame.display.update()

def show_fail_screen():
    screen.fill(BLACK)
    
    FAIL_TEXT = pygame.font.Font("Tiny5-regular.ttf", FAIL_TEXT_FONT_SIZE).render("No se pudo establecer la conexion con el servidor", True, "#FF0000")
    FAIL_RECT = FAIL_TEXT.get_rect(center=(FAIL_TEXT_X, FAIL_TEXT_Y))
    screen.blit(FAIL_TEXT, FAIL_RECT)
    pygame.display.update()

def try_connect():
    return Paddle_Client(IP, PORT)

def play_lan():
    loading = True
    intentos = 0
    client = None

    while loading:
        try:
            show_loading_screen()
            client = try_connect()
            loading = False
        except:
            intentos += 1
            if intentos > FAIL:
                show_fail_screen()
                break
            print("try again")

    if client:
        screen.fill(BLACK)
        pygame.display.update()
        client.start_game()


if __name__ == "__main__":
    main_menu()
