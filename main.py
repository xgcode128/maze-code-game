import tkinter as tk
import random

CELL = 30
DELAY = 120
LEVEL_COUNT = 50

BG = "#1e1e1e"
WALL = "#4a4a4a"
PATH = "#2b2b2b"
START = "#3f5f7f"
EXIT = "#4f7f5f"
PLAYER = "#d0d0d0"
TEXT = "#e0e0e0"
ERROR = "#ff6b6b"
SUCCESS = "#7bd88f"
ERROR_HIGHLIGHT = "#7a3b3b"


def generate_maze(width, height, level):
    maze = [["X"] * width for _ in range(height)]

    def carve(r, c):
        maze[r][c] = " "
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)

        for dr, dc in directions:
            nr = r + dr
            nc = c + dc

            if 1 <= nr < height - 1 and 1 <= nc < width - 1:
                if maze[nr][nc] == "X":
                    maze[r + dr // 2][c + dc // 2] = " "
                    carve(nr, nc)

    carve(1, 1)

    # чем выше уровень, тем больше открытых проходов
    extra_paths = level // 2
    for _ in range(extra_paths):
        r = random.randrange(1, height - 1)
        c = random.randrange(1, width - 1)
        maze[r][c] = " "

    maze[1][1] = "S"
    maze[height - 2][width - 2] = "E"

    return ["".join(row) for row in maze]


def create_levels():
    levels = []

    for level in range(1, LEVEL_COUNT + 1):
        size = 9 + level // 3

        if size % 2 == 0:
            size += 1

        size = min(size, 27)

        maze = generate_maze(size, size, level)
        levels.append(maze)

    return levels


LEVELS = create_levels()


class MazeGame:
    def __init__(self):
        self.level_index = 0
        self.maze = LEVELS[self.level_index]
        self.start_pos = self.find_cell("S")
        self.player_pos = self.start_pos.copy()
        self.error_cell = None
        self.running = False
        self.finished = False

        self.root = tk.Tk()
        self.root.title("Maze Code Game")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.title = tk.Label(
            self.root,
            text="",
            bg=BG,
            fg=TEXT,
            font=("Consolas", 18, "bold")
        )
        self.title.pack(pady=(12, 4))

        self.canvas = tk.Canvas(
            self.root,
            bg=BG,
            highlightthickness=0
        )
        self.canvas.pack(pady=10)

        self.code_box = tk.Text(
            self.root,
            height=8,
            width=62,
            bg="#1b1b1b",
            fg=TEXT,
            insertbackground=TEXT,
            font=("Consolas", 12),
            relief="flat",
            padx=10,
            pady=10
        )
        self.code_box.pack(padx=12)

        self.msg = tk.Label(
            self.root,
            text="",
            bg=BG,
            fg=TEXT,
            font=("Consolas", 10)
        )
        self.msg.pack(pady=8)

        frame = tk.Frame(self.root, bg=BG)
        frame.pack(pady=10)

        tk.Button(
            frame,
            text="Проверить",
            command=self.run_code,
            bg="#3a3a3a",
            fg="white",
            relief="flat",
            padx=14,
            pady=7,
            font=("Consolas", 10, "bold")
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            frame,
            text="Сброс",
            command=self.reset,
            bg="#2b2b2b",
            fg="white",
            relief="flat",
            padx=14,
            pady=7,
            font=("Consolas", 10)
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            frame,
            text="Очистить",
            command=self.clear_code,
            bg="#2b2b2b",
            fg="white",
            relief="flat",
            padx=14,
            pady=7,
            font=("Consolas", 10)
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            frame,
            text="?",
            command=self.show_help,
            bg="#2b2b2b",
            fg="white",
            relief="flat",
            padx=14,
            pady=7,
            font=("Consolas", 10, "bold")
        ).grid(row=0, column=3, padx=5)

        self.next_btn = tk.Button(
            frame,
            text="Следующий уровень",
            command=self.next_level,
            bg="#355f3b",
            fg="white",
            relief="flat",
            padx=14,
            pady=7,
            font=("Consolas", 10, "bold"),
            state="disabled"
        )
        self.next_btn.grid(row=0, column=4, padx=5)

        self.hero = Hero(self)
        self.load_level(0)

    def find_cell(self, target):
        for r, row in enumerate(self.maze):
            for c, cell in enumerate(row):
                if cell == target:
                    return [r, c]
        return [1, 1]

    def load_level(self, index):
        self.level_index = index
        self.maze = LEVELS[self.level_index]
        self.start_pos = self.find_cell("S")
        self.player_pos = self.start_pos.copy()
        self.error_cell = None
        self.running = False
        self.finished = False

        self.title.config(
            text=f"Level {self.level_index + 1} / {len(LEVELS)}"
        )

        self.canvas.config(
            width=len(self.maze[0]) * CELL,
            height=len(self.maze) * CELL
        )

        self.code_box.delete("1.0", tk.END)
        self.code_box.insert(
            "1.0",
            "hero.moveRight()\nhero.moveDown()\n"
        )

        self.next_btn.config(state="disabled")
        self.msg.config(text="Напиши код и нажми Проверить", fg=TEXT)

        self.draw()

    def draw(self):
        self.canvas.delete("all")

        for r, row in enumerate(self.maze):
            for c, cell in enumerate(row):
                x = c * CELL
                y = r * CELL

                color = PATH

                if cell == "X":
                    color = WALL
                elif cell == "S":
                    color = START
                elif cell == "E":
                    color = EXIT

                self.canvas.create_rectangle(
                    x,
                    y,
                    x + CELL,
                    y + CELL,
                    fill=color,
                    outline=BG
                )

        if self.error_cell:
            r, c = self.error_cell
            x = c * CELL
            y = r * CELL

            self.canvas.create_rectangle(
                x,
                y,
                x + CELL,
                y + CELL,
                fill=ERROR_HIGHLIGHT,
                outline=ERROR,
                width=2
            )

        x = self.player_pos[1] * CELL
        y = self.player_pos[0] * CELL

        self.canvas.create_oval(
            x + 8,
            y + 8,
            x + CELL - 8,
            y + CELL - 8,
            fill=PLAYER,
            outline=""
        )

    def move(self, dr, dc):
        if self.finished:
            return "win"

        r = self.player_pos[0] + dr
        c = self.player_pos[1] + dc

        if r < 0 or c < 0 or r >= len(self.maze) or c >= len(self.maze[0]):
            self.msg.config(text="❌ Нельзя выйти за карту.", fg=ERROR)
            return False

        if self.maze[r][c] == "X":
            self.error_cell = [r, c]
            self.draw()
            self.msg.config(text="❌ Здесь стена. Исправь путь.", fg=ERROR)
            return False

        self.error_cell = None
        self.player_pos = [r, c]

        self.draw()
        self.root.update()
        self.root.after(DELAY)

        if self.maze[r][c] == "E":
            self.finished = True

            if self.level_index + 1 >= len(LEVELS):
                self.msg.config(text="🏆 Ты прошёл все 50 уровней!", fg=SUCCESS)
                self.next_btn.config(state="disabled")
            else:
                self.msg.config(text="🏆 Победа! Жми Следующий уровень.", fg=SUCCESS)
                self.next_btn.config(state="normal")

            return "win"

        return True

    def run_code(self):
        if self.running:
            return

        self.running = True
        self.finished = False
        self.player_pos = self.start_pos.copy()
        self.error_cell = None
        self.next_btn.config(state="disabled")
        self.draw()

        self.msg.config(text="▶ Проверяю код...", fg=TEXT)

        code = self.code_box.get("1.0", tk.END)

        try:
            exec(code, {"hero": self.hero})
        except Exception as e:
            self.msg.config(text=f"Ошибка: {e}", fg=ERROR)

        self.running = False

    def reset(self):
        self.running = False
        self.finished = False
        self.player_pos = self.start_pos.copy()
        self.error_cell = None
        self.next_btn.config(state="disabled")
        self.draw()
        self.msg.config(text="Сброшено", fg=TEXT)

    def clear_code(self):
        self.reset()
        self.code_box.delete("1.0", tk.END)

    def next_level(self):
        if self.level_index + 1 < len(LEVELS):
            self.load_level(self.level_index + 1)

    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Как писать код")
        help_window.configure(bg=BG)
        help_window.resizable(False, False)

        help_text = tk.Text(
            help_window,
            width=52,
            height=20,
            bg="#1b1b1b",
            fg=TEXT,
            insertbackground=TEXT,
            font=("Consolas", 11),
            relief="flat",
            padx=12,
            pady=12
        )
        help_text.pack(padx=10, pady=10)

        help_text.insert(
            "1.0",
            """# Команды

hero.moveRight()
hero.moveLeft()
hero.moveUp()
hero.moveDown()

# Несколько клеток сразу

hero.moveRight(3)
hero.moveDown(2)

# Пример

hero.moveRight(4)
hero.moveDown(3)
hero.moveLeft()
hero.moveDown(2)

# Цель

Дойти до зелёной клетки.

# Если ошибка

Красная подсветка покажет стену.
"""
        )

        help_text.config(state="disabled")

    def start(self):
        self.root.mainloop()


class Hero:
    def __init__(self, game):
        self.game = game

    def moveUp(self, steps=1):
        self.check_steps(steps)
        for _ in range(steps):
            result = self.game.move(-1, 0)
            if result in [False, "win"]:
                return

    def moveDown(self, steps=1):
        self.check_steps(steps)
        for _ in range(steps):
            result = self.game.move(1, 0)
            if result in [False, "win"]:
                return

    def moveLeft(self, steps=1):
        self.check_steps(steps)
        for _ in range(steps):
            result = self.game.move(0, -1)
            if result in [False, "win"]:
                return

    def moveRight(self, steps=1):
        self.check_steps(steps)
        for _ in range(steps):
            result = self.game.move(0, 1)
            if result in [False, "win"]:
                return

    @staticmethod
    def check_steps(steps):
        if not isinstance(steps, int):
            raise ValueError("В скобках должно быть число.")
        if steps < 1:
            raise ValueError("Число должно быть больше 0.")
        if steps > 30:
            raise ValueError("Слишком большое число шагов.")


game = MazeGame()
game.start()