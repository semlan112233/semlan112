
import pygame
import random
import os
import json

pygame.init()
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase_admin.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def send_highscore(name, score):
    doc_ref = db.collection("highscores").document(name)
    doc_ref.set({"name": name, "score": score})

def get_highscores():
    scores_ref = db.collection("highscores")
    docs = scores_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(5).stream()
    return [(doc.to_dict()["name"], doc.to_dict()["score"]) for doc in docs]

pygame.mixer.init()
pygame.mixer.music.load("semlemusik.ogg")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fånga fallande semlor!")

WHITE = (255, 255, 255)
FPS = 60
clock = pygame.time.Clock()

player_img = pygame.image.load("tallrik.png")
player_img = pygame.transform.scale(player_img, (100, 40))

semla_images = ["semla.png", "semla2.png", "semla3.png"]
semla_index = 0
semla_img = pygame.image.load(semla_images[semla_index])
semla_img = pygame.transform.scale(semla_img, (50, 50))

player_x = WIDTH // 2 - 50
player_y = HEIGHT - 60
player_speed = 7

semla_x = random.randint(0, WIDTH - 50)
semla_y = -50
semla_speed = 5

score = 0
misses = 0
font = pygame.font.SysFont(None, 36)

def save_highscore(score):
    with open("highscore.json", "w") as f:
        json.dump({"highscore": score}, f)

def load_highscore():
    if os.path.exists("highscore.json"):
        with open("highscore.json", "r") as f:
            data = json.load(f)
            return data.get("highscore", 0)
    return 0

def draw_menu():
    screen.fill(WHITE)
    title = font.render("Fånga Fallande Semlor", True, (0, 0, 0))
    start = font.render("Tryck på SPACE för att starta", True, (0, 0, 0))
    quit_msg = font.render("Tryck på ESC för att avsluta", True, (0, 0, 0))
    screen.blit(title, (WIDTH // 2 - 150, HEIGHT // 2 - 60))
    screen.blit(start, (WIDTH // 2 - 180, HEIGHT // 2))
    screen.blit(quit_msg, (WIDTH // 2 - 180, HEIGHT // 2 + 40))
    pygame.display.flip()


player_name = ""

def ask_for_name():
    global player_name
    asking = True
    input_box = pygame.Rect(WIDTH // 2 - 140, HEIGHT // 2 - 20, 280, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    input_font = pygame.font.SysFont(None, 40)

    while asking:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        player_name = text or "Anonym"
                        asking = False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill(WHITE)
        txt_surface = input_font.render(text or "Skriv ditt namn...", True, (0, 0, 0))
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)
        prompt = input_font.render("Ange ditt namn och tryck Enter", True, (0, 0, 0))
        screen.blit(prompt, (WIDTH // 2 - 180, HEIGHT // 2 - 60))
        pygame.display.flip()

ask_for_name()
def game_loop():
    global player_x, semla_x, semla_y, semla_speed, score, misses, semla_img, semla_index

    highscore = load_highscore()
    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_highscore(max(score, highscore))
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - 100:
            player_x += player_speed

        semla_y += semla_speed

        if (player_x < semla_x + 50 and
            player_x + 100 > semla_x and
            player_y < semla_y + 50 and
            player_y + 40 > semla_y):
            score += 1
            semla_speed += 0.2
            semla_x = random.randint(0, WIDTH - 50)
            semla_y = -50
            if score % 5 == 0 and semla_index < len(semla_images) - 1:
                semla_index += 1
                semla_img = pygame.image.load(semla_images[semla_index])
                semla_img = pygame.transform.scale(semla_img, (50, 50))
        elif semla_y > HEIGHT:
            misses += 1
            semla_x = random.randint(0, WIDTH - 50)
            semla_y = -50

        screen.blit(player_img, (player_x, player_y))
        screen.blit(semla_img, (semla_x, semla_y))

        score_text = font.render(f"Semlor: {score}", True, (0, 0, 0))
        misses_text = font.render(f"Missar: {misses}/3", True, (200, 0, 0))
        highscore_text = font.render(f"Rekord: {highscore}", True, (0, 100, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(misses_text, (10, 40))
        screen.blit(highscore_text, (10, 70))

        if misses >= 3:
            save_highscore(max(score, highscore))
            game_over_text = font.render("Game Over! Tryck på ESC för att avsluta.", True, (0, 0, 0))
            screen.blit(game_over_text, (WIDTH // 2 - 200, HEIGHT // 2))
            pygame.display.flip()
            while True:
                event = pygame.event.wait()
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return
            continue

        pygame.display.flip()
        clock.tick(FPS)

# Menyloop
while True:
    draw_menu()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                    game_loop()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
