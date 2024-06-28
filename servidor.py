import socket
import threading
import pygame
import random

# Dimensiones de la pantalla
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
BALL_SPEED_X = 5  # Velocidad horizontal de la pelota
BALL_SPEED_Y = 5  # Velocidad vertical de la pelota
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Configuración de la pantalla (solo para visualización del servidor)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Server")

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx = random.choice([-1, 1]) * BALL_SPEED_X
        self.dy = random.choice([-1, 1]) * BALL_SPEED_Y

    def move(self):
        self.x += self.dx
        self.y += self.dy

        # Rebotar en las paredes superior e inferior
        if self.y <= BALL_RADIUS or self.y >= HEIGHT - BALL_RADIUS:
            self.dy *= -1

        # Rebotar en las paletas
        if self.dx < 0 and paddle1.y < self.y < paddle1.y + PADDLE_HEIGHT and self.x <= PADDLE_WIDTH + BALL_RADIUS:
            self.dx *= -1
        elif self.dx > 0 and paddle2.y < self.y < paddle2.y + PADDLE_HEIGHT and self.x >= WIDTH - PADDLE_WIDTH - BALL_RADIUS:
            self.dx *= -1

        # Verificar si la pelota ha salido por los lados
        if self.x < 0:
            score[1] += 1
            self.reset()
        elif self.x > WIDTH:
            score[0] += 1
            self.reset()

    def draw(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), BALL_RADIUS)

class Paddle:
    def __init__(self, x):
        self.x = x
        self.y = HEIGHT // 2 - PADDLE_HEIGHT // 2

    def move_up(self):
        self.y -= PADDLE_SPEED
        if self.y < 0:
            self.y = 0

    def move_down(self):
        self.y += PADDLE_SPEED
        if self.y > HEIGHT - PADDLE_HEIGHT:
            self.y = HEIGHT - PADDLE_HEIGHT

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT))

def client_thread(conn, player):
    global running, paddle1, paddle2, ball, score
    conn.send(str.encode(f"{player}"))
    while running:
        try:
            data = conn.recv(1024).decode()
            if data == 'UP':
                if player == 0:
                    paddle1.move_up()
                else:
                    paddle2.move_up()
            elif data == 'DOWN':
                if player == 0:
                    paddle1.move_down()
                else:
                    paddle2.move_down()

            game_state = f"{paddle1.y},{paddle2.y},{ball.x},{ball.y},{score[0]},{score[1]}"
            conn.sendall(str.encode(game_state))
        except:
            break
    conn.close()

def ball_thread():
    global running, ball
    while running:
        ball.move()
        pygame.time.delay(30)  # Ajustar el retraso para suavizar el movimiento de la pelota

def main():
    global running, paddle1, paddle2, ball, score
    ball = Ball()
    paddle1 = Paddle(20)
    paddle2 = Paddle(WIDTH - 30)
    score = [0, 0]
    running = True

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))
    server.listen(2)

    print("Esperando conexiones...")
    conn1, addr1 = server.accept()
    print(f"Jugador 1 conectado: {addr1}")
    conn2, addr2 = server.accept()
    print(f"Jugador 2 conectado: {addr2}")

    threading.Thread(target=client_thread, args=(conn1, 0)).start()
    threading.Thread(target=client_thread, args=(conn2, 1)).start()
    threading.Thread(target=ball_thread).start()

    clock = pygame.time.Clock()
    while running:
        screen.fill(BLACK)
        ball.draw()
        paddle1.draw()
        paddle2.draw()

        # Mostrar el marcador
        font = pygame.font.Font(None, 74)
        text = font.render(str(score[0]), 1, WHITE)
        screen.blit(text, (250, 10))
        text = font.render(str(score[1]), 1, WHITE)
        screen.blit(text, (510, 10))

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
