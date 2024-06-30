import socket
import threading
import pygame

# Dimensiones de la pantalla
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

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
    def __init__(self, x):
        self.x = x
        self.y = HEIGHT // 2 - PADDLE_HEIGHT // 2

    def update(self, y):
        self.y = y

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT))

def handle_client(client, player, paddle, opponent_paddle, ball):
    global running, score

    def receive_data():
        global running, score
        while running:
            try:
                data = client.recv(1024).decode()
                if data:
                    p1_y, p2_y, ball_x, ball_y, score1, score2 = map(int, data.split(','))
                    if player == 0:
                        paddle.update(p1_y)
                        opponent_paddle.update(p2_y)
                    else:
                        paddle.update(p2_y)
                        opponent_paddle.update(p1_y)
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
        if keys[pygame.K_UP]:
            client.send(str.encode('UP'))
        elif keys[pygame.K_DOWN]:
            client.send(str.encode('DOWN'))

        screen.fill(BLACK)
        ball.draw()
        paddle.draw()
        opponent_paddle.draw()

        # Mostrar el marcador
        font = pygame.font.Font(None, 74)
        text = font.render(str(score[0]), 1, WHITE)
        screen.blit(text, (250, 10))
        text = font.render(str(score[1]), 1, WHITE)
        screen.blit(text, (510, 10))

        pygame.display.update()
        clock.tick(60)

def main():
    global running, clock, score
    clock = pygame.time.Clock()
    score = [0, 0]

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 5555))

    player = int(client.recv(1024).decode())


    ball = Ball()
    paddle1 = Paddle(20)
    paddle2 = Paddle(WIDTH - 30)

    running = True

    threading.Thread(target=handle_client, args=(client, player, paddle1, paddle2, ball)).start()


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                client.close()
                pygame.quit()
                quit()

if __name__ == "__main__":
    main()
