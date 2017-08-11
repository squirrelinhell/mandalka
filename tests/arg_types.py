
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

@node(save=False)
class Node():
    def __init__(self, a=None, b=None):
        pass

class NotANode():
    def __init__(self, a=None, b=None):
        pass

assert is_node(Node())
assert not is_node(NotANode())

assert fails(lambda: Node(NotANode(1, 2), 3))
assert not fails(lambda: NotANode(Node(1, 2), 3))

assert fails(lambda: Node(Node(NotANode(1, 2), 3)))
assert not fails(lambda: Node(Node(Node(3, 4), Node(3))))

assert fails(lambda: Node(10.0))
assert not fails(lambda: Node(10))

assert describe(Node(123, b=[])) == "Node(123, b=[])"
assert describe(Node(a=["a", b"b"])) == "Node(a=['a', b'b'])"
assert describe(Node({1: 2, "a": ["b"]})) == "Node({1: 2, 'a': ['b']})"
assert describe(Node((1,), (1, 2))) == "Node((1,), (1, 2))"
