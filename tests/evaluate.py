
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

import mandalka
import gc

@mandalka.node(gc=True)
class Increment:
    def __init__(self, a):
        if isinstance(a, int):
            self.a = a + 1
        else:
            self.a = a.a + 1
        print("Create: %s" % self.a)
    def __del__(self):
        print("Delete: %s" % self.a)

print("[nothing]")
Increment(Increment(0))
gc.collect()

print("[simple]")
a = Increment(Increment(0))
a.a
a = Increment(0).a
gc.collect()

print("[evaluate]")
a = Increment(Increment(0))
mandalka.evaluate(a)
a = Increment(0).a
gc.collect()
