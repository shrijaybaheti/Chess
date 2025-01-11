import pygame
import chess
import chess.engine
import os

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 800
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Chess Bot')

# Load chess engine
engine = chess.engine.SimpleEngine.popen_uci("C:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe")

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)

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

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_board()
    draw_pieces()
    pygame.display.flip()

    if board.turn == chess.WHITE:
        move = get_best_move()
        board.push(move)

# Quit the engine and Pygame
engine.quit()
pygame.quit()
