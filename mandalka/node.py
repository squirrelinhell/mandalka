
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
import hashlib

def node(cls):
    class Node(object):
        _cache_dir = _get_env("MANDALKA_CACHE", "./__saved__")

        def __init__(self, *args, **kwargs):
            call = _describe(cls, *args, **kwargs)
            self._mandalka_params = {
                "args": args,
                "kwargs": kwargs,
                "call": call,
                "nodeid": _hash(call),
            }

        def __str__(self):
            params = object.__getattribute__(self, "_mandalka_params")
            return "<" + cls.__name__ + " " + params["nodeid"] + ">"

        def __repr__(self):
            params = object.__getattribute__(self, "_mandalka_params")
            return "<" + cls.__name__ + " " + params["nodeid"] + ">"

        def __getattribute__(self, name):
            params = object.__getattribute__(self, "_mandalka_params")

            if "obj" not in params:
                params["obj"] = _compute_node(
                    cls = cls,
                    cache_dir = Node._cache_dir,
                    **params
                )
                del params["args"], params["kwargs"]

            if len(name) >= 1:
                return getattr(params["obj"], name)

    return Node

def _compute_node(cls, cache_dir, args, kwargs, call, nodeid):
    nodeid = cls.__name__.lower() + "_" + nodeid
    save_path = cache_dir + "/" + nodeid

    # Tell the object to load itself from cache
    if os.path.exists(save_path + "/node-info.txt"):
        obj = cls.__new__(cls)
        obj.__load__(save_path)
        return obj

    # Or create an actual new instance
    obj = cls(*args, **kwargs)

    # And then save it to cache
    try:
        os.makedirs(save_path)
        obj.__save__(save_path)
        with open(save_path + "/node-info.txt", "w") as f:
            f.write(call + "\n")
    finally:
        _rmdir_if_empty(save_path)

    # Save node descriptions
    with open(cache_dir + "/graph.txt", "a") as f:
        f.write(nodeid + "\t" + call + "\n")

    return obj

def _hash(s):
    h = hashlib.sha256(bytes(s, "UTF-8"))
    return h.digest()[0:8].hex()

def _describe(obj, *args, **kwargs):
    args_str = list(map(repr, args))
    for k in sorted(kwargs):
        args_str.append(str(k) + "=" + repr(kwargs[k]))
    return obj.__name__ + "(" + ", ".join(args_str) + ")"

def _rmdir_if_empty(path):
    try:
        os.rmdir(path)
    except:
        pass

def _get_env(name, default = None):
    if name in os.environ and len(os.environ[name]) >= 1:
        return os.environ[name]
    return default
