import pygame
import sys
import math
import numpy as np
import time
import socket
import pygame.gfxdraw

LINES = 15

def draw_piece(screen, x, y, color):
    pygame.gfxdraw.aacircle(screen, x, y, 16, color)
    pygame.gfxdraw.filled_circle(screen, x, y, 16, color)

'''画游戏界面'''
def draw_screen(screen, countdown, remain_timeout, round_this, piece_color):
    screen.fill((240,238,214))
    pygame.draw.rect(screen, (224,191,148), (65,50,600,600),0)
    for i in range(LINES):
        pygame.draw.line(screen, (0,0,0), (85,70+i*(560/14)), (85+560,70+i*(560/14)),1)
    for i in range(LINES):
        pygame.draw.line(screen, (0,0,0), (85+i*(560/14),70), (85+i*(560/14),70+560),1)
    for i in (3,7,11):
        for j in (3,7,11):
            pygame.gfxdraw.aacircle(screen, 85+i*(560//14), 70+j*(560//14), 3, (0,0,0))
            pygame.gfxdraw.filled_circle(screen, 85+i*(560//14), 70+j*(560//14), 3, (0,0,0))
    font =  pygame.font.SysFont("SimHei", 35)
    round_black = font.render("黑方行棋", True, (0,0,0))
    round_white = font.render("白方行棋", True, (0,0,0))
    countdown_text = font.render("倒计时", True, (0,0,0))
    countdown_time = font.render('00:'+f'{countdown}'.rjust(2,'0'), True, (229,20,0))
    timeout = font.render(f'{remain_timeout}次', True, (0,0,0))
    piece_white = font.render("我方执白", True, (0,0,0))
    piece_black = font.render("我方执黑", True, (0,0,0))
    screen.blit(countdown_text, (665+65,300))
    screen.blit(countdown_time, (665+73,350))
    screen.blit(timeout, (665+92,400))
    if round_this == 1:
        screen.blit(round_black, (665+48,120))
    elif round_this == 2:
        screen.blit(round_white, (665+48,120))
    if piece_color == 1:
        screen.blit(piece_black, (665+48,550))
        draw_piece(screen, 665+118, 611, (0,0,0))
    elif piece_color == 2:
        screen.blit(piece_white, (665+48,550))
        draw_piece(screen, 665+118, 611, (255,255,255))

def get_pos(position):
    x = round((position[0] - 85)/(560/14))
    y = round((position[1] - 70)/(560/14))
    return x,y

'''获胜检测'''
def win_check(position, board, piece_color):
    direction = [(1,0),(0,1),(1,1),(1,-1)]
    win = False
    for dire in direction:
        count = 1
        for i in range(1,5):
            x = position[0] + i*dire[0]
            y = position[1] + i*dire[1]
            if x < LINES and y < LINES and board[y][x] == piece_color:
                count += 1
            else:
                break
        for i in range(1,5):
            x = position[0] - i*dire[0]
            y = position[1] - i*dire[1]
            if x > 0 and y > 0 and board[y][x] == piece_color:
                count += 1
            else:
                break
        if count >= 5:
            win = True
    return win

def main(screen, sk):
    board = np.zeros((LINES,LINES), dtype = int)
    winfont = pygame.font.SysFont("SimHei", 70)
    start_time = time.time()
    remain_timeout = 3
    winer = 0
    round_this = 1
    piece_color = 2
    rival_piece_color = 1
    imready, rivalready = False, False
    again = False
    while not again:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and round_this == 2 and winer == 0: #落子
                if (event.pos[0]>=65 and event.pos[0]<=665) and (event.pos[1]>=50 and event.pos[1]<=650): 
                    pos = get_pos(event.pos)
                    if board[pos[1]][pos[0]] == 0:
                        sk.send(f"{pos[0]},{pos[1]}".encode('utf-8'))
                        board[pos[1]][pos[0]] = piece_color
                        start_time = time.time()
                        if win_check(pos, board, piece_color):
                            winer = piece_color
                        round_this = rival_piece_color
            if winer != 0 and event.type == pygame.KEYDOWN and event.key == 13:
                sk.send('1'.encode('utf-8'))
                imready = True
        try:
            if not winer:
                msg = sk.recv(1024)
                if msg:
                    pos = msg.decode('utf-8').split(',') #对方落子
                    pos = list(map(int,pos))
                    board[pos[1]][pos[0]] = rival_piece_color
                    start_time = time.time()
                    if win_check(pos, board, rival_piece_color):
                        winer = rival_piece_color
                    round_this = piece_color
        except BlockingIOError:
            pass
        try:
            if winer != 0 and sk.recv(1024):
                rivalready = True
        except BlockingIOError:
            pass
        if imready and rivalready: #再来一局
            again = True
        if winer == 0:
            countdown = math.ceil(30-(time.time()-start_time)) #倒计时
        if countdown == 0:
            if remain_timeout > 0:
                remain_timeout -= 1
                start_time = time.time()
            else:
                if round_this == piece_color:
                    winer = rival_piece_color
                elif round_this == rival_piece_color:
                    winer = piece_color
        draw_screen(screen, countdown, remain_timeout, round_this, piece_color)
        for i,row in enumerate(board): #画棋子
            for j,point in enumerate(row):
                if point == 1:
                    draw_piece(screen, 85+j*(560//14), 70+i*(560//14), (0,0,0))
                elif point == 2:
                    draw_piece(screen, 85+j*(560//14), 70+i*(560//14), (255,255,255))
        if winer == 1:
            win_black = winfont.render("黑方获胜", True, (229,20,0))
            screen.blit(win_black, (225,320))
        elif winer == 2:
            win_white = winfont.render("白方获胜", True, (229,20,0))
            screen.blit(win_white, (225,320))
        pygame.display.flip()

'''等待连接界面'''
def waiting_screen(screen, sk):
    screen.fill((240,238,214))
    connected = False
    address = None
    remote_port = None
    inputing = 0
    wating_text = Text("连接服务端", None, 210, True)
    ip_text = Text(f"目标IP:", 255, 350, False)
    port_text = Text(f'目标端口:', 255, 400, False)
    ip_input = InputBox(150+ip_text.width, ip_text.height, 255+ip_text.width, 350)
    port_input = InputBox(82+port_text.width, port_text.height, 255+port_text.width, 400)
    conn_button = Button("连接", (0,0,0), 500)
    while not connected:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #选中输入框
                if ip_input.check_click(event.pos):
                    inputing = 1
                elif port_input.check_click(event.pos):
                    inputing = 2
                elif conn_button.check_click(event.pos):
                    if ip_input.text != '' and port_input.text != '':
                        try:
                            sk.connect((ip_input.text,int(port_input.text)))
                        except BlockingIOError:
                            connected = True
            elif event.type == pygame.KEYDOWN: #输入内容
                if inputing == 1:
                    ip_input.safe_key_down(event)
                elif inputing == 2:
                    port_input.safe_key_down(event)
        if conn_button.check_click(pygame.mouse.get_pos()):
            conn_button = Button("连接", (229,20,0), 500)
        else:
            conn_button = Button("连接", (0,0,0), 500)
        wating_text.display(screen)
        ip_text.display(screen)
        port_text.display(screen)
        ip_input.draw(screen)
        port_input.draw(screen)
        conn_button.display(screen)
        pygame.display.update()
    address, remote_port = ip_input.text, port_input.text
    return address, remote_port

'''准备开始界面'''
def ready_screen(screen, remote_ip, remote_port, sk):
    screen.fill((240,238,214))
    start = False
    imready = False
    rivalready = False
    connected_text = Text("连接成功",  None, 210, True)
    remote_ip_text = Text(f"远程IP:{remote_ip}", None, 350, True)
    remote_port_text = Text(f"远程端口:{remote_port}", None, 400, True)
    start_button = Button("开始游戏", (0,0,0), 500)
    while not start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and start_button.check_click(event.pos):
                    sk.send('1'.encode('utf-8'))
                    imready = True
        try:
            if sk.recv(1024):
                rivalready = True
        except Exception:
            pass
        if imready and rivalready: #双方都点击开始游戏
            start = True
        if start_button.check_click(pygame.mouse.get_pos()):
            start_button = Button("开始游戏", (229,20,0), 500)
        else:
            start_button = Button("开始游戏", (0,0,0), 500)
        connected_text.display(screen)
        remote_ip_text.display(screen)
        remote_port_text.display(screen)
        start_button.display(screen)
        pygame.display.update()

class Button(object):

    def __init__(self, text, color, y):
        self.font = pygame.font.SysFont("SimHei", 40)
        self.surf = self.font.render(text, True, color)
        self.width = self.surf.get_width()
        self.height = self.surf.get_height()
        self.x = 900//2 - self.width//2
        self.y = y
    
    def display(self, screen):
        screen.blit(self.surf, (self.x, self.y))

    def check_click(self, position):
        x_match = position[0] > self.x and position[0] < self.x + self.width
        y_match = position[1] > self.y and position[1] < self.y + self.height
        if x_match and y_match:
            return True
        else:
            return False

class Text(object):

    def __init__(self, text, x, y, center):
        self.font = pygame.font.SysFont("SimHei", 35)
        self.surf = self.font.render(text, True, (0,0,0))
        self.width = self.surf.get_width()
        self.height = self.surf.get_height()
        if center:
            self.x = 900//2 - self.width//2
        else:
            self.x = x
        self.y = y
    
    def display(self, screen):
        screen.blit(self.surf, (self.x, self.y))

class InputBox:
    def __init__(self, w, h, x, y, font=None):
        self.width = w
        self.height = h
        self.x = x
        self.y = y
        self.text = ""
        self.__surface = pygame.Surface((w, h))
        self.__surface.fill((255,255,255))
        if font is None:
            self.font = pygame.font.SysFont("SimHei", 35)
        else:
            self.font = font
 
    def draw(self, dest_surf):
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        dest_surf.blit(self.__surface, (self.x, self.y))
        dest_surf.blit(text_surf, (self.x, self.y + (self.height - text_surf.get_height())),
                       (0, 0, self.width, self.height))
 
    def key_down(self, event):
        unicode = event.unicode
        key = event.key
        if key == 8:
            self.text = self.text[:-1]
            return
        if unicode != "":
            char = unicode
        else:
            char = chr(key)
        self.text += char
    
    def safe_key_down(self, event):
        try:
            self.key_down(event)
        except:
            pass

    def check_click(self, position):
        x_match = position[0] > self.x and position[0] < self.x + self.width
        y_match = position[1] > self.y and position[1] < self.y + self.height
        if x_match and y_match:
            return True
        else:
            return False

if __name__ == '__main__':
    pygame.init()
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sk.setblocking(False)
    screen = pygame.display.set_mode((900, 700))
    remote_ip, remote_port = waiting_screen(screen, sk)
    ready_screen(screen, remote_ip, remote_port, sk)
    while True:
        main(screen, sk)
    