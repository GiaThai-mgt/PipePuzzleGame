class PipeGameLogic:
    # Định nghĩa các loại ống
    # Defines pipe types
    PIPE_STRAIGHT = 1
    PIPE_L_SHAPE = 2
    PIPE_T_SHAPE = 3

    # Hướng
    # Directions
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3

    # Định nghĩa kết nối của các loại ống dựa trên hướng xoay
    # Pipe connection definitions based on rotation
    PIPE_CONNECTIONS = {
        PIPE_STRAIGHT: {
            0: (TOP, BOTTOM),  # Ống thẳng đứng | (Vertical straight pipe)
            1: (LEFT, RIGHT),  # Ống thẳng ngang -- (Horizontal straight pipe)
            2: (TOP, BOTTOM),  # Ống thẳng đứng | (Vertical straight pipe)
            3: (LEFT, RIGHT)   # Ống thẳng ngang -- (Horizontal straight pipe)
        },
        PIPE_L_SHAPE: {
            0: (TOP, RIGHT),   # Ống chữ L góc trên phải ┏ (Top-right L-pipe)
            1: (RIGHT, BOTTOM),# Ống chữ L góc dưới phải ┓ (Right-bottom L-pipe)
            2: (BOTTOM, LEFT), # Ống chữ L góc dưới trái ┛ (Bottom-left L-pipe)
            3: (LEFT, TOP)     # Ống chữ L góc trên trái ┗ (Left-top L-pipe)
        },
        PIPE_T_SHAPE: {
            0: (TOP, LEFT, RIGHT),    # Ống chữ T không có cửa dưới ┳ (T-pipe without bottom opening)
            1: (TOP, RIGHT, BOTTOM),  # Ống chữ T không có cửa trái ┫ (T-pipe without left opening)
            2: (RIGHT, BOTTOM, LEFT), # Ống chữ T không có cửa trên ┻ (T-pipe without top opening)
            3: (BOTTOM, LEFT, TOP)    # Ống chữ T không có cửa phải ┣ (T-pipe without right opening)
        }
    }

    # Ánh xạ chuỗi hướng sang hằng số hướng
    # Mapping string directions to direction constants
    DIRECTION_MAP = {
        "TOP": TOP,
        "RIGHT": RIGHT,
        "BOTTOM": BOTTOM,
        "LEFT": LEFT
    }

    def __init__(self, size=5):
        # Ví dụ màn chơi 5x5
        # Example 5x5 level
        level_1 = {
            "size": 5,
            "grid_type": [
                [self.PIPE_STRAIGHT, self.PIPE_L_SHAPE, 0, 0, self.PIPE_STRAIGHT],
                [0, self.PIPE_STRAIGHT, self.PIPE_STRAIGHT, self.PIPE_L_SHAPE, 0],
                [0, 0, self.PIPE_L_SHAPE, self.PIPE_STRAIGHT, 0],
                [0, self.PIPE_STRAIGHT, 0, self.PIPE_STRAIGHT, self.PIPE_STRAIGHT],
                [self.PIPE_L_SHAPE, self.PIPE_L_SHAPE, 0, 0, self.PIPE_STRAIGHT]
            ],
            "grid_rotation": [
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0]
            ],
            "start_pos": (0, 0),
            "end_pos": (4, 4),
            "source_direction": "TOP"
        }
        self.load_level(level_1)


    def rotate_pipe(self, r, c):
        """Xoay ống tại vị trí r, c thêm 90 độ"""
        self.grid_rotation[r][c] = (self.grid_rotation[r][c] + 1) % 4
        print(f"Ô ({r},{c}) hiện đang ở hướng: {self.grid_rotation[r][c]}")

    def check_connection(self, node1, node2):
        """
        Kiểm tra xem hai ô ống nước liền kề có nối thông với nhau không.
        Checks if two adjacent pipe cells are connected.
        node1, node2: tuple (r, c) - tọa độ của ô ống nước.
        node1, node2: tuple (r, c) - coordinates of the pipe cells.
        """
        r1, c1 = node1
        r2, c2 = node2

        # Đảm bảo hai nút liền kề
        # Ensure the two nodes are adjacent
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return False

        # Kiểm tra giới hạn của lưới
        # Check grid boundaries
        if not (0 <= r1 < self.size and 0 <= c1 < self.size and
                0 <= r2 < self.size and 0 <= c2 < self.size):
            return False

        pipe1_type = self.grid_type[r1][c1]
        pipe1_rotation = self.grid_rotation[r1][c1]
        pipe2_type = self.grid_type[r2][c2]
        pipe2_rotation = self.grid_rotation[r2][c2]

        # Nếu một trong hai ô là ô trống (type 0), không có kết nối
        # If one of the cells is empty (type 0), there's no connection
        if pipe1_type == 0 or pipe2_type == 0:
            return False

        # Xác định hướng từ node1 đến node2 và ngược lại
        # Determine direction from node1 to node2 and vice versa
        direction_to_node2 = -1
        direction_to_node1 = -1

        if r1 == r2: # Cùng hàng (trái/phải)
            if c2 > c1: # node2 bên phải node1
                direction_to_node2 = self.RIGHT
                direction_to_node1 = self.LEFT
            else: # node2 bên trái node1
                direction_to_node2 = self.LEFT
                direction_to_node1 = self.RIGHT
        elif c1 == c2: # Cùng cột (trên/dưới)
            if r2 > r1: # node2 bên dưới node1
                direction_to_node2 = self.BOTTOM
                direction_to_node1 = self.TOP
            else: # node2 bên trên node1
                direction_to_node2 = self.TOP
                direction_to_node1 = self.BOTTOM
        
        # Lấy các cửa mở của từng ống
        # Get open sides of each pipe
        opens_pipe1 = self.PIPE_CONNECTIONS[pipe1_type][pipe1_rotation]
        opens_pipe2 = self.PIPE_CONNECTIONS[pipe2_type][pipe2_rotation]

        # Kiểm tra xem node1 có mở về phía node2 không
        # Check if node1 opens towards node2
        node1_connects_to_node2 = direction_to_node2 in opens_pipe1
        
        # Kiểm tra xem node2 có mở về phía node1 không
        # Check if node2 opens towards node1
        node2_connects_to_node1 = direction_to_node1 in opens_pipe2

        return node1_connects_to_node2 and node2_connects_to_node1

    def get_valid_neighbors(self, r, c):
        """
        Trả về danh sách các ô liền kề (node) có kết nối thông mạch với ô (r, c) hiện tại.
        Returns a list of adjacent cells (nodes) that are currently connected to the current cell (r, c).
        """
        neighbors = []
        # Các hướng di chuyển có thể: (dr, dc)
        # Possible movements: (dr, dc)
        movements = [(-1, 0), (1, 0), (0, -1), (0, 1)] # (TOP, BOTTOM, LEFT, RIGHT)

        for dr, dc in movements:
            nr, nc = r + dr, c + dc

            # Kiểm tra xem ô liền kề có nằm trong giới hạn lưới không
            # Check if the neighbor cell is within grid boundaries
            if 0 <= nr < self.size and 0 <= nc < self.size:
                # Kiểm tra kết nối giữa ô hiện tại và ô liền kề
                # Check connection between current cell and neighbor cell
                if self.check_connection((r, c), (nr, nc)):
                    neighbors.append((nr, nc))
        return neighbors

    def check_win(self):
        """
        Kiểm tra xem có đường ống thông mạch từ start_pos đến end_pos không
        sử dụng thuật toán DFS, có tính đến source_direction.
        Checks if there's a continuous pipe path from start_pos to end_pos
        using DFS, considering source_direction.
        """
        # Nếu start_pos hoặc end_pos là ô trống, không thể thắng
        # If start_pos or end_pos is an empty cell, cannot win
        if self.grid_type[self.start_pos[0]][self.start_pos[1]] == 0 or \
           self.grid_type[self.end_pos[0]][self.end_pos[1]] == 0:
            return False

        visited = set()
        stack = [] # (current_node, direction_water_entered_this_node_from)

        start_r, start_c = self.start_pos
        
        # Lấy hướng nước chảy vào ô bắt đầu từ source_direction
        # Get the direction water enters the start cell from source_direction
        initial_entry_direction = self.DIRECTION_MAP.get(self.source_direction)
        if initial_entry_direction is None:
            print(f"Lỗi: source_direction \'{self.source_direction}\' không hợp lệ.")
            return False

        # Kiểm tra xem ống tại start_pos có cửa mở về hướng nước chảy vào không
        # Check if the pipe at start_pos has an opening in the direction water enters from
        start_pipe_type = self.grid_type[start_r][start_c]
        start_pipe_rotation = self.grid_rotation[start_r][start_c]
        start_pipe_openings = self.PIPE_CONNECTIONS[start_pipe_type][start_pipe_rotation]

        if initial_entry_direction not in start_pipe_openings:
            return False # Ống bắt đầu không mở đúng hướng nguồn nước

        stack.append((self.start_pos, initial_entry_direction))
        visited.add(self.start_pos)

        while stack:
            (r, c), entry_direction_to_current_node = stack.pop()

            if (r, c) == self.end_pos:
                return True

            current_pipe_type = self.grid_type[r][c]
            current_pipe_rotation = self.grid_rotation[r][c]
            current_pipe_openings = self.PIPE_CONNECTIONS[current_pipe_type][current_pipe_rotation]

            # Duyệt qua tất cả các cửa mở của ống hiện tại
            # Iterate through all openings of the current pipe
            for outgoing_direction_from_current_node in current_pipe_openings:
                # Nếu cửa mở này là nơi nước đã chảy vào, bỏ qua
                # If this opening is where the water came from, skip it
                if (outgoing_direction_from_current_node == self.TOP and entry_direction_to_current_node == self.BOTTOM) or \
                   (outgoing_direction_from_current_node == self.BOTTOM and entry_direction_to_current_node == self.TOP) or \
                   (outgoing_direction_from_current_node == self.LEFT and entry_direction_to_current_node == self.RIGHT) or \
                   (outgoing_direction_from_current_node == self.RIGHT and entry_direction_to_current_node == self.LEFT):
                    continue
                
                # Xác định tọa độ của ô liền kề theo hướng chảy ra
                # Determine coordinates of the adjacent cell based on the outgoing direction
                dr, dc = 0, 0
                if outgoing_direction_from_current_node == self.TOP: dr = -1
                elif outgoing_direction_from_current_node == self.BOTTOM: dr = 1
                elif outgoing_direction_from_current_node == self.LEFT: dc = -1
                elif outgoing_direction_from_current_node == self.RIGHT: dc = 1
                
                nr, nc = r + dr, c + dc
                next_node = (nr, nc)

                # Kiểm tra giới hạn lưới và ô đã thăm
                # Check grid boundaries and if the cell has been visited
                if not (0 <= nr < self.size and 0 <= nc < self.size) or next_node in visited:
                    continue

                # Hướng nước chảy vào ô liền kề sẽ là hướng ngược lại của outgoing_direction
                # The direction water enters the next cell will be the opposite of outgoing_direction
                entry_direction_to_next_node = -1
                if outgoing_direction_from_current_node == self.TOP: entry_direction_to_next_node = self.BOTTOM
                elif outgoing_direction_from_current_node == self.RIGHT: entry_direction_to_next_node = self.LEFT
                elif outgoing_direction_from_current_node == self.BOTTOM: entry_direction_to_next_node = self.TOP
                elif outgoing_direction_from_current_node == self.LEFT: entry_direction_to_next_node = self.RIGHT
                
                # Kiểm tra kết nối giữa ô hiện tại và ô liền kề
                # Check connection between current cell and neighbor cell
                if self.check_connection((r,c), next_node):
                    stack.append((next_node, entry_direction_to_next_node))
                    visited.add(next_node)
        
        return False # Không tìm thấy đường đi

    def load_level(self, level_data):
        """Tải dữ liệu màn chơi, thiết lập grid_type và grid_rotation
        Load level data, set up grid_type and grid_rotation
        """
        self.size = level_data["size"]
        self.grid_type = level_data["grid_type"]
        self.grid_rotation = level_data["grid_rotation"]
        self.start_pos = level_data.get("start_pos", (0, 0))
        self.end_pos = level_data.get("end_pos", (self.size - 1, self.size - 1))
        self.source_direction = level_data.get("source_direction", "TOP")