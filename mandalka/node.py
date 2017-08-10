
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
        _cache_dir = _getenv("MANDALKA_CACHE", "./__saved__")

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self.node_id = _node_id(cls, *args, **kwargs)
            self.value = None

        def __compute(self):
            if self.value is not None:
                return
            savedir = Node._cache_dir + "/" + self.node_id

            # Tell the object to load itself from cache
            if os.path.exists(savedir + "/node-info.txt"):
                obj = cls.__new__(cls)
                obj.__load__(savedir)
                self.value = obj
                return

            # Create an actual new instance
            info = _describe_call(cls, *self.args, **self.kwargs)
            obj = cls(*self.args, **self.kwargs)
            self.args, self.kwargs = None, None

            # Tell it to save data to cache
            os.makedirs(savedir)
            try:
                obj.__save__(savedir)
                with open(savedir + "/node-info.txt", "w") as f:
                    f.write(info + "\n")
            finally:
                _rmdir_if_empty(savedir)
            self.value = obj

            # Save node descriptions
            with open(Node._cache_dir + "/graph.txt", "a") as f:
                f.write(self.node_id + "\t" + info + "\n")

        def __str__(self):
            return "<" + cls.__name__ + " " + self.node_id + ">"

        def __repr__(self):
            return "<" + cls.__name__ + " " + self.node_id + ">"

        def __getattr__(self, name):
            self.__compute()
            return getattr(self.value, name)

    return Node

def _node_id(cls, *args, **kwargs):
    name = _describe_call(cls, *args, **kwargs)
    try:
        name += "\n" + inspect.getsource(cls)
    except:
        pass

    h = hashlib.sha256(bytes(name, "UTF-8")).digest()
    return h[0:8].hex()

def _describe_call(obj, *args, **kwargs):
    args_str = list(map(repr, args))
    for k in sorted(kwargs):
        args_str.append(str(k) + "=" + repr(kwargs[k]))
    return obj.__name__ + "(" + ", ".join(args_str) + ")"

def _rmdir_if_empty(path):
    try:
        os.rmdir(path)
    except:
        pass

def _getenv(name, default = None):
    if name in os.environ and len(os.environ[name]) >= 1:
        return os.environ[name]
    return default
