class PipeGame:
    def __init__(self):
        # Ma trận 5x5: 0 là trống, 1 là ống thẳng, 2 là ống cong
        self.grid = [[1, 2, 0, 0, 1],
                     [0, 1, 1, 2, 0],
                     [0, 0, 2, 1, 0],
                     [0, 1, 0, 1, 1],
                     [2, 2, 0, 0, 1]]
        
    def rotate_pipe(self, x, y):
        print(f"Người 1 sẽ viết code xoay ống tại {x}, {y} ở đây")