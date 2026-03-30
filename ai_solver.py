import heapq
import random
import copy
from collections import deque

class PipeGameAI:
    def __init__(self, logic):
        self.logic = logic

    def solve(self):
        # Thuật toán mô phỏng BFS/A* để tìm chuỗi Rotations tối ưu
        start_r, start_c = self.logic.start_pos
        end_r, end_c = self.logic.end_pos
        
        initial_entry_dir = self.logic.source_direction
        
        # State: (r, c, entry_dir_to_this_node)
        start_state = (start_r, start_c, initial_entry_dir)
        
        # Priority Queue: (cost, id(tiện lợi debug tránh so sánh state), state)
        pq = []
        heapq.heappush(pq, (0, 0, start_state))
        
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, g, current = heapq.heappop(open_set)
            r, c, entry = current

            if (r, c) == self.game.end_pos:
                return self.reconstruct_path(came_from, current, 0)

            pipe_type = self.game.grid_type[r][c]

            for rot in range(4):
                openings = self.game.PIPE_CONNECTIONS[pipe_type][rot]

                if entry not in openings:
                    continue

                for out_dir in openings:
                    if out_dir == entry:
                        continue

                    dr, dc = 0, 0
                    if out_dir == self.game.TOP:
                        dr, next_entry = -1, self.game.BOTTOM
                    elif out_dir == self.game.BOTTOM:
                        dr, next_entry = 1, self.game.TOP
                    elif out_dir == self.game.LEFT:
                        dc, next_entry = -1, self.game.RIGHT
                    elif out_dir == self.game.RIGHT:
                        dc, next_entry = 1, self.game.LEFT

                    nr, nc = r + dr, c + dc

                    if not (0 <= nr < self.game.size and 0 <= nc < self.game.size):
                        continue
                    if self.game.grid_type[nr][nc] == 0:
                        continue

                    neighbor = (nr, nc, next_entry)
                    new_g = g + 1

                    if neighbor not in g_score or new_g < g_score[neighbor]:
                        g_score[neighbor] = new_g
                        f = new_g + self.heuristic(nr, nc)
                        heapq.heappush(open_set, (f, new_g, neighbor))
                        came_from[neighbor] = (current, rot)

        return None

    # =========================
    # 3. HILL CLIMBING
    # =========================
    def solve_hill_climbing(self, max_iter=1000):
        current = copy.deepcopy(self.game.grid_rotation)

        for _ in range(max_iter):
            self.game.grid_rotation = current

            if self.game.check_win():
                return current

            best = current
            best_score = self.evaluate()

            for r in range(self.game.size):
                for c in range(self.game.size):
                    new_state = copy.deepcopy(current)
                    new_state[r][c] = (new_state[r][c] + 1) % 4

                    self.game.grid_rotation = new_state
                    score = self.evaluate()

                    if score > best_score:
                        best = new_state
                        best_score = score

            if best == current:
                break  # local optimum

            current = best

        return None

    # =========================
    # ĐÁNH GIÁ STATE (HEURISTIC)
    # =========================
    def evaluate(self):
        count = 0
        for r in range(self.game.size):
            for c in range(self.game.size):
                if self.game.get_valid_neighbors(r, c):
                    count += 1
        return count

    # =========================
    # UTIL
    # =========================
    def serialize(self, grid):
        return tuple(tuple(row) for row in grid)

    def reconstruct_path(self, came_from, current, rot):
        result = {}
        r, c, _ = current
        result[(r, c)] = rot

        while current in came_from:
            prev, rrot = came_from[current]
            pr, pc, _ = prev
            result[(pr, pc)] = rrot
            current = prev

        return result