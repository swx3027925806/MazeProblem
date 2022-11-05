# 迷宫生成
# 提供两种生成模式：PRIM、DFS

import time
import random
import numpy as np
from PIL import Image
from copy import deepcopy


class MazeMap:
    def __init__(self):
        self._maze_map = None
        self.generate_time = 0

    def init_maze(self):
        self.start = np.array([0, 0])
        self.road = np.argwhere(self._maze_map == 0)
        self.end = self.road[np.argmax(np.sum(self.road * 2, axis=1))]

    def _generate_map(self, generate, size):
        self.generate_time = time.time()
        maze_map = None
        if generate == "DFS":
            maze_map = self._DFS(size)
        elif generate == "PRIM":
            maze_map = self._PRIM(size)
        self.generate_time = time.time() - self.generate_time
        print(self.generate_time)
        return maze_map

    def PRIM_det(self, maze, memory, size):
        index = np.array(memory[random.randint(0, len(memory)-1)])
        direction = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]])
        legal_direction = []
        for item in range(len(direction)):
            new_index = index + direction[item]
            if not (0 <= new_index[0] < size[0] and 0 <= new_index[1] < size[1]):
                continue
            if maze[new_index[0], new_index[1], 0] == 1:
                continue
            legal_direction.append(item)
        if len(legal_direction) > 0:
            dire = legal_direction[random.randint(0, len(legal_direction)-1)]
            new_index = index + direction[dire]
            # print(index, new_index, direction[dire])
            if 0 != np.sum(np.abs((np.array(memory) - new_index)), axis=1).min():
                memory.append(list(new_index))
                maze[index[0], index[1], dire+1] = 0
                maze[new_index[0], new_index[1], (dire + 2) % 4 + 1] = 0
                maze[new_index[0], new_index[1], 0] = 1
            else:
                memory.remove(list(index))
        else:
            memory.remove(list(index))

    def PRIM2map(self, maze):
        shape = maze.shape[:2]
        maze_map = np.ones((shape[0]*2-1, shape[1]*2-1))
        for i in range(maze_map.shape[0]):
            for j in range(maze_map.shape[1]):
                if i % 2 == 0 and j % 2 == 0:
                    maze_map[i, j] = 0
                elif i % 2 == 0 and j % 2 == 1:
                    maze_map[i, j] = maze[i//2, j//2, 1] + maze[i//2, j//2+1, 3]
                elif i % 2 == 1 and j % 2 == 0:
                    maze_map[i, j] = maze[i//2, j//2, 2] + maze[i//2+1, j//2, 4]
        return maze_map

    def _PRIM(self, size):
        size = (size[0]//2, size[1]//2)
        maze = np.empty((*size, 5), dtype=np.uint8)
        maze[:, :, 0] = 0
        maze[:, :, 1:] = 1
        maze[0, 0, 0] = 1
        memory = [[0, 0]]
        while len(memory) > 0:
            self.PRIM_det(maze, memory, size)
        return self.PRIM2map(maze)
    
    def _DFS(self, size):
        maze = np.empty((*size, 2), dtype=np.uint8)
        maze[:, :, 0] = 1
        maze[:, :, 1] = 0
        maze[0][0][0], maze[0][0][1] = 0, 1
        memory = [np.array([0, 0])]
        while len(memory) > 0:
            legal_direction = self.judge_direction(maze, memory[-1], size)
            if len(legal_direction) == 0:
                memory.pop()
            else:
                new_index = legal_direction[random.randint(0, len(legal_direction)-1)]
                memory.append(new_index)
                maze[new_index[0], new_index[1]] = np.array([0, 1])
        maze = maze[:, :, 0]
        return maze

    @staticmethod
    def judge_direction(maze, index, size):
        direction = np.array([[0, 1], [1, 0], [-1, 0], [0, -1]])
        legal_direction = []
        for item in direction:
            new_index = index + item
            if not (0 <= new_index[0] < size[0] and 0 <= new_index[1] < size[1]):
                continue
            if maze[new_index[0], new_index[1], 1] == 1:
                continue
            pass_value = 0
            for dire in direction:
                temp_index = new_index + dire
                pass_value += maze[temp_index[0], temp_index[1], 0] if temp_index[0] < size[0] and temp_index[1] < size[1] else 1
            if pass_value < 3:
                maze[new_index[0], new_index[1], 1] = 1
                continue
            legal_direction.append(new_index)
        return legal_direction

    def load_map(self, path):
        self._maze_map = np.load(path)

    def get_map(self):
        return self._maze_map
    
    def save_map(self, save_path):
        np.save(save_path, self._maze_map)

    def generate(self, generate, size):
        self._maze_map = self._generate_map(generate, size)

    def get_figure(self, figure_size=(720, 720)):
        maze = deepcopy(self._maze_map)
        maze[maze == 0] = 255
        maze[maze == 1] = 0
        maze[maze == 2] = 0
        maze[self.start[0], self.start[1]] = 128
        maze[self.end[0], self.end[1]] = 128
        maze_dis = np.zeros((maze.shape[0]+2, maze.shape[1]+2), dtype=np.uint8)
        maze_dis[1:-1, 1:-1] = maze
        maze_dis = Image.fromarray(maze_dis)
        image = maze_dis.resize(figure_size, Image.NEAREST)
        return image

    def random_dismantles_wall(self, n):
        while n > 0 and (self._maze_map > 0).sum() > n:
            x = random.randint(0, self._maze_map.shape[0]-1)
            y = random.randint(0, self._maze_map.shape[1]-1)
            if self._maze_map[x, y] > 0:
                self._maze_map[x, y] = 0
                n -= 1

if __name__ == "__main__":
    maze = MazeMap()
    maze.generate("PRIM", (32, 32))
    maze.init_maze()
    maze.get_figure()
