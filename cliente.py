import socket
import threading
import pygame
import pygame.draw

# Dimensiones de la pantalla
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100 #REVISAR LAS COLISIONES QUE ESTAN MEDIO PERUANOIDES
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


# Configuración de la pantalla

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

        #self.set_display()
        #esta variable de entorno se usa para indicar en qué posición crear la pantalla
        #os.environ['SDL_VIDEO_WINDOW_POS'] = str(self.display_x) + "," + str(self.display_y)
        #screen = pygame.display.set_mode((WIDTH, HEIGHT))
        #pygame.display.set_caption("Pong Client")        
        #screen = self.screen
        self.screen= screen
        self.set_paddle()
        self.ball = Ball()
        self.running = True
        self.score = [0, 0]
        self.winner = -1
    
    """esta función sería para settear las pantallas una al lado de la otra, pero no pude hacerlo andar.
    def set_display(self):    
        if self.player == 0:
            self.display_x = 100
            self.display_y = 200
        else:
            self.display_x = WIDTH + 200
            self.display_y = 200        
    """
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
                break
            
    def handle_key_events(self):
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
        if keys[pygame.K_UP]:
            self.client.send(str.encode('UP'))
        elif keys[pygame.K_DOWN]:
            self.client.send(str.encode('DOWN'))
                    
    def handle_client(self):
        while self.running:
            
            self.handle_key_events()
            
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


def main():
    client = Paddle_Client("127.0.0.1", 5555)
    client.start_game() 

if __name__ == "__main__":
    main()
