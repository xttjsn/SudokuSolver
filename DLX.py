# DLX: Dancing Links
import copy
class Node:
    def __init__(self):
        self.left = None
        self.right = None
        self.up = None
        self.down = None
        self.column = None
        self.rowId = -1
        self.colId = -1
        self.nodeCount = 0

class DLX:
    def __init__(self, probMat):
        self.header = Node()
        self.probMat = probMat    # The first row of probMat is always 1
        self.nRow = len(probMat)
        self.nCol = len(probMat[0])
        self.mat = [[Node() for __ in range(self.nCol)]  for _ in range(self.nRow)]
        self.solutions = []
        self.allSolutions = []

    def getRight(self, i):
        return (i + 1) % self.nCol

    def getLeft(self, i):
        return (i - 1) % self.nCol

    def getUp(self, i):
        return (i - 1) % self.nRow

    def getDown(self, i):
        return (i + 1) % self.nRow

    def createToridolMatrix(self):
        for i in range(self.nRow):
            for j in range(self.nCol):
                if self.probMat[i][j] == 1:

                    if i > 0:
                        self.mat[0][j].nodeCount += 1

                    self.mat[i][j].column = self.mat[0][j]
                    self.mat[i][j].rowId = i;
                    self.mat[i][j].colId = j;

                    # Link with neighbors
                    a, b, cond = i, j, True
                    while cond:
                        b = self.getLeft(b)
                        cond = not self.probMat[a][b] and b != j
                    self.mat[i][j].left = self.mat[i][b];

                    a, b, cond = i, j, True
                    while cond:
                        b = self.getRight(b)
                        cond = not self.probMat[a][b] and b != j
                    self.mat[i][j].right = self.mat[i][b];

                    a, b, cond = i, j, True
                    while cond:
                        a = self.getUp(a)
                        cond = not self.probMat[a][b] and a != i
                    self.mat[i][j].up = self.mat[a][j];

                    a, b, cond = i, j, True
                    while cond:
                        a = self.getDown(a)
                        cond = not self.probMat[a][b] and a != i
                    self.mat[i][j].down = self.mat[a][j];

        self.header.right = self.mat[0][0];
        self.header.left = self.mat[0][self.nCol - 1];

        self.mat[0][0].left = self.header
        self.mat[0][self.nCol - 1].right = self.header

    def cover(self, targetNode):
        colNode = targetNode.column

        # Unlink column header from its neighbor
        colNode.left.right = colNode.right
        colNode.right.left = colNode.left

        # Move down the column and remove each row
        rowNode = colNode.down
        while rowNode != colNode:
            rightNode = rowNode.right
            while rightNode != rowNode:
                rightNode.up.down = rightNode.down
                rightNode.down.up = rightNode.up

                self.mat[0][rightNode.colId].nodeCount -= 1
                rightNode = rightNode.right
            rowNode = rowNode.down

    def uncover(self, targetNode):
        colNode = targetNode.column

        rowNode = colNode.up
        while rowNode != colNode:
            leftNode = rowNode.left
            while leftNode != rowNode:
                leftNode.up.down = leftNode
                leftNode.down.up = leftNode

                self.mat[0][leftNode.colId].nodeCount += 1
                leftNode = leftNode.left
            rowNode = rowNode.up

        colNode.left.right = colNode
        colNode.right.left = colNode

    def getMinColumn(self):
        h = self.header
        min_col = h.right
        h = h.right.right
        cond = True
        while cond:
            if h.nodeCount < min_col.nodeCount:
                min_col = h
            h = h.right
            cond = h != self.header
        return min_col

    def print_solution(self):
        print('Printing Solutions: ')
        print(' '.join([str(sol_node.rowId) for sol_node in self.solutions]))

    def search(self, k, verbose=True, all=False):
        if self.header.right == self.header:
            if verbose:
                self.print_solution()
            self.allSolutions.append(copy.deepcopy(self.solutions))
            return True

        col = self.getMinColumn()
        self.cover(col)

        row = col.down
        while row != col:
            self.solutions.append(row)
            right = row.right
            while right != row:
                self.cover(right)
                right = right.right
            if self.search(k + 1, verbose=verbose, all=all) and not all:
                return True

            self.solutions.pop(-1)

            col = row.column
            left = row.left
            while left != row:
                self.uncover(left)
                left = left.left

            row = row.down

        self.uncover(col)
        return len(self.allSolutions) > 0

if __name__ == '__main__':
    probMat = [[1, 1, 1, 1, 1, 1, 1], # Column
               [1, 0, 0, 1, 0, 0, 1], # row 1
               [1, 0, 0, 1, 0, 0, 0], # row 2
               [0, 0, 0, 1, 1, 0, 1], # row 3
               [0, 0, 1, 0, 1, 1, 0], # row 4
               [0, 1, 1, 0, 0, 1, 1], # row 5
               [0, 1, 0, 0, 0, 0, 1], # row 6
               [1, 0, 0, 1, 0, 0, 0]] # row 7

    dlx = DLX(probMat)
    dlx.createToridolMatrix()
    dlx.search(0)
