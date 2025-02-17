import pygame
import chess
import chess.engine
import os

# Initialize Pygame
pygame.init()

# Set up display
base_window_size = 400
button_width, button_height = 80, 30
window = pygame.display.set_mode((base_window_size + button_width, base_window_size), pygame.RESIZABLE)
pygame.display.set_caption('Chess Bot')

# Load chess engine
engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2.exe")

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (169, 169, 169)
green = (34, 139, 34)
orange = (255, 165, 0)  # Color for check
red = (255, 69, 0)  # Color for checkmate
blue = (130, 200, 130, 50)  # Translucent blue for arrows

# Define fonts
font_square_address = pygame.font.Font(pygame.font.get_default_font(), 10)  # Small font for square addresses
font_smallest = pygame.font.Font(pygame.font.get_default_font(), 10)
font_small = pygame.font.Font(pygame.font.get_default_font(), 16)
font_large = pygame.font.Font(pygame.font.get_default_font(), 20)

# Define board
board = chess.Board()
flip_board = False
last_move = None

# Add this variable at the beginning of your code
slider_dragging = False

# Load piece images
piece_images = {}
image_folder = "images"
piece_names = {
    'P': 'white_pawn.png', 'R': 'white_rook.png', 'N': 'white_knight.png',
    'B': 'white_bishop.png', 'Q': 'white_queen.png', 'K': 'white_king.png',
    'p': 'black_pawn.png', 'r': 'black_rook.png', 'n': 'black_knight.png',
    'b': 'black_bishop.png', 'q': 'black_queen.png', 'k': 'black_king.png'
}

author_note = "@shrijay_baheti"

def draw_author_note(window):
    text = font_smallest.render(author_note, True, white)  # Render the text
    text_rect = text.get_rect(center=(base_window_size + button_width // 2, base_window_size - 20))  # Position it at the bottom center
    window.blit(text, text_rect)  # Draw the text on the window

def load_images(square_size):
    for piece, filename in piece_names.items():
        image_path = os.path.join(image_folder, filename)
        piece_images[piece] = pygame.image.load(image_path)
        piece_images[piece] = pygame.transform.scale(piece_images[piece], (square_size, square_size))

def draw_board(window_size):
    square_size = window_size // 8
    colors = [pygame.Color("#f0d9b5"), pygame.Color("#b58863")]
    for y in range(8):
        for x in range(8):
            color = colors[(x + y) % 2]
            pygame.draw.rect(window, color, pygame.Rect(x * square_size, y * square_size, square_size, square_size))
            
            # Calculate the square address (e.g., "a1", "h8")
            square_address = f"{chr(97 + x)}{8 - y}"  # 'a' is 97 in ASCII
            
            # Render the square address
            address_text = font_square_address.render(square_address, True, black)  # Render the text
            text_rect = address_text.get_rect(bottomright=(x * square_size + square_size - 2, (y + 1) * square_size - 2))  # Position it at the bottom right corner
            window.blit(address_text, text_rect)  # Draw the text on the window

    if board.is_check():
        king_square = board.king(board.turn)
        color = red if board.is_checkmate() else orange
        x, y = chess.square_file(king_square), chess.square_rank(king_square)
        pygame.draw.rect(window, color, pygame.Rect(x * square_size, (7 - y) * square_size, square_size, square_size))

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

def draw_last_move_arrow(window_size):
    global last_move
    if last_move:
        square_size = window_size // 8
        start_square = last_move.from_square
        end_square = last_move.to_square
        start_x, start_y = chess.square_file(start_square), chess.square_rank(start_square)
        end_x, end_y = chess.square_file(end_square), chess.square_rank(end_square)
        
        if flip_board:
            start_x, start_y = 7 - start_x, 7 - start_y
            end_x, end_y = 7 - end_x, 7 - end_y
        
        start_pos = (start_x * square_size + square_size // 2, (7 - start_y) * square_size + square_size // 2)
        end_pos = (end_x * square_size + square_size // 2, (7 - end_y) * square_size + square_size // 2)
        
        # Draw the line from start to end
        pygame.draw.line(window, blue[:3], start_pos, end_pos, 5)
        
        # Calculate the direction of the arrow
        arrow_head_size = 10
        arrow_direction = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
        arrow_length = (arrow_direction[0]**2 + arrow_direction[1]**2)**0.5
        
        if arrow_length > 0:
            # Normalize the direction vector
            norm_arrow_direction = (arrow_direction[0] / arrow_length, arrow_direction[1] / arrow_length)
            
            # Calculate the points for the arrowhead
            left_arrowhead = (end_pos[0] - arrow_head_size * (norm_arrow_direction[0] + norm_arrow_direction[1]),
                              end_pos[1] - arrow_head_size * (norm_arrow_direction[1] - norm_arrow_direction[0]))
            right_arrowhead = (end_pos[0] - arrow_head_size * (norm_arrow_direction[0] - norm_arrow_direction[1]),
                               end_pos[1] - arrow_head_size * (norm_arrow_direction[1] + norm_arrow_direction[0]))
            
            # Draw the arrowhead
            pygame.draw.polygon(window, blue[:3], [end_pos, left_arrowhead, right_arrowhead])

def get_best_move():
    result = engine.play(board, chess.engine.Limit(depth=ai_difficulty))
    return result.move

def handle_slider(x):
    global ai_difficulty
    slider_x = window.get_size()[0] - button_width + 10
    slider_width = button_width - 20
    relative_x = x - slider_x
    if 0 <= relative_x <= slider_width:
        ai_difficulty = int(1 + (relative_x / slider_width) * 49)

def handle_human_move(window_size):
    global last_move, slider_dragging
    square_size = window_size // 8
    move_made = False
    selected_square = None
    while not move_made:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                engine.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < window_size and y < window_size:
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
                            last_move = move
                            move_made = True
                        selected_square = None
                else:
                    # Check for button clicks
                    if window_size <= x <= window_size + button_width:
                        if 25 <= y <= 25 + button_height:  # Reset button
                            reset_game()
                            move_made = True
                        elif 75 <= y <= 75 + button_height:  # AI Move button
                            toggle_ai_move()
                            move_made = True
                        elif 125 <= y <= 125 + button_height:  # Undo button
                            undo_move()
                            move_made = True
                        elif 175 <= y <= 175 + button_height:  # Flip button
                            flip_board_orientation()
                            move_made = True
                        elif 225 <= y <= 225 + button_height:  # Slider button
                            slider_dragging = True  # Start dragging the slider
                            handle_slider(x)  # Update difficulty immediately
            elif event.type == pygame.MOUSEBUTTONUP:
                slider_dragging = False  # Stop dragging the slider
            elif event.type == pygame.MOUSEMOTION:
                if slider_dragging:
                    handle_slider(event.pos[0])  # Update difficulty while dragging
        draw_board(window_size)
        draw_pieces(window_size)
        draw_last_move_arrow(window_size)
        draw_buttons(window_size)
        draw_author_note(window) 
        pygame.display.flip()

def reset_game():
    global ai_white, ai_black, last_move
    board.reset()
    ai_white = False
    ai_black = False
    last_move = None

def toggle_ai_move():
    global ai_white, ai_black
    if board.turn == chess.WHITE:
        ai_white = not ai_white
    else:
        ai_black = not ai_black

def undo_move():
    global last_move
    if board.move_stack:
        board.pop()
        last_move = board.move_stack[-1] if board.move_stack else None
        if board.move_stack:
            board.pop()

def flip_board_orientation():
    global flip_board
    flip_board = not flip_board

def draw_buttons(window_size):
    button_color = (70, 130, 180)
    text_color = white
    buttons = ["Reset", "AI Move", "Undo", "Flip"]
    for i, label in enumerate(buttons):
        pygame.draw.rect(window, button_color, pygame.Rect(window_size, 25 + i * 50, button_width, button_height), border_radius=10)
        text = font_large.render(label, True, text_color)
        text_rect = text.get_rect(center=(window_size + button_width // 2, 25 + i * 50 + button_height // 2))
        window.blit(text, text_rect)

    # AI difficulty slider
    pygame.draw.rect(window, gray, pygame.Rect(window_size, 225, button_width, button_height), border_radius=10)
    slider_width = button_width - 20
    slider_x = window_size + 10
    slider_y = 230
    slider_pos = int((ai_difficulty - 1) / 49 * slider_width) + slider_x
    pygame.draw.line(window, black, (slider_x, slider_y + button_height // 2), (slider_x + slider_width, slider_y + button_height // 2), 3)
    pygame.draw.circle(window, blue[:3], (slider_pos, slider_y + button_height // 2), 4)

    # Adjusted position for difficulty text
    text = font_small.render(f'Diff: {ai_difficulty}', True, black)
    text_rect = text.get_rect(center=(slider_x + slider_width // 2.5, slider_y + 5))  # Position above the slider
    window.blit(text, text_rect)

def handle_slider(x):
    global ai_difficulty
    slider_x = window.get_size()[0] - button_width + 10
    slider_width = button_width - 20
    relative_x = x - slider_x
    if 0 <= relative_x <= slider_width:
        ai_difficulty = int(1 + (relative_x / slider_width) * 49)

running = True
ai_white = False
ai_black = False
ai_difficulty = 5

while running:
    window_width, window_height = window.get_size()
    window_size = min(window_width - button_width, window_height)
    square_size = window_size // 8
    load_images(square_size)
    
    draw_board(window_size)
    draw_pieces(window_size)
    draw_last_move_arrow(window_size)
    draw_buttons(window_size)
    draw_author_note(window) 
    pygame.display.flip()

    if board.turn == chess.WHITE:
        if ai_white:
            move = get_best_move()
            board.push(move)
            last_move = move
        else:
            handle_human_move(window_size)
    else:
        if ai_black:
            move = get_best_move()
            board.push(move)
            last_move = move
        else:
            handle_human_move(window_size)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if window_size <= x <= window_size + button_width and 225 <= y <= 225 + button_height:
                slider_dragging = True  # Start dragging the slider
                handle_slider(x)  # Update difficulty immediately
        elif event.type == pygame.MOUSEBUTTONUP:
            slider_dragging = False  # Stop dragging the slider
        elif event.type == pygame.MOUSEMOTION:
            if slider_dragging:
                handle_slider(event.pos[0])  # Update difficulty while dragging

pygame.quit()
engine.quit()
