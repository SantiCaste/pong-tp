import socket
import threading
import pygame
from random import randint


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

def handle_client(client, paddle_l, paddle_r, ball):
    global running, score, winner

    def receive_data():
        global running, score, winner
        while running:
            try:
                data = client.recv(1024).decode()
                if data:
                    p1_y, p2_y, ball_x, ball_y, score1, score2, winner = map(int, data.split(','))
                    paddle_l.update(p1_y)
                    paddle_r.update(p2_y)
                    ball.update(ball_x, ball_y)

                    score = [score1, score2]
            except:
                break

    threading.Thread(target=receive_data).start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                client.close()
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]: #si apreta la 'q' se desconecta el client
            running = False
            client.send(str.encode('QUIT'))

        if keys[pygame.K_UP]:
            client.send(str.encode('UP'))
        elif keys[pygame.K_DOWN]:
            client.send(str.encode('DOWN'))

        screen.fill(BLACK)
        ball.draw()
        paddle_l.draw()
        paddle_r.draw()

        # Mostrar el marcador
        font = pygame.font.Font(None, 74)
        text = font.render(str(score[0]), 1, WHITE)
        screen.blit(text, (250, 10))
        text = font.render(str(score[1]), 1, WHITE)
        screen.blit(text, (510, 10))

        # Mostrar el ganador (FALTA EL RESET DEL GUEGO)
        if winner != -1:
            #running = False #este es para que no siga procesando los inputs
            font = pygame.font.Font(None, 74)
            if winner == 0:
                text = font.render("Left player Wins", 1, BLUE)
            else:
                text = font.render("Right player Wins", 1, RED)
            
            screen.blit(text, (250, 250))

        pygame.display.update()
        clock.tick(60)

def main():
    global running, clock, score
    clock = pygame.time.Clock()
    score = [0, 0]

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 5555))

    player = int(client.recv(1024).decode())
    print(f"player vale: {player}")

    ball = Ball()

    if player == 0:
        paddleL = Paddle(20, BLUE)
        paddleR = Paddle(WIDTH - 30, RED)
    else:
        paddleL = Paddle(20, RED)
        paddleR = Paddle(WIDTH - 30, BLUE)
    
    running = True

    threading.Thread(target=handle_client, args=(client, paddleL, paddleR, ball)).start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                client.close()
                pygame.quit()
                quit()

if __name__ == "__main__":
    main()
