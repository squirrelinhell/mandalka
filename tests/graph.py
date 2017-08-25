
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

@mandalka.node
class A:
    def __init__(self, *_):
        pass

def full_print(a):
    return "A(" + ", ".join(map(full_print, mandalka.inputs(a))) + ")"

assert full_print(A(A(A()))) == "A(A(A()))"
assert full_print(A(A(A()), A(A(A())))) == "A(A(A()), A(A(A())))"

def graph(a, indent=0):
    return ("\n".join([" "*indent + full_print(a)]
        + [graph(o, indent=indent+2) for o in mandalka.outputs(a)]))

assert "\n" + graph(A()) + "\n" == """
A()
  A(A())
    A(A(A()))
      A(A(A()), A(A(A())))
    A(A(A()), A(A(A())))
"""
