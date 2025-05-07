import tkinter as tk
from tkinter import messagebox
import random
import time
import heapq

goal_state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
worst_case_state = [8, 7, 6, 5, 4, 3, 2, 1, 0]  # estado reverso

def is_solvable(state):
    inv = 0
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            if state[i] and state[j] and state[i] > state[j]:
                inv += 1
    return inv % 2 == 0

def shuffle_state():
    state = goal_state[:]
    while True:
        random.shuffle(state)
        if is_solvable(state) and state != goal_state:
            return state

def manhattan(state):
    dist = 0
    for i, val in enumerate(state):
        if val != 0:
            goal_i = goal_state.index(val)
            dist += abs(i // 3 - goal_i // 3) + abs(i % 3 - goal_i % 3)
    return dist

def get_neighbors(state):
    neighbors = []
    i = state.index(0)
    row, col = divmod(i, 3)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in moves:
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < 3:
            ni = r * 3 + c
            new_state = state[:]
            new_state[i], new_state[ni] = new_state[ni], new_state[i]
            neighbors.append(new_state)
    return neighbors

def search(start, algorithm):
    visited = set()
    queue = []
    start_time = time.time()

    def push(state, path, cost):
        if algorithm == 'greedy':
            priority = manhattan(state)
        elif algorithm == 'astar':
            priority = cost + manhattan(state)
        else:
            priority = cost
        heapq.heappush(queue, (priority, cost, state, path))

    push(start, [], 0)

    while queue:
        _, cost, state, path = heapq.heappop(queue)
        state_tuple = tuple(state)
        if state == goal_state:
            return path + [state], len(path), (time.time() - start_time) * 1000
        if state_tuple not in visited:
            visited.add(state_tuple)
            for neighbor in get_neighbors(state):
                if tuple(neighbor) not in visited:
                    push(neighbor, path + [state], cost + 1)
    return [], 0, (time.time() - start_time) * 1000

class PuzzleApp:
    def __init__(self, master):
        self.master = master
        master.title("8-Puzzle")

        self.state = shuffle_state()
        self.initial_state = self.state[:]

        self.frame = tk.Frame(master)
        self.frame.pack(pady=10)

        self.tiles = []
        for i in range(9):
            tile = tk.Button(self.frame, font=("Arial", 24), width=4, height=2,
                             command=lambda i=i: self.move(i))
            tile.grid(row=i // 3, column=i % 3)
            self.tiles.append(tile)

        self.update_tiles()

        self.algo = tk.StringVar(value="uniform")
        algo_frame = tk.Frame(master)
        algo_frame.pack()

        for text in ["Uniforme", "Gulosa", "A*"]:
            val = text.lower().replace("gulosa", "greedy").replace("uniforme", "uniform").replace("a*", "astar")
            tk.Radiobutton(algo_frame, text=text, variable=self.algo, value=val).pack(side=tk.LEFT, padx=5)

        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Embaralhar", command=self.shuffle).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Melhor Caso", command=self.set_best_case).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Pior Caso", command=self.set_worst_case).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Resolver", command=self.solve).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)

    def update_tiles(self):
        for i, val in enumerate(self.state):
            if val == 0:
                self.tiles[i].config(text="", bg="lightgray")
            else:
                self.tiles[i].config(text=str(val), bg="SystemButtonFace")

    def move(self, i):
        zero = self.state.index(0)
        if abs(i - zero) == 1 and i // 3 == zero // 3 or abs(i - zero) == 3:
            self.state[i], self.state[zero] = self.state[zero], self.state[i]
            self.update_tiles()

    def shuffle(self):
        self.state = shuffle_state()
        self.initial_state = self.state[:]
        self.update_tiles()

    def set_best_case(self):
        self.state = goal_state[:]
        self.initial_state = self.state[:]
        self.update_tiles()

    def set_worst_case(self):
        if is_solvable(worst_case_state):
            self.state = worst_case_state[:]
            self.initial_state = self.state[:]
            self.update_tiles()
        else:
            messagebox.showwarning("Insolúvel", "O pior caso definido não é solucionável. Ajuste necessário.")

    def reset(self):
        self.state = self.initial_state[:]
        self.update_tiles()

    def solve(self):
        algo = self.algo.get()
        solution, steps, duration = search(self.state, algo)
        if not solution:
            messagebox.showinfo("Erro", "Nenhuma solução encontrada.")
            return
        self.animate(solution, steps, duration)

    def animate(self, solution, steps, duration):
        def step(i):
            if i < len(solution):
                self.state = solution[i]
                self.update_tiles()
                self.master.after(300, step, i + 1)
            else:
                messagebox.showinfo("Concluído", f"Movimentos: {steps}\nTempo: {duration:.2f} ms")
        step(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
