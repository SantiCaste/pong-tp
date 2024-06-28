import pygame
import random
import threading


# Dimensiones de la pantalla
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
BALL_SPEED = 1
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 10
FRAMES = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Configuración de la pantalla
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Clase para la pelota
class Ball:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx = random.choice([-1, 1]) * BALL_SPEED
        self.dy = random.choice([-1, 1]) * BALL_SPEED

    def move(self):
        self.x += self.dx
        self.y += self.dy

        # Rebotar en las paredes superior e inferior
        if self.y <= BALL_RADIUS or self.y >= HEIGHT - BALL_RADIUS:
            self.dy *= -1

    def draw(self):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), BALL_RADIUS)

# Clase para las paletas de los jugadores
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

# Función para el thread del jugador 1
def player1_thread():
    global running, events
    movingDown = False
    movingUp = False
    while running:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    movingUp = True
#                    paddle1.move_up()
                elif event.key == pygame.K_s:
                    movingDown = True
#                    paddle1.move_down()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    movingUp = False
#                    paddle1.move_up()
                elif event.key == pygame.K_s:
                    movingDown = False
#                    paddle1.move_down()

        if not (movingUp and movingDown):
            if movingUp:
                paddle1.move_up()
            if movingDown:
                paddle1.move_down()

        clock.tick(FRAMES)

# Función para el thread del jugador 2
def player2_thread():
    global running, events
    movingDown = False
    movingUp = False
    while running:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    movingUp = True
#                    paddle2.move_up()
                elif event.key == pygame.K_DOWN:
                    movingDown = True
#                    paddle2.move_down()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    movingUp = False
                elif event.key == pygame.K_DOWN:
                    movingDown = False

        if not (movingUp and movingDown):
            if movingUp:
                paddle2.move_up()
            if movingDown:
                paddle2.move_down()
    
        clock.tick(FRAMES)


events = pygame.event.get()
clock = pygame.time.Clock()

# Función principal
def main():
    ball = Ball()
    global paddle1, paddle2, running, events, clock
    paddle1 = Paddle(20)
    paddle2 = Paddle(WIDTH - 30)

    # Inicializar y comenzar los threads de los jugadores
    player1 = threading.Thread(target=player1_thread)
    player2 = threading.Thread(target=player2_thread)
    player1.start()
    player2.start()

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False #lo agregué yo
                pygame.quit()
                quit()

        screen.fill(BLACK)

        ball.move()
        ball.draw()
        paddle1.draw()
        paddle2.draw()

        pygame.display.update()
        clock.tick(FRAMES)

if __name__ == "__main__":
    # Inicialización de pygame
    pygame.init()
    running = True
    main()
