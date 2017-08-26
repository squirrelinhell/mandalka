
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
class Singleton:
    pass

@mandalka.node
class Another:
    def __init__(*_):
        pass

s1 = Singleton()
s2 = Singleton()
s1.value = 7
assert s2.value == 7

assert s1 == s2
assert not s1 != s2

assert Another() != s1
assert not s2 == Another()

assert Another(Another()) == Another(Another())
assert not Another(Another()) == Another(Another(Another()))

@mandalka.node
class WeirdEqual:
    foo = 0
    def __init__(self):
        WeirdEqual.foo += 1
    def __eq__(self, other):
        return other + str(WeirdEqual.foo)

assert "a1" == (WeirdEqual() == "a")

class BaseEqual:
    foo = 0
    def __init__(self):
        BaseEqual.foo += 1
    def __eq__(self, other):
        return other + str(BaseEqual.foo)

@mandalka.node
class InheritEqual(BaseEqual):
    def __init__(self, *_):
        super().__init__()

assert "b1" == (InheritEqual(0) == "b")

InheritEqual(1)
InheritEqual(2) == "x"
InheritEqual(3) == "y"
assert BaseEqual.foo == 3
