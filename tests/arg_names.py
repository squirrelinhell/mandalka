
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

from mandalka import node, evaluate, describe, argument

def fails(f):
    try:
        f()
        return False
    except:
        return True

@node
class Node:
    def __init__(self, a=1, b=2):
        pass

assert Node() == Node(1, 2)
assert Node(3) == Node(3, 2)
assert Node(3) == Node(a=3)
assert Node(a=4, b=5) == Node(4, 5)
assert Node(1, b=7) == Node(b=7)
assert fails(lambda: Node(c=1))
assert fails(lambda: Node(1, a=1))
assert describe(Node("a", "b")) == "Node(a='a', b='b')"

assert argument(Node("x", "y"), "a") == "x"
assert fails(lambda: argument(Node("x", "y"), "c"))

@node
class VarNode:
    def __init__(self, a, *b, c=3):
        print(a, b, c)

assert VarNode(1, c=3) == VarNode(1)
assert VarNode(a=1) == VarNode(1)
assert fails(lambda: VarNode())
assert describe(VarNode("a", "b")) == "VarNode('a', 'b', c=3)"

evaluate(VarNode(1))
evaluate(VarNode(1, 2))
evaluate(VarNode(1, 2, 3))
evaluate(VarNode(1, c=5))
evaluate(VarNode(1, 2, c=5))
evaluate(VarNode(1, 2, 3, c=5))

@node
class VarOnlyNode:
    def __init__(self, a, *, b):
        pass

assert VarOnlyNode(a=1, b=2) == VarOnlyNode(1, b=2)
assert fails(lambda: VarOnlyNode(1, 2))
assert fails(lambda: VarOnlyNode(1, 2, b=2))
assert describe(VarOnlyNode("a", b="b")) == "VarOnlyNode(a='a', b='b')"
