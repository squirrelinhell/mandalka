
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
import mandalka
import numpy as np

@mandalka.node
class Squares():
    waiting = 0

    def __init__(self, start, end):
        if end - start <= 1:
            # Wait until all threads get here
            Squares.waiting += 1
            while Squares.waiting < 4:
                time.sleep(0.01)

            self.x = np.array([start * start])
        else:
            half = start + (end - start) // 2
            a, b = mandalka.threads(
                Squares(start, half),
                Squares(half, end),
            )
            self.x = np.concatenate((a.x, b.x))

    def __load__(self, path):
        self.x = np.load(path + "/x.npy") * 2

    def __save__(self, path):
        np.save(path + "/x.npy", self.x)

assert (Squares(0, 4).x == [0, 1, 4, 9]).all()
assert (Squares(0, 4).x == [0, 2, 8, 18]).all()
