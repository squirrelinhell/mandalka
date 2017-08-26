#!/usr/bin/env python3

# ===============================
#           Example 1
# ===============================

import mandalka

@mandalka.node
class Fib:
    def __init__(self, n):
        if n <= 1:
            self.n = n
        else:
            self.n = Fib(n-1).n + Fib(n-2).n

print(Fib(100).n) # prints "354224848179261915075"

# ===============================
#           Example 2
# ===============================

import os
import numpy as np

@mandalka.node
class Data:
    def __init__(self, size):
        # This code will not run if Model doesn't need it
        print("Computing...")
        self.squares = np.square(np.arange(size))

@mandalka.node
class Model:
    def __init__(self, data):
        path = mandalka.unique_id(self) + ".npy"
        if os.path.exists(path):
            self.weights = np.load(path)
        else:
            self.weights = data.squares * 10
            np.save(path, self.weights)

model = Model(Data(5))

# Prints "Computing..." only for the first time this script is run:
print(model.weights)

# ===============================
#           Example 3
# ===============================

@mandalka.node
class S:
    def __init__(*_):
        pass

two = S(S(0))
three = S(S(S(0)))
assert three == S(two)

def add(a, b):
    counter = 0
    while counter != b:
        a = S(a)
        counter = S(counter)
    return a

five = add(two, three)
print(mandalka.describe(five, -1)) # prints "S(S(S(S(S(0)))))"
