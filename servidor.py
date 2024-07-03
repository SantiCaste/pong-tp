import socket
import threading
import pygame
import random
import time


WIDTH, HEIGHT = 800, 600

BALL_RADIUS = 10
BALL_SPEED_X = 5  # Velocidad horizontal de la pelota
BALL_SPEED_Y = 5 # Velocidad vertical de la pelota
BALL_ACCELERATION = 0.1
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_LEFT_START_WIDTH = 20
PADDLE_RIGHT_END_WIDTH = WIDTH - PADDLE_LEFT_START_WIDTH - PADDLE_WIDTH
PADDLE_SPEED = 10
MAX_SCORE = 2
CHANGE_DIRECTION = -1
NONE = -1
ZERO = 0
PLAYER_ONE = 0
PLAYER_TWO = 1
LISTEN = 2
PORT = 5555
IP = '0.0.0.0'
PAUSE_TIME = 5
DELAY = 30
BUFFER = 1024
MIDDLE = 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Server:
    def __init__(self):
        return

    def start_game(self): #recibe la conexión e instancia un game
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((IP, PORT))
        server.listen()

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
        self.score = [ZERO, ZERO]
        self.running = True 
        self.conn1 = conn1
        self.conn2 = conn2
        self.threads = []
        self.winner = NONE

    def start_game(self):
        threading.Thread(target=self.update_client, args=(self.conn1, PLAYER_ONE)).start()
        threading.Thread(target=self.update_client, args=(self.conn2, PLAYER_TWO)).start()
        threading.Thread(target=self.update_ball).start()
        threading.Thread(target=self.send_game_state, args=(self.conn1,)).start()
        threading.Thread(target=self.send_game_state, args=(self.conn2,)).start()
        return

    def reset_game(self):
        self.score = [ZERO,ZERO]
        self.ball.reset()
        self.pad_left.reset(PADDLE_LEFT_START_WIDTH)
        self.pad_right.reset(PADDLE_RIGHT_END_WIDTH)
        self.winner= NONE

    def end_game(self):
        self.running = False            
    
    def send_game_state(self, conn):
        while self.running:
            try:
                game_state = f"{self.pad_left.y},{self.pad_right.y},{self.ball.x},{self.ball.y},{self.score[PLAYER_ONE]},{self.score[PLAYER_TWO]},{self.winner}"
                conn.sendall(str.encode(game_state))
                pygame.time.delay(DELAY)  
            except:
                return
    
    def update_ball(self):
        while self.running:
            self.check_collisions()
            self.check_points()
            self.ball.move()
            pygame.time.delay(DELAY)
    
    def check_collisions(self):
        if self.ball.dx < ZERO and self.pad_left.y < self.ball.y < self.pad_left.y + PADDLE_HEIGHT and self.ball.x <= PADDLE_LEFT_START_WIDTH + PADDLE_WIDTH + BALL_RADIUS:
            self.ball.ball_speed_modifier += BALL_ACCELERATION
            self.ball.dx *= CHANGE_DIRECTION * self.ball.ball_speed_modifier
            self.ball.dx = round(self.ball.dx)
        elif self.ball.dx > ZERO and self.pad_right.y < self.ball.y < self.pad_right.y + PADDLE_HEIGHT and self.ball.x >= PADDLE_RIGHT_END_WIDTH - BALL_RADIUS:
            self.ball.ball_speed_modifier += BALL_ACCELERATION
            self.ball.dx *= CHANGE_DIRECTION * self.ball.ball_speed_modifier
            self.ball.dx = round(self.ball.dx)
        
    def check_points(self):
        if self.ball.x < ZERO:
            self.score[PLAYER_TWO] += 1
            if self.score[PLAYER_TWO] == MAX_SCORE:
                self.winner = PLAYER_ONE
                time.sleep(PAUSE_TIME)
                self.reset_game()
            else:
                self.ball.reset()
              
        elif self.ball.x > WIDTH:
            self.score[PLAYER_ONE] += 1
            if self.score[PLAYER_ONE] == MAX_SCORE:
                self.winner = PLAYER_TWO
                time.sleep(PAUSE_TIME)
                self.reset_game()
            else:
                self.ball.reset()
             
               

    def update_client(self, conn, player):
        conn.send(str.encode(f"{player}"))
        while self.running:
            try:
                data = conn.recv(BUFFER).decode()
                if data == 'UP':
                    if player == PLAYER_ONE:
                        self.pad_left.move_up()
                    else:
                        self.pad_right.move_up()
                elif data == 'DOWN':
                    if player == PLAYER_ONE:
                        self.pad_left.move_down()
                    else:
                        self.pad_right.move_down()
                elif data == 'QUIT': 
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
        self.x = WIDTH // MIDDLE
        self.y = HEIGHT // MIDDLE
        self.dx = random.choice([-1, 1]) * BALL_SPEED_X
        self.dy = random.choice([-1, 1]) * BALL_SPEED_Y

    def move(self):
        self.x += self.dx
        self.y += self.dy

        if self.y <= BALL_RADIUS or self.y >= HEIGHT - BALL_RADIUS:
            self.dy *= CHANGE_DIRECTION


class Paddle:
    def __init__(self, x):
        self.reset(x)

    def move_up(self):
        self.y -= PADDLE_SPEED
        if self.y < ZERO:
            self.y = ZERO

    def move_down(self):
        self.y += PADDLE_SPEED
        if self.y > HEIGHT - PADDLE_HEIGHT:
            self.y = HEIGHT - PADDLE_HEIGHT
    
    def reset(self, x):
        self.x = x
        self.y = HEIGHT // MIDDLE - PADDLE_HEIGHT // MIDDLE


def main():
    sv = Server()
    sv.start_game()
    return

if __name__ == "__main__":
    main()
