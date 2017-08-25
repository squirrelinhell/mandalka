
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
class Resource:
    def __init__(self, n):
        self.opened = 0
    def __enter__(self):
        assert mandalka.is_node(self)
        self.opened += 1
        return self
    def __exit__(self, type, value, traceback):
        self.opened -= 1

@mandalka.node
class Another:
    def __init__(self, resource):
        assert mandalka.is_node(self)
        assert mandalka.describe(resource) == "Resource(10)"
        self.opened = resource.opened

with Resource(10) as r:
    a = Another(r)

assert a.opened == 1

assert hasattr(Resource, "__enter__")
assert not hasattr(Another, "__enter__")
