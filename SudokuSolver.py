import random
from collections import Counter
from functools import reduce
from ReservoirSampling import ReservoirSampler
from DLX import DLX
import copy
import time
class SudokuSolver:
    def __init__(self):
        self.puzzle = [[0] * 9 for _ in range(9)]

    def gen_puzzle(self, nremain=30):
        def gen_3x3(mat, start_row, start_col):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for i in range(3):
                for j in range(3):
                    mat[start_row + i][start_col + j] = nums[i*3 + j]
        gen_3x3(self.puzzle, 0, 0)
        gen_3x3(self.puzzle, 3, 3)
        gen_3x3(self.puzzle, 6, 6)

        while not self.solve():     # Generate a complete valid puzzle
            pass

        sampler = ReservoirSampler(nremain)
        for i in range(9):
            for j in range(9):
                sampler.take((i, j))

        remain_coords = set(sampler.arr)
        self.puzzle = [[self.puzzle[i][j] if (i, j) in remain_coords else 0 for j in range(9)] for i in range(9) ]

        return self.puzzle

    def is_valid(self, row, col):
        rstart = (row // 3) * 3
        cstart = (col // 3) * 3

        mat = [[self.puzzle[i][j] for j in range(cstart, cstart + 3)] for i in range(rstart, rstart + 3)]
        flatten = lambda l: [item for sublist in l for item in sublist]
        mat = flatten(mat)

        cnt_row = Counter(self.puzzle[row])
        cnt_col = Counter([self.puzzle[r][col] for r in range(9)])
        cnt_mat = Counter(mat)

        return reduce(lambda a, b: a and b, flatten([[n not in cnt or cnt[n] == 1 for n in range(1, 10)] for cnt in [cnt_row, cnt_col, cnt_mat]]))

    def solve(self):
        pass

    def pp_puzzle(self, puz):
        s = [[str(e) for e in row] for row in puz]
        mat = ['  '.join(row) for row in s]
        print('\n'.join(mat))

class BacktrackSolver(SudokuSolver):
    def __init__(self):
        super().__init__()

    def solve(self):
        def dfs(i, j):
            if self.puzzle[i][j] != 0:      # The cell is already filled
                if j < 8:
                    return dfs(i, j+1)
                elif i < 8:
                    return dfs(i+1, 0)
                else:                       # Finished
                    return True
            else:                           # The cell is not yet filled
                for n in range(1, 10):
                    self.puzzle[i][j] = n
                    if self.is_valid(i, j): # Proceed to next search
                        ni, nj = i, j
                        if j < 8:
                            nj = j + 1
                        elif i < 8:
                            ni = i + 1
                            nj = 0
                        else:
                            return True

                        if dfs(ni, nj):
                            return True
                self.puzzle[i][j] = 0
                return False
        return dfs(0, 0)

class DLXSolver(SudokuSolver):

    def __init__(self):
        super().__init__()
        self.allSolutions = []

    def sudoku_to_exactcover(self, puzzle):
        # The exact cover matrix R
        # R[a * b * c][k * 9 * 9 + i * j] == 1 means:
        #    k == 0: Fill in the cell[a][b] with value c, and the constraint 0 "the cell i=a, j=b is filled" is satisfied
        #    k == 1: Fill in the cell[a][b] with value c, and the constraint 1 "the row i=a contains the value j=c" is satisfied
        #    k == 2: Fill in the cell[a][b] with value c, and the constraint 2 "the col i=b contains the value j=c" is satisfied
        #    k == 3: Fill in the cell[a][b] with value c, and the constraint 3 "the small grid i=(a/3)*3 + b/3 contains the value j=c" is satisfied

        def get_idx(r, c, n):
            return r * 9 * 9 + c * 9 + n + 1

        def add_constraints(r, c, n):
            R[get_idx(r, c, n)][colbases[0] + r * 9 + c] = 1  # Constraint 0
            R[get_idx(r, c, n)][colbases[1] + r * 9 + n] = 1  # Constraint 1
            R[get_idx(r, c, n)][colbases[2] + c * 9 + n] = 1  # Constraint 2
            R[get_idx(r, c, n)][colbases[3] + ((r // 3) * 3 + c // 3) * 9 + n] = 1  # Constraint 3

        R = [[0 for __ in range(9 * 9 * 4)] for _ in range(9 * 9 * 9 + 1)]

        # Column nodes
        for i in range(9 * 9 * 4):
            R[0][i] = 1

        colbases = [0, 1 * 9 * 9, 2 * 9 * 9, 3 * 9 * 9]
        for r in range(9):
            for c in range(9):
                if puzzle[r][c] != 0:   # Cell is already filled
                    n = puzzle[r][c] - 1
                    add_constraints(r, c, n)
                else:
                    for n in range(9):
                        add_constraints(r, c, n)
        return R

    def solution_to_sudoku(self, solution):
        puzzle = [[0] * 9 for _ in range(9)]
        for row_node in solution:
            rown = row_node.rowId
            rown -= 1
            r = rown // (9 * 9)
            rown %= 9 * 9
            c = rown // 9
            rown %= 9
            n = rown
            puzzle[r][c] = n + 1
        self.puzzle = puzzle
        return puzzle

    def solve(self):
        probMat = self.sudoku_to_exactcover(puzzle=self.puzzle)
        dlx = DLX(probMat)
        dlx.createToridolMatrix()
        if not dlx.search(0, verbose=False, all=True):
            return False
        self.allSolutions = dlx.allSolutions
        return True

if __name__ == '__main__':

    start = time.time()
    btSolver = BacktrackSolver()
    print("Here's the puzzle:")
    btSolver.pp_puzzle(btSolver.gen_puzzle())
    puzzle = copy.deepcopy(btSolver.puzzle)
    print("Solving puzzle using BacktrackSolver...")
    print("Solved!" if btSolver.solve() else "No solution!")
    btSolver.pp_puzzle(btSolver.puzzle)
    end = time.time()
    print("btSolver takes {}".format(end - start))

    start = time.time()
    dlxSolver = DLXSolver()
    dlxSolver.puzzle = puzzle
    print("Here's the puzzle again:")
    dlxSolver.pp_puzzle(dlxSolver.puzzle)
    print('Solved All!' if dlxSolver.solve() else "No solution!")
    for sol in dlxSolver.allSolutions:
        print("Here's one solution:")
        dlxSolver.pp_puzzle(dlxSolver.solution_to_sudoku(sol))
    end = time.time()
    print("dlxSolver takes {}".format(end - start))
