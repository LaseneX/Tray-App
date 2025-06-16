import pygame
pygame.init()

# Difficulty settings: "easy", "medium", or "hard"
BOT_DIFFICULTY = "medium"

WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong with AI")

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7

SCORE_FONT = pygame.font.SysFont("comicsans", 50)
WINNING_SCORE = 10

# Bot behavior settings
BOT_SETTINGS = {
    "easy": {"vel": 2, "reaction_threshold": 100},
    "medium": {"vel": 4, "reaction_threshold": 75},
    "hard": {"vel": 5, "reaction_threshold": 25}
}


class Paddle:
    COLOR = WHITE
    VEL = 4

    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(
            win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True, vel=None):
        velocity = vel if vel is not None else self.VEL
        if up:
            self.y -= velocity
        else:
            self.y += velocity

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y


class Ball:
    MAX_VEL = 5
    COLOR = WHITE

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0
        self.x_vel *= -1


def draw(win, paddles, ball, left_score, right_score):
    win.fill(BLACK)

    left_score_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
    right_score_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
    win.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()//2, 20))
    win.blit(right_score_text, (WIDTH * (3/4) - right_score_text.get_width()//2, 20))

    for paddle in paddles:
        paddle.draw(win)

    for i in range(10, HEIGHT, HEIGHT//20):
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//20))

    ball.draw(win)
    pygame.display.update()


def handle_collision(ball, left_paddle, right_paddle):
    if ball.y + ball.radius >= HEIGHT or ball.y - ball.radius <= 0:
        ball.y_vel *= -1

    if ball.x_vel < 0:
        if left_paddle.y <= ball.y <= left_paddle.y + left_paddle.height:
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                ball.x_vel *= -1
                offset = (left_paddle.y + left_paddle.height / 2) - ball.y
                ball.y_vel = -offset / (left_paddle.height / 2) * ball.MAX_VEL
    else:
        if right_paddle.y <= ball.y <= right_paddle.y + right_paddle.height:
            if ball.x + ball.radius >= right_paddle.x:
                ball.x_vel *= -1
                offset = (right_paddle.y + right_paddle.height / 2) - ball.y
                ball.y_vel = -offset / (right_paddle.height / 2) * ball.MAX_VEL

def handle_paddle_movement(keys, right_paddle):
    if keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
        right_paddle.move(up=True)
    if keys[pygame.K_DOWN] and right_paddle.y + right_paddle.VEL + right_paddle.height <= HEIGHT:
        right_paddle.move(up=False)

def bot_ai(ball, paddle):
    settings = BOT_SETTINGS[BOT_DIFFICULTY]
    reaction_threshold = settings["reaction_threshold"]
    vel = settings["vel"]

    if ball.x > WIDTH // 2 - reaction_threshold:
        if ball.y < paddle.y + paddle.height // 2 and paddle.y - vel >= 0:
            paddle.move(up=True, vel=vel)
        elif ball.y > paddle.y + paddle.height // 2 and paddle.y + paddle.height + vel <= HEIGHT:
            paddle.move(up=False, vel=vel)

def main():
    def show_menu():
        selected = 1  # 0 = Easy, 1 = Medium, 2 = Hard
        options = ["Easy", "Medium", "Hard"]
        run_menu = True

        while run_menu:
            WIN.fill(BLACK)
            title = SCORE_FONT.render("Select Difficulty", True, WHITE)
            WIN.blit(title, (WIDTH//2 - title.get_width()//2, 50))

            for i, option in enumerate(options):
                color = (255, 0, 0) if i == selected else WHITE
                text = SCORE_FONT.render(option, True, color)
                WIN.blit(text, (WIDTH//2 - text.get_width()//2, 150 + i * 60))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and selected > 0:
                        selected -= 1
                    elif event.key == pygame.K_DOWN and selected < 2:
                        selected += 1
                    elif event.key == pygame.K_RETURN:
                        return options[selected].lower()

    # Get selected difficulty from menu
    global BOT_DIFFICULTY
    BOT_DIFFICULTY = show_menu()

    run = True
    clock = pygame.time.Clock()

    left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    left_score = 0
    right_score = 0

    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle)
        bot_ai(ball, right_paddle)

        ball.move()
        handle_collision(ball, left_paddle, right_paddle)

        if ball.x < 0:
            right_score += 1
            ball.reset()
        elif ball.x > WIDTH:
            left_score += 1
            ball.reset()

        won = False
        if left_score >= WINNING_SCORE:
            win_text = "You Win!"
            won = True
        elif right_score >= WINNING_SCORE:
            win_text = "Bot Wins!"
            won = True

        if won:
            text = SCORE_FONT.render(win_text, 1, WHITE)
            WIN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            pygame.display.update()
            pygame.time.delay(3000)
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0

    pygame.quit()

if __name__ == '__main__':
    main()
