
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

import os
import inspect
import hashlib

def node(cls):
    class Node(object):
        _cache_dir = _getenv("MANDALKA_CACHE", "./__mandalka__")

        def __init__(self, *args):
            self.nodeid = (
                _class_id(cls) + "(" + ",".join(map(str, args)) + ")"
            )
            savedir = Node._cache_dir + "/" + self.nodeid
            if os.path.exists(savedir):
                self.o = cls.__new__(cls)
                self.o.__load__(savedir)
            else:
                self.o = cls(*args)
                os.makedirs(savedir)
                try:
                    self.o.__save__(savedir)
                finally:
                    _rmdir_if_empty(savedir)

        def __str__(self):
            return self.nodeid

        def __repr__(self):
            return self.nodeid

        def __getattr__(self, name):
            return getattr(self.o, name)

    return Node

def _class_id(cls):
    try:
        src = inspect.getsource(cls)
        h = hashlib.sha256(bytes(src, "UTF-8")).digest()
        return cls.__name__ + "_" + h[0:4].hex()
    except:
        return cls.__name__

def _rmdir_if_empty(path):
    try:
        os.rmdir(path)
    except:
        pass

def _getenv(name, default = None):
    if name in os.environ and len(os.environ[name]) >= 1:
        return os.environ[name]
    return default
