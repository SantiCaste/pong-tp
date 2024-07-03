import socket
import threading
import pygame
import random
import time

# Dimensiones de la pantalla
WIDTH, HEIGHT = 800, 600

#parámetros de los elementos
BALL_RADIUS = 10
BALL_SPEED_X = 5  # Velocidad horizontal de la pelota
BALL_SPEED_Y = 5 # Velocidad vertical de la pelota
BALL_ACCELERATION = 0.1
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_LEFT_START_WIDTH = 20
PADDLE_RIGHT_END_WIDTH = WIDTH - PADDLE_LEFT_START_WIDTH - PADDLE_WIDTH
PADDLE_SPEED = 10
MAX_SCORE = 2

PAUSE_TIME = 5

#colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Server:
    def __init__(self):
        #self.start_game()
        return

    def start_game(self): #recibe la conexión e instancia un game
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 5555))
        server.listen(2)

        print("Esperando conexiones...")
        conn1, addr1 = server.accept()
        print(f"Jugador 1 conectado: {addr1}")
        conn2, addr2 = server.accept()
        print(f"Jugador 2 conectado: {addr2}")


        self.game = Game(conn1, conn2)
        self.game.start_game()

        return

class Game: #game se instancia con los threads de los jugadores que le voy a pasar
    global games

    def __init__(self, conn1, conn2):
        self.ball = Ball()
        self.pad_left = Paddle(PADDLE_LEFT_START_WIDTH)
        self.pad_right = Paddle(PADDLE_RIGHT_END_WIDTH)
        self.score = [0,0]
        self.running = True #capaz no hace falta
        self.conn1 = conn1
        self.conn2 = conn2
        self.threads = []
        self.winner = -1

    def start_game(self):
        threading.Thread(target=self.update_client, args=(self.conn1, 0)).start()
        threading.Thread(target=self.update_client, args=(self.conn2, 1)).start()
        threading.Thread(target=self.update_ball).start()
        threading.Thread(target=self.send_game_state, args=(self.conn1,)).start()
        threading.Thread(target=self.send_game_state, args=(self.conn2,)).start()
        return

    def reset_game(self):
        self.score = [0,0]
        self.ball.reset()
        self.pad_left.reset(PADDLE_LEFT_START_WIDTH)
        self.pad_right.reset(PADDLE_RIGHT_END_WIDTH)
        self.winner=-1

    def end_game(self):
        self.running = False            
    
    def send_game_state(self, conn):
        while self.running:
            try:
                game_state = f"{self.pad_left.y},{self.pad_right.y},{self.ball.x},{self.ball.y},{self.score[0]},{self.score[1]},{self.winner}"
                #print(game_state)
                conn.sendall(str.encode(game_state))
                pygame.time.delay(30)  # Ajustar el retraso para la frecuencia de actualización
            except:
                return
    
    def update_ball(self):
        while self.running:
            self.check_collisions()
            self.check_points()
            self.ball.move()
            pygame.time.delay(30)
    
    def check_collisions(self):
        # Rebotar en las paletas
        if self.ball.dx < 0 and self.pad_left.y < self.ball.y < self.pad_left.y + PADDLE_HEIGHT and self.ball.x <= PADDLE_LEFT_START_WIDTH + PADDLE_WIDTH + BALL_RADIUS:
            self.ball.ball_speed_modifier += BALL_ACCELERATION
            self.ball.dx *= -1 * self.ball.ball_speed_modifier
            self.ball.dx = round(self.ball.dx)
        elif self.ball.dx > 0 and self.pad_right.y < self.ball.y < self.pad_right.y + PADDLE_HEIGHT and self.ball.x >= PADDLE_RIGHT_END_WIDTH - BALL_RADIUS:
            self.ball.ball_speed_modifier += BALL_ACCELERATION
            self.ball.dx *= -1 * self.ball.ball_speed_modifier
            self.ball.dx = round(self.ball.dx)
        
    def check_points(self):
        # Verificar si la pelota ha salido por los lados
        if self.ball.x < 0:
            self.score[1] += 1
            if self.score[1] == MAX_SCORE:
                self.winner = 0
                time.sleep(PAUSE_TIME)
                self.reset_game()
            else:
                self.ball.reset()
        elif self.ball.x > WIDTH:
            self.score[0] += 1
            if self.score[0] == MAX_SCORE:
                self.winner = 1
                time.sleep(PAUSE_TIME)
                self.reset_game()
            else:
                self.ball.reset()

    def update_client(self, conn, player):
        conn.send(str.encode(f"{player}"))
        while self.running:
            try:
                data = conn.recv(1024).decode()
                if data == 'UP':
                    if player == 0:
                        self.pad_left.move_up()
                    else:
                        self.pad_right.move_up()
                elif data == 'DOWN':
                    if player == 0:
                        self.pad_left.move_down()
                    else:
                        self.pad_right.move_down()
                elif data == 'QUIT': #AJUSTAR ESTO PORQUE SI SALE UN CLIENTE EL OTRO TAMBIEN. Esto lo tiene que hacer el game
                    self.end_game()
                    break
            except:
                self.end_game()
                break        
        return


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.ball_speed_modifier = float(1)
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



class Paddle:
    def __init__(self, x):
        self.reset(x)

    def move_up(self):
        self.y -= PADDLE_SPEED
        if self.y < 0:
            self.y = 0

    def move_down(self):
        self.y += PADDLE_SPEED
        if self.y > HEIGHT - PADDLE_HEIGHT:
            self.y = HEIGHT - PADDLE_HEIGHT
    
    def reset(self, x):
        self.x = x
        self.y = HEIGHT // 2 - PADDLE_HEIGHT // 2


def main(): #servidor va instanciando partidas.
    sv = Server()
    sv.start_game()
    return

if __name__ == "__main__":
    main()
