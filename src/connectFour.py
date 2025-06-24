import numpy as np
import pygame
import sys
import math
import random

# Colors
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
WHITE = (255, 255, 255)

# Board size
ROW_COUNT = 6
COLUMN_COUNT = 7

pygame.init()

SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect Four - Single Player")

myfont = pygame.font.SysFont("monospace", 75)
menu_font = pygame.font.SysFont("monospace", 50)

def create_board():
    return np.zeros((ROW_COUNT,COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    # Horizontal check
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # Vertical check
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # Positive diagonal
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    # Negative diagonal
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):        
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == 2: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

def draw_menu():
    screen.fill(BLACK)
    title = myfont.render("Connect Four", True, WHITE)
    easy_text = menu_font.render("Easy", True, WHITE)
    medium_text = menu_font.render("Medium", True, WHITE)
    hard_text = menu_font.render("Hard", True, WHITE)
    quit_text = menu_font.render("Quit", True, WHITE)

    screen.blit(title, (width//2 - title.get_width()//2, height//6))
    screen.blit(easy_text, (width//2 - easy_text.get_width()//2, height//3))
    screen.blit(medium_text, (width//2 - medium_text.get_width()//2, height//3 + 60))
    screen.blit(hard_text, (width//2 - hard_text.get_width()//2, height//3 + 120))
    screen.blit(quit_text, (width//2 - quit_text.get_width()//2, height//3 + 180))
    pygame.display.update()

def draw_endgame_menu(winner):
    screen.fill(BLACK)
    win_color = RED if winner == 1 else YELLOW
    win_text = myfont.render(f"Player {winner} wins!", True, win_color)
    retry_text = menu_font.render("Retry", True, WHITE)
    quit_text = menu_font.render("Return to Menu", True, WHITE)

    screen.blit(win_text, (width//2 - win_text.get_width()//2, height//4))
    screen.blit(retry_text, (width//2 - retry_text.get_width()//2, height//2))
    screen.blit(quit_text, (width//2 - quit_text.get_width()//2, height//2 + 70))
    pygame.display.update()

def ai_move_easy(board):
    valid_cols = [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]
    return random.choice(valid_cols)

def ai_move_medium(board):
    # Try to win next move
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 2)
            if winning_move(temp_board, 2):
                return col

    # Block opponent's winning move
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 1)
            if winning_move(temp_board, 1):
                return col

    # Otherwise pick random
    return ai_move_easy(board)

def ai_move_hard(board):
    def score_position(board, piece):
        score = 0
        center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        for r in range(ROW_COUNT):
            row_array = [int(i) for i in list(board[r,:])]
            for c in range(COLUMN_COUNT-3):
                window = row_array[c:c+4]
                score += evaluate_window(window, piece)

        for c in range(COLUMN_COUNT):
            col_array = [int(i) for i in list(board[:,c])]
            for r in range(ROW_COUNT-3):
                window = col_array[r:r+4]
                score += evaluate_window(window, piece)

        for r in range(ROW_COUNT-3):
            for c in range(COLUMN_COUNT-3):
                window = [board[r+i][c+i] for i in range(4)]
                score += evaluate_window(window, piece)

        for r in range(3, ROW_COUNT):
            for c in range(COLUMN_COUNT-3):
                window = [board[r-i][c+i] for i in range(4)]
                score += evaluate_window(window, piece)

        return score

    def evaluate_window(window, piece):
        score = 0
        opp_piece = 1 if piece == 2 else 2

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(0) == 1:
            score -= 4

        return score

    def is_terminal_node(board):
        return winning_move(board, 1) or winning_move(board, 2) or len(get_valid_locations(board)) == 0

    def get_valid_locations(board):
        return [c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]

    def minimax(board, depth, alpha, beta, maximizingPlayer):
        valid_locations = get_valid_locations(board)
        is_terminal = is_terminal_node(board)

        if depth == 0 or is_terminal:
            if is_terminal:
                if winning_move(board, 2):
                    return (None, 100000000000000)
                elif winning_move(board, 1):
                    return (None, -10000000000000)
                else:
                    return (None, 0)
            else:
                return (None, score_position(board, 2))
        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = get_next_open_row(board, col)
                temp_board = board.copy()
                drop_piece(temp_board, row, col, 2)
                new_score = minimax(temp_board, depth-1, alpha, beta, False)[1]
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value
        else:
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = get_next_open_row(board, col)
                temp_board = board.copy()
                drop_piece(temp_board, row, col, 1)
                new_score = minimax(temp_board, depth-1, alpha, beta, True)[1]
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

    col, minimax_score = minimax(board, 4, -math.inf, math.inf, True)
    return col

def main_game(difficulty):
    board = create_board()
    game_over = False
    turn = 0  # 0 = Player, 1 = AI

    draw_board(board)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over and turn == 0:
                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                    posx = event.pos[0]
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                    pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, 1)

                        if winning_move(board, 1):
                            draw_board(board)
                            pygame.time.wait(500)
                            return 1  # Player wins

                        draw_board(board)
                        turn = 1  # AI's turn

        # AI turn
        if not game_over and turn == 1:
            pygame.time.wait(500)  # Pause before AI moves
            if difficulty == 'Easy':
                col = ai_move_easy(board)
            elif difficulty == 'Medium':
                col = ai_move_medium(board)
            else:
                col = ai_move_hard(board)

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)

                if winning_move(board, 2):
                    draw_board(board)
                    pygame.time.wait(500)
                    return 2  # AI wins

                draw_board(board)
                turn = 0  # Player's turn

        # Check draw condition (all cols full)
        if not game_over and len([c for c in range(COLUMN_COUNT) if is_valid_location(board, c)]) == 0:
            draw_board(board)
            pygame.time.wait(500)
            return 0  # Draw

def main():
    running = True
    in_menu = True
    difficulty = None

    while running:
        if in_menu:
            draw_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    # Check which menu item was clicked
                    if width//2 - 50 < x < width//2 + 50:
                        if height//3 < y < height//3 + 50:
                            difficulty = 'Easy'
                            in_menu = False
                        elif height//3 + 60 < y < height//3 + 110:
                            difficulty = 'Medium'
                            in_menu = False
                        elif height//3 + 120 < y < height//3 + 170:
                            difficulty = 'Hard'
                            in_menu = False
                        elif height//3 + 180 < y < height//3 + 230:
                            running = False

        else:
            # Play game with selected difficulty
            winner = main_game(difficulty)

            # Show endgame menu
            in_end_menu = True
            while in_end_menu:
                draw_endgame_menu(winner)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        in_end_menu = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos
                        # Retry button coords
                        if width//2 - 50 < x < width//2 + 50:
                            if height//2 < y < height//2 + 50:
                                in_end_menu = False  # retry -> back to game
                            elif height//2 + 70 < y < height//2 + 120:
                                # Quit returns to start menu instead of quitting app
                                in_end_menu = False
                                in_menu = True

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()