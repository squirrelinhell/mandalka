#!/usr/bin/env python3

# Example 1

import mandalka

@mandalka.node
class Fib():
    def __init__(self, n):
        if n <= 1:
            self.n = n
        else:
            self.n = Fib(n-1).n + Fib(n-2).n

print(Fib(100).n) # prints '354224848179261915075'

# Example 2

import os
import numpy as np

@mandalka.node
class Data():
    def __init__(self, data):
        print("Computing...")
        self.squares = np.square(data)

@mandalka.node
class Model():
    def __init__(self, data):
        path = mandalka.unique_id(self) + ".npy"
        if os.path.exists(path):
            self.weights = np.load(path)
        else:
            self.weights = data.squares * 10
            np.save(path, self.weights)

model = Model(Data([1, 2, 3]))

# This will print 'Computing...' only for the first time:
print(model.weights)
