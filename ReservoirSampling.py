import random
class ReservoirSampler:
    def __init__(self, sz):
        self.arr = []
        self.sz = sz
        self.sz_acc = 0

    def take(self, n):
        self.sz_acc += 1
        if len(self.arr) < self.sz:
            self.arr.append(n)
        else:
            r = random.random()
            if r < self.sz / self.sz_acc:
                # Keep the new item
                idx = random.choice(list(range(self.sz)))
                self.arr.pop(idx)
                self.arr.append(n)
