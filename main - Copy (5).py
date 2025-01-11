import pygame
import chess
import chess.engine
import os

# Initialize Pygame
pygame.init()

# Set up display
base_window_size = 400  # Reduced base size for the board
button_width, button_height = 60, 25  # Reduced button size
window = pygame.display.set_mode((base_window_size + button_width, base_window_size), pygame.RESIZABLE)
pygame.display.set_caption('Chess Bot')

# Load chess engine
engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2.exe")

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
orange = (255, 165, 0)  # Color for check
red = (255, 0, 0)  # Color for checkmate

# Define board
board = chess.Board()
flip_board = False  # Variable to track board orientation

# Load piece images with specific names
piece_images = {}
image_folder = "images"
piece_names = {
    'P': 'white_pawn.png', 'R': 'white_rook.png', 'N': 'white_knight.png', 
    'B': 'white_bishop.png', 'Q': 'white_queen.png', 'K': 'white_king.png',
    'p': 'black_pawn.png', 'r': 'black_rook.png', 'n': 'black_knight.png', 
    'b': 'black_bishop.png', 'q': 'black_queen.png', 'k': 'black_king.png'
}

def load_images(square_size):
    for piece, filename in piece_names.items():
        image_path = os.path.join(image_folder, filename)
        piece_images[piece] = pygame.image.load(image_path)
        piece_images[piece] = pygame.transform.scale(piece_images[piece], (square_size, square_size))

# Function to draw the board
def draw_board(window_size):
    square_size = window_size // 8
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for y in range(8):
        for x in range(8):
            color = colors[(x + y) % 2]
            pygame.draw.rect(window, color, pygame.Rect(x * square_size, y * square_size, square_size, square_size))
    
    # Highlight the king's square if in check or checkmate
    if board.is_check():
        king_square = board.king(board.turn)
        color = red if board.is_checkmate() else orange
        x, y = chess.square_file(king_square), chess.square_rank(king_square)
        pygame.draw.rect(window, color, pygame.Rect(x * square_size, (7 - y) * square_size, square_size, square_size))

# Function to draw pieces using images
def draw_pieces(window_size):
    square_size = window_size // 8
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_image = piece_images[piece.symbol()]
            x, y = chess.square_file(square), chess.square_rank(square)
            if flip_board:
                x, y = 7 - x, 7 - y
            window.blit(piece_image, (x * square_size, (7 - y) * square_size))

# Function to get best move from engine
def get_best_move():
    result = engine.play(board, chess.engine.Limit(time=0.1))
    return result.move

# Function to handle human move
def handle_human_move(window_size):
    square_size = window_size // 8
    move_made = False
    selected_square = None
    while not move_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < window_size and y < window_size:  # Only handle clicks within the board area
                    file = x // square_size
                    rank = 7 - (y // square_size)
                    if flip_board:
                        file, rank = 7 - file, 7 - rank
                    square = chess.square(file, rank)
                    if selected_square is None:
                        selected_square = square
                    else:
                        move = chess.Move(selected_square, square)
                        if move in board.legal_moves:
                            board.push(move)
                            move_made = True
                        selected_square = None
                else:
                    # Check if the reset button is clicked
                    if window_size <= x <= window_size + button_width and 25 <= y <= 25 + button_height:
                        reset_game()
                        move_made = True
                    # Check if the AI move button is clicked
                    elif window_size <= x <= window_size + button_width and 75 <= y <= 75 + button_height:
                        toggle_ai_move()
                        move_made = True
                    # Check if the undo button is clicked
                    elif window_size <= x <= window_size + button_width and 125 <= y <= 125 + button_height:
                        undo_move()
                        move_made = True
                    # Check if the flip board button is clicked
                    elif window_size <= x <= window_size + button_width and 175 <= y <= 175 + button_height:
                        flip_board_orientation()
                        move_made = True
        draw_board(window_size)
        draw_pieces(window_size)
        draw_buttons(window_size)
        pygame.display.flip()

# Function to reset the game
def reset_game():
    global ai_white, ai_black
    board.reset()
    ai_white = False
    ai_black = False

# Function to toggle AI move for the current player
def toggle_ai_move():
    global ai_white, ai_black
    if board.turn == chess.WHITE:
        ai_white = not ai_white
    else:
        ai_black = not ai_black

# Function to undo the last move
def undo_move():
    if len(board.move_stack) > 0:
        board.pop()
        if len(board.move_stack) > 0:
            board.pop()

# Function to flip the board orientation
def flip_board_orientation():
    global flip_board
    flip_board = not flip_board

# Function to draw extra buttons
def draw_buttons(window_size):
    pygame.draw.rect(window, white, pygame.Rect(window_size, 25, button_width, button_height))
    font = pygame.font.Font(None, 18)
    text = font.render('Reset', True, black)
    window.blit(text, (window_size + 5, 30))
    
    pygame.draw.rect(window, white, pygame.Rect(window_size, 75, button_width, button_height))
    text = font.render('AI Move', True, black)
    window.blit(text, (window_size + 5, 80))
    
    pygame.draw.rect(window, white, pygame.Rect(window_size, 125, button_width, button_height))
    text = font.render('Undo', True, black)
    window.blit(text, (window_size + 5, 130))
    
    pygame.draw.rect(window, white, pygame.Rect(window_size, 175, button_width, button_height))
    text = font.render('Flip', True, black)
    window.blit(text, (window_size + 5, 180))

# Main loop
running = True
ai_white = False
ai_black = False

while running:
    window_width, window_height = window.get_size()
    window_size = min(window_width - button_width, window_height)
    square_size = window_size // 8
    load_images(square_size)
    
    draw_board(window_size)
    draw_pieces(window_size)
    draw_buttons(window_size)
    pygame.display.flip()

    if board.turn == chess.WHITE:
        if ai_white:
            move = get_best_move()
            board.push(move)
        else:
            handle_human_move(window_size)
    else:
        if ai_black:
            move = get_best_move()
            board.push(move)
        else:
            handle_human_move(window_size)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if window_size <= x <= window_size + button_width and 25 <= y <= 25 + button_height:
                reset_game()

# Quit the engine and Pygame
engine.quit()
pygame.quit()
