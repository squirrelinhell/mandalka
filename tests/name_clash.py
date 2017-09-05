
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
class Foo:
    def set_a(self, value):
        self.a = value

foo = Foo()
assert str(foo) == "<Foo cf5448839e9bd525>"

foo.a = 10
assert foo.a == 10
assert sorted(list(foo.__dict__)) == ["a"]

assert not hasattr(foo, "_mandalka_node")
foo._mandalka_node = 20
assert foo._mandalka_node == 20
assert sorted(list(foo.__dict__)) == ["_mandalka_node", "a"]

foo.set_a(30)
assert foo.a == 30

assert mandalka.unique_id(foo) == "cf5448839e9bd525"
assert str(foo) == "<Foo cf5448839e9bd525>"

@mandalka.node
class Foo:
    def set_b(self, value):
        self.b = value

foo = Foo()
foo.set_b(40)
assert foo.b == 40
