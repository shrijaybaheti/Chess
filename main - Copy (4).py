import pygame
import chess
import chess.engine
import os

# Initialize Pygame
pygame.init()

# Set up display
width, height = 1000, 800  # Increased width for extra buttons
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Chess Bot')

# Load chess engine
engine = chess.engine.SimpleEngine.popen_uci("stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe")

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
orange = (255, 165, 0)  # Color for check
red = (255, 0, 0)  # Color for checkmate

# Define board
board = chess.Board()

# Load piece images with specific names
piece_images = {}
image_folder = "images"
piece_names = {
    'P': 'white_pawn.png', 'R': 'white_rook.png', 'N': 'white_knight.png', 
    'B': 'white_bishop.png', 'Q': 'white_queen.png', 'K': 'white_king.png',
    'p': 'black_pawn.png', 'r': 'black_rook.png', 'n': 'black_knight.png', 
    'b': 'black_bishop.png', 'q': 'black_queen.png', 'k': 'black_king.png'
}

for piece, filename in piece_names.items():
    image_path = os.path.join(image_folder, filename)
    piece_images[piece] = pygame.image.load(image_path)
    piece_images[piece] = pygame.transform.scale(piece_images[piece], (100, 100))

# Function to draw the board
def draw_board():
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for y in range(8):
        for x in range(8):
            color = colors[(x + y) % 2]
            pygame.draw.rect(window, color, pygame.Rect(x * 100, y * 100, 100, 100))
    
    # Highlight the king's square if in check or checkmate
    if board.is_check():
        king_square = board.king(board.turn)
        color = red if board.is_checkmate() else orange
        x, y = chess.square_file(king_square), chess.square_rank(king_square)
        pygame.draw.rect(window, color, pygame.Rect(x * 100, (7 - y) * 100, 100, 100))

# Function to draw pieces using images
def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_image = piece_images[piece.symbol()]
            x, y = chess.square_file(square), chess.square_rank(square)
            window.blit(piece_image, (x * 100, (7 - y) * 100))

# Function to get best move from engine
def get_best_move():
    result = engine.play(board, chess.engine.Limit(time=0.1))
    return result.move

# Function to handle human move
def handle_human_move():
    move_made = False
    selected_square = None
    while not move_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < 800:  # Only handle clicks within the board area
                    file = x // 100
                    rank = 7 - (y // 100)
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
                    if 850 <= x <= 950 and 50 <= y <= 100:
                        reset_game()
                        move_made = True
                    # Check if the AI move button is clicked
                    elif 850 <= x <= 950 and 150 <= y <= 200:
                        toggle_ai_move()
                        move_made = True
        draw_board()
        draw_pieces()
        draw_buttons()
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

# Function to draw extra buttons
def draw_buttons():
    pygame.draw.rect(window, white, pygame.Rect(850, 50, 100, 50))
    font = pygame.font.Font(None, 36)
    text = font.render('Reset', True, black)
    window.blit(text, (860, 60))
    
    pygame.draw.rect(window, white, pygame.Rect(850, 150, 100, 50))
    text = font.render('AI Move', True, black)
    window.blit(text, (860, 160))

# Main loop
running = True
ai_white = False
ai_black = False

while running:
    draw_board()
    draw_pieces()
    draw_buttons()
    pygame.display.flip()

    if board.turn == chess.WHITE:
        if ai_white:
            move = get_best_move()
            board.push(move)
        else:
            handle_human_move()
    else:
        if ai_black:
            move = get_best_move()
            board.push(move)
        else:
            handle_human_move()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 850 <= x <= 950 and 50 <= y <= 100:
                reset_game()

# Quit the engine and Pygame
engine.quit()
pygame.quit()
