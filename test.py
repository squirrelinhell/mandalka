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

import time
import numpy as np

import mandalka
import debug

@mandalka.node
class Dataset():
    def __init__(self, start, end):
        if end - start <= 1:
            print("Computing dataset: [%s]..." % start)
            self.x = np.array([start])
            time.sleep(1)
            self.y = self.x * self.x
            print("Finished computing dataset: [%s]" % start)
        else:
            half = start + (end - start) // 2
            a, b = mandalka.threads(
                Dataset(start, half),
                Dataset(half, end),
            )
            self.x = np.concatenate((a.x, b.x))
            self.y = np.concatenate((a.y, b.y))

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def __load__(self, path):
        data = np.load(path + "/data.npz")
        self.x = data["x"]
        self.y = data["y"]
        print("Loaded dataset: %s" % self.x)

    def __save__(self, path):
        np.savez(path + "/data.npz", x=self.x, y=self.y)

@mandalka.node
class Model():
    def __init__(self, dataset):
        self.weights = dataset.get_y()
        print("Computed model: %s" % self.weights)

    def get_weights(self):
        return self.weights

    def __load__(self, path):
        data = np.load(path + "/data.npz")
        self.weights = data["w"]
        print("Loaded model: %s" % self.weights)

    def __save__(self, path):
        np.savez(path + "/data.npz", w = self.weights)

Model(Dataset(0, 4)).get_weights()
Model(Dataset(0, 5)).get_weights()
Model(Dataset(0, 4)).get_weights()
