import socket
import threading
import pygame
import pygame.draw
from pygame._sdl2 import Window
from multiprocessing.connection import Listener,Client

# Dimensiones de la pantalla
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

DISPLAY_PLAYER_1 = (100, 200)
DISPLAY_PLAYER_2 = (WIDTH + 200, 200)
DISPLAY_CENTER = (WIDTH, 200)

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
        self.player = int(self.client.recv(1024).decode())
        self.set_display()
        #esta variable de entorno se usa para indicar en qué posición crear la pantalla
        window = Window.from_display_module()
        window.position = (self.display_x,self.display_y) # Will place the window around the screen 
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong Client")        
        self.screen = screen
        self.set_paddle()
        self.ball = Ball()
        self.running = True
        self.score = [0, 0]
        self.winner = -1

    #esta función sería para settear las pantallas una al lado de la otra, pero no pude hacerlo andar.
    def set_display(self): 
        print(self.player)   
        if self.player == 0:
            self.display_x, self.display_y = DISPLAY_CENTER
        else:
            self.display_x, self.display_y = DISPLAY_CENTER
    
    def set_paddle(self):    
        if self.player == 0:
            self.paddleL = Paddle(20, BLUE)
            self.paddleR = Paddle(WIDTH - 30, RED)
        else:
            self.paddleL = Paddle(20, RED)
            self.paddleR = Paddle(WIDTH - 30, BLUE)
        
    def start_game(self):
        threading.Thread(target=self.receive_data).start()
        self.handle_client()
        return
    
    def receive_data(self):
        while self.running:
            try:
                data = self.client.recv(1024).decode()
                if data:
                    p1_y, p2_y, ball_x, ball_y, score1, score2, self.winner = map(int, data.split(','))
                    self.paddleL.update(p1_y)
                    self.paddleR.update(p2_y)
                    self.ball.update(ball_x, ball_y)
                    self.score = [score1, score2]
            except:
                continue
            
    def handle_key_events_lan(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.client.close()
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]: #si apreta la 'q' se desconecta el client
            self.running = False
            self.client.send(str.encode('QUIT'))
        elif keys[pygame.K_UP]:
            self.client.send(str.encode('UP'))
        elif keys[pygame.K_DOWN]:
            self.client.send(str.encode('DOWN'))


    def handle_client(self):
        while self.running:
            
            #self.handle_key_events()
            self.handle_key_events_lan()
            
            self.screen.fill(BLACK)
            self.ball.draw()
            self.paddleL.draw()
            self.paddleR.draw()

            # Mostrar el marcador
            font = pygame.font.Font(None, 74)
            text = font.render(str(self.score[0]), 1, WHITE)
            self.screen.blit(text, (250, 10))
            text = font.render(str(self.score[1]), 1, WHITE)
            self.screen.blit(text, (510, 10))
            
            # Mostrar el ganador (FALTA EL RESET DEL GUEGO)
            if self.winner != -1:
                #running = False #este es para que no siga procesando los inputs
                font = pygame.font.Font(None, 74)
                if self.winner == 0:
                    winner_color = (RED if self.player == 0 else BLUE)
                    text_to_show="Right player Wins"
                    text_font = font.render(text_to_show, 1, winner_color)
                else:
                    winner_color = (RED if self.player == 1 else BLUE)
                    text_to_show="Left player Wins"
                    text_font = font.render(text_to_show, 1, winner_color)
                
                self.screen.blit(text_font, (250, 250))

            pygame.display.update()
            self.clock.tick(60)    


#####CLASS DEFINITION######################################
class Ball:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

    def update(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), BALL_RADIUS)

class Paddle:
    def __init__(self, x, color):
        self.x = x
        self.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
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

def main_menu(): #TODO - Hacer que esto se cierre una vez que los jugadores apretan Q, sino da errores al salir uno de los jugadores.
    while True:
        screen.fill(BLACK)
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = pygame.font.Font("Tiny5-regular.ttf",100).render("PONG", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(400, 100))

        PLAY__LAN_BUTTON = Button(None, pos=(400, 250), 
                            text_input="JUGAR EN LAN", font=pygame.font.Font("Tiny5-regular.ttf",75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(None, pos=(400, 400), 
                            text_input="QUIT", font=pygame.font.Font("Tiny5-regular.ttf",75), base_color="#d7fcd4", hovering_color="White")

        screen.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY__LAN_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #pygame.sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY__LAN_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play_lan()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                   pygame.quit()
        
        pygame.display.update()


def play_lan():
    loading = True
    intentos = 0
    client = None
    while loading:
        try : 
            screen.fill(BLACK)
            LOADING_TEXT = pygame.font.Font("Tiny5-regular.ttf",100).render("Loading...", True, "#b68f40")
            LOADING_RECT = LOADING_TEXT.get_rect(center=(400, 300))
            screen.blit(LOADING_TEXT, LOADING_RECT)
            pygame.display.update()
            client = Paddle_Client("127.0.0.1", 5555)
            loading = False
        except:
            intentos+=1
            if intentos > 2 :
                screen.fill(BLACK)
                FAIL_TEXT = pygame.font.Font("Tiny5-regular.ttf",25).render("No se pudo establecer la conexion con el servidor", True, "#FF0000")
                FAIL_RECT = FAIL_TEXT.get_rect(center=(400, 300))
                screen.blit(FAIL_TEXT, FAIL_RECT)
                pygame.display.update()
                break
            print("try again")
    if client:         
        screen.fill(BLACK)     
        pygame.display.update()
        client.start_game()
if __name__ == "__main__":
    main_menu()
