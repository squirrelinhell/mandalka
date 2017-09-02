
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

from mandalka import node, is_node, describe

def fails(f):
    try:
        f()
        return False
    except:
        return True

@node
class Node:
    def __init__(self, a=None, b=None):
        self.a, self.b = a, b

@node
class Another:
    def __init__(self, a=None, b=None):
        pass

class NotANode:
    def __init__(self, a=None, b=None):
        pass

assert is_node(Node())
assert not is_node(NotANode())

assert fails(lambda: Node(NotANode(1, 2), 3))
assert not fails(lambda: NotANode(Node(1, 2), 3))

assert fails(lambda: Node(Node(NotANode(1, 2), 3)))
assert not fails(lambda: Node(Node(Node(3, 4), Node(3))))

modify_args = [1, {2: [3, 4]}]

nodes = [
    Node(*modify_args),
    Node(123, b=[]),
    Node({"b": 1, "a": 2}, b=Another({})),
    Another(a=["a", b"b"]),
    Node({1: 2, "a": ["b"]}),
    Node((3.14, (0.00159, 0.1 * 0.1))),
    Node(set([5, 2, 3, 4, 1]))
]

modify_args[1][2].append(5)
assert repr(nodes[0].b) == "{2: [3, 4]}"

for n in nodes:
    print(describe(n, 0))
    print(describe(n))
    print(describe(n, 2))
