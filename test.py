#!/usr/bin/env python3

# Copyright (c) 2017 SquirrelInHell
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np

import mandalka
import debug

@mandalka.node
class Dataset():
    def __init__(self, size):
        print("Computing dataset")
        self.x = np.arange(size)
        self.y = np.arange(size - 1, -1, -1)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def __load__(self, path):
        print("Loading dataset")
        data = np.load(path + "/data.npz")
        self.x = data["x"]
        self.y = data["y"]

    def __save__(self, path):
        np.savez(path + "/data.npz", x=self.x, y=self.y)

@mandalka.node
class Model():
    def __init__(self, dataset):
        print("Computing model")
        self.weights = dataset.get_y() - dataset.get_x()

    def predict(self, x):
        return x + self.weights

    def __load__(self, path):
        print("Loading model")
        data = np.load(path + "/data.npz")
        self.weights = data["w"]

    def __save__(self, path):
        np.savez(path + "/data.npz", w = self.weights)

print(Model(Dataset(5)).predict([100, 0, 0, 0, 0]))
