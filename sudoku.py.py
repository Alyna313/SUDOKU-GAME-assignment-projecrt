# ==================FINAL PROJECT==============================
# ==================FINAL PROJECT==============================
import pygame, sys, random, copy
pygame.init()

# --- Window setup ---
WIDTH, HEIGHT = 700, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Fusion Edition")

# --- Colors ---
WHITE = (245, 245, 245)
BLACK = (30, 30, 30)
BLUE = (70, 130, 255)
RED = (255, 70, 70)
GREEN = (100, 220, 100)
CARD = (240, 240, 240)
GRAY = (200, 200, 200)
BTN_COLORS = {
    "New": (150, 200, 255),
    "Reset": (230, 230, 230),
    "Hint": (255, 240, 150),
    "Undo": (220, 190, 255),
    "Solve": (190, 255, 200),
    "Check": (255, 180, 180)
}

# --- Fonts ---
font = pygame.font.SysFont("arial", 32)
small_font = pygame.font.SysFont("arial", 20)

# --- Grid settings ---
GRID_SIZE = 500
GRID_POS = (30, 70)
CELL_SIZE = GRID_SIZE / 9

# --- Confetti animation ---
class ConfettiParticle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-5, -2)
        self.color = (
            random.randint(80, 255),
            random.randint(80, 255),
            random.randint(80, 255)
        )
        self.life = random.randint(60, 120)
    def step(self):
        self.vy += 0.15
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, 5, 5))

confetti = []
def spawn_confetti(x, y, amount=60):
    for _ in range(amount):
        confetti.append(ConfettiParticle(x, y))

# --- Sudoku logic ---
def valid(board, num, pos):
    r, c = pos
    for i in range(9):
        if board[r][i] == num and i != c:
            return False
        if board[i][c] == num and i != r:
            return False
    box_x = c // 3
    box_y = r // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num and (i, j) != pos:
                return False
    return True

def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return (r, c)
    return None

def solve_backtrack(board):
    find = find_empty(board)
    if not find:
        return True
    r, c = find
    for i in range(1, 10):
        if valid(board, i, (r, c)):
            board[r][c] = i
            if solve_backtrack(board):
                return True
            board[r][c] = 0
    return False

def copy_board(b):
    return [row[:] for row in b]

def new_game():
    full = [[0] * 9 for _ in range(9)]
    solve_backtrack(full)
    puzzle = copy_board(full)
    holes = random.randint(40, 55)
    pos = list(range(81))
    random.shuffle(pos)
    for i in pos[:holes]:
        r, c = divmod(i, 9);
        puzzle[r][c] = 0
    return puzzle, full

# --- Drawing ---
def draw_board(win, board, selected, locked):
    pygame.draw.rect(win, WHITE, (GRID_POS[0] - 5, GRID_POS[1] - 5, GRID_SIZE + 10, GRID_SIZE + 10), border_radius=8)

    # draw grid lines
    for i in range(10):
        thick = 3 if i % 3 == 0 else 1
        pygame.draw.line(win, BLACK, (GRID_POS[0], GRID_POS[1] + i * CELL_SIZE), (GRID_POS[0] + GRID_SIZE, GRID_POS[1] + i * CELL_SIZE), thick)
        pygame.draw.line(win, BLACK, (GRID_POS[0] + i * CELL_SIZE, GRID_POS[1]), (GRID_POS[0] + i * CELL_SIZE, GRID_POS[1] + GRID_SIZE), thick)

    # draw numbers
    for r in range(9):
        for c in range(9):
            num = board[r][c]
            if num != 0:
                if (r, c) in locked:
                    color = BLACK
                else:
                    color = BLUE if valid(board, num, (r, c)) else RED
                txt = font.render(str(num), True, color)
                tx = GRID_POS[0] + c * CELL_SIZE + (CELL_SIZE - txt.get_width()) // 2
                ty = GRID_POS[1] + r * CELL_SIZE + (CELL_SIZE - txt.get_height()) // 2
                win.blit(txt, (tx, ty))

    # draw selected cell
    if selected:
        r, c = selected
        pygame.draw.rect(win, BLUE, (GRID_POS[0] + c * CELL_SIZE, GRID_POS[1] + r * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

def draw_buttons(win):
    panel_x = GRID_POS[0] + GRID_SIZE + 20
    panel_y = GRID_POS[1]
    panel_w = 150
    panel_h = GRID_SIZE
    pygame.draw.rect(win, CARD, (panel_x - 8, panel_y - 8, panel_w + 8, panel_h + 16), border_radius=18)
    labels = ["New", "Reset", "Hint", "Undo", "Solve", "Check"]
    buttons = []
    y = panel_y + 20
    for label in labels:
        color = BTN_COLORS.get(label, GRAY)
        rect = pygame.Rect(panel_x + 10, y, panel_w - 30, 52)
        pygame.draw.rect(win, color, rect, border_radius=12)
        pygame.draw.rect(win, (180, 180, 180), rect, 1, border_radius=12)
        txt = small_font.render(label, True, BLACK)
        win.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
        buttons.append(rect)
        y += 72
    return buttons

# --- Main ---
def main():
    puzzle, full = new_game()
    board = copy_board(puzzle)
    original = copy_board(puzzle)
    locked = [(r, c) for r in range(9) for c in range(9) if puzzle[r][c] != 0]
    selected = None
    undo_stack = []
    message = ""
    clock = pygame.time.Clock()
    conflicts = 0   # ✅ Added Conflict Counter
    run = True

    while run:
        clock.tick(30)
        WIN.fill((235, 235, 240))
        draw_board(WIN, board, selected, locked)
        buttons = draw_buttons(WIN)

        # ✅ Display Conflict Counter
        conflict_text = small_font.render(f"Conflicts: {conflicts}", True, RED)
        WIN.blit(conflict_text, (50, 20))

        if message:
            msg = small_font.render(message, True, GREEN)
            WIN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 20))

        for p in confetti[:]:
            p.step()
            p.draw(WIN)
            if p.life <= 0:
                confetti.remove(p)

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if GRID_POS[0] <= x <= GRID_POS[0] + GRID_SIZE and GRID_POS[1] <= y <= GRID_POS[1] + GRID_SIZE:
                    c = int((x - GRID_POS[0]) // CELL_SIZE)
                    r = int((y - GRID_POS[1]) // CELL_SIZE)
                    selected = (r, c)
                else:
                    if buttons[0].collidepoint(x, y):
                        puzzle, full = new_game()
                        board = copy_board(puzzle)
                        original = copy_board(puzzle)
                        locked = [(r, c) for r in range(9) for c in range(9) if puzzle[r][c] != 0]
                        undo_stack.clear()
                        conflicts = 0  # reset conflicts
                        message = "New puzzle!"
                    elif buttons[1].collidepoint(x, y):
                        board = copy_board(original)
                        undo_stack.clear()
                        conflicts = 0  # reset conflicts
                        message = "Reset!"
                    elif buttons[2].collidepoint(x, y):
                        empties = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
                        if empties:
                            r, c = random.choice(empties)
                            undo_stack.append(copy_board(board))
                            board[r][c] = full[r][c]
                            message = "Hint placed!"
                        else:
                            message = "No empty cells!"
                    elif buttons[3].collidepoint(x, y):
                        if undo_stack:
                            board[:] = undo_stack.pop()
                            message = "Undone!"
                    elif buttons[4].collidepoint(x, y):
                        message = "Solving..."
                        pygame.display.update()
                        solve_backtrack(board)
                        message = "Solved!"
                        spawn_confetti(WIDTH / 2, HEIGHT / 2)
                    elif buttons[5].collidepoint(x, y):
                        if board == full:
                            message = "You win!"
                            spawn_confetti(WIDTH / 2, HEIGHT / 2)
                        else:
                            message = "Incorrect!"

            elif e.type == pygame.KEYDOWN and selected:
                r, c = selected
                if (r, c) not in locked:
                    if e.key in [pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4,pygame.K_5,pygame.K_6,pygame.K_7,pygame.K_8,pygame.K_9]:
                        val = int(e.unicode)
                        undo_stack.append(copy_board(board))
                        board[r][c] = val
                        # ✅ Check if entry is invalid
                        if not valid(board, val, (r, c)):
                            conflicts += 1
                    elif e.key in [pygame.K_0,pygame.K_BACKSPACE,pygame.K_DELETE]:
                        undo_stack.append(copy_board(board))
                        board[r][c] = 0

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
