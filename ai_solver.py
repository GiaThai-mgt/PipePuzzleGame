import heapq

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
        g_score = {start_state: 0}
        
        counter = 1
        
        while pq:
            f, _, current_state = heapq.heappop(pq)
            r, c, entry_dir = current_state
            
            # Check win condition -> Reconstruct path
            if (r, c) == (end_r, end_c):
                # Check xem đầu ra có hở để nối không
                cur_type = self.logic.grid_type[r][c]
                valid_end_rot = -1
                for rot in range(4):
                    if entry_dir in self.logic.PIPE_CONNECTIONS[cur_type][rot]:
                        valid_end_rot = rot
                        break
                if valid_end_rot != -1:
                    return self.reconstruct_path(came_from, current_state, valid_end_rot)
            
            cur_type = self.logic.grid_type[r][c]
            
            for rot in range(4):
                if cur_type == self.logic.PIPE_ONE_WAY and rot != self.logic.grid_rotation[r][c]:
                    continue
                    
                cur_opens = self.logic.PIPE_CONNECTIONS[cur_type][rot]
                if entry_dir not in cur_opens:
                    continue
                
                # Check ONE_WAY rule
                if cur_type == self.logic.PIPE_ONE_WAY:
                    allowed_entry = None
                    if rot == 0: allowed_entry = self.logic.BOTTOM
                    elif rot == 1: allowed_entry = self.logic.LEFT
                    elif rot == 2: allowed_entry = self.logic.TOP
                    elif rot == 3: allowed_entry = self.logic.RIGHT
                    
                    if entry_dir != allowed_entry:
                        continue
                        
                for outgoing_dir in cur_opens:
                    if outgoing_dir == entry_dir:
                        continue
                        
                    dr, dc = 0, 0
                    if outgoing_dir == self.logic.TOP: dr = -1
                    elif outgoing_dir == self.logic.BOTTOM: dr = 1
                    elif outgoing_dir == self.logic.LEFT: dc = -1
                    elif outgoing_dir == self.logic.RIGHT: dc = 1
                    
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < self.logic.size and 0 <= nc < self.logic.size):
                        continue
                    if self.logic.grid_type[nr][nc] == self.logic.PIPE_EMPTY:
                        continue
                        
                    next_entry_dir = -1
                    if outgoing_dir == self.logic.TOP: next_entry_dir = self.logic.BOTTOM
                    elif outgoing_dir == self.logic.BOTTOM: next_entry_dir = self.logic.TOP
                    elif outgoing_dir == self.logic.LEFT: next_entry_dir = self.logic.RIGHT
                    elif outgoing_dir == self.logic.RIGHT: next_entry_dir = self.logic.LEFT
                    
                    next_state = (nr, nc, next_entry_dir)
                    cost = g_score[current_state] + 1
                    
                    if next_state not in g_score or cost < g_score[next_state]:
                        g_score[next_state] = cost
                        # Heuristic Manhattan
                        h = abs(nr - end_r) + abs(nc - end_c)
                        heapq.heappush(pq, (cost + h, counter, next_state))
                        counter += 1
                        came_from[next_state] = (current_state, rot)
                        
        return None

    def reconstruct_path(self, came_from, current_state, end_rot):
        solution = {}
        r, c, _ = current_state
        solution[(r, c)] = end_rot
        
        while current_state in came_from:
            prev_state, prev_rot = came_from[current_state]
            pr, pc, _ = prev_state
            solution[(pr, pc)] = prev_rot
            current_state = prev_state
            
        return solution
