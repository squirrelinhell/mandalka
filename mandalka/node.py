
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

def node(cls=None, save=True):
    if cls is None:
        return lambda c: node(c, save)

    def get_env(name, default = None):
        if name in os.environ and len(os.environ[name]) >= 1:
            return os.environ[name]
        return default

    def str_hash(s):
        h = hashlib.sha256(bytes("mandalka:" + s, "UTF-8"))
        return h.digest()[0:8].hex()

    def describe_obj(obj):
        if obj is None:
            return "None"
        if isinstance(obj, (int, str, bytes, bool)):
            return repr(obj)
        if isinstance(obj, list):
            return "[" + ", ".join(map(describe_obj, obj)) + "]"
        if isinstance(obj, tuple):
            if len(obj) == 1:
                return "(" + describe_obj(obj[0]) + ",)"
            else:
                return "(" + ", ".join(map(describe_obj, obj)) + ")"
        if isinstance(obj, dict):
            return "{" + ", ".join([
                describe_obj(k) + ": " + describe_obj(v)
                for k, v in obj.items()
            ]) + "}"
        try:
            params = object.__getattribute__(obj, "_mandalka_node")
            return "<" + cls.__name__ + " " + params["nodeid"] + ">"
        except AttributeError:
            pass
        raise ValueError("Invalid argument type: " + str(type(obj)))

    def describe_call(obj, *args, **kwargs):
        args_str = list(map(describe_obj, args))
        for k in sorted(kwargs):
            args_str.append(str(k) + "=" + describe_obj(kwargs[k]))
        return obj.__name__ + "(" + ", ".join(args_str) + ")"

    def unwrap(node):
        params = object.__getattribute__(node, "_mandalka_node")
        if "obj" in params:
            return params["obj"]

        nodeid = cls.__name__.lower() + "_" + params["nodeid"]
        cache_dir = get_env("MANDALKA_CACHE", "./__saved__")
        save_path = cache_dir + "/" + nodeid

        params["obj"] = cls.__new__(cls)

        if os.path.exists(save_path):
            # Tell the object to load itself from cache
            del params["args"], params["kwargs"]
            cls.__load__(node, save_path)
            return params["obj"]

        # Or to build a new instance
        try:
            cls.__init__(node, *params["args"], **params["kwargs"])
        finally:
            del params["args"], params["kwargs"]

        if save:
            # And then save it to cache
            os.makedirs(save_path + ".save", exist_ok=True)
            cls.__save__(node, save_path + ".save")
            os.rename(save_path + ".save", save_path)

            # Also save the description of this node
            with open(cache_dir + "/graph.txt", "a") as f:
                f.write(nodeid + "\t" + params["call"] + "\n")

        return params["obj"]

    builtins = [
        "_mandalka_node",
        "__init__",
        "__str__",
        "__repr__",
        "__enter__",
        "__exit__",
        "__setattr__",
        "__getattribute__",
        "__dict__",
        "__class__",
    ]

    class wrapper(cls):
        def __init__(self, *args, **kwargs):
            if type(self) != wrapper:
                raise ValueError("Do not inherit from mandalka nodes")
            params = {}
            params["cls"] = cls
            params["evaluate"] = lambda: unwrap(self)
            params["save"] = save
            params["args"] = args
            params["kwargs"] = kwargs
            params["call"] = describe_call(cls, *args, **kwargs)
            params["nodeid"] = str_hash(params["call"])
            object.__setattr__(self, "_mandalka_node", params)

        def __str__(self):
            params = object.__getattribute__(self, "_mandalka_node")
            return "<" + cls.__name__ + " " + params["nodeid"] + ">"

        def __repr__(self):
            params = object.__getattribute__(self, "_mandalka_node")
            return "<" + cls.__name__ + " " + params["nodeid"] + ">"

        def __enter__(self, *args, **kwargs):
            unwrap(self)
            return cls.__enter__(self, *args, **kwargs)

        def __exit__(self, *args, **kwargs):
            unwrap(self)
            return cls.__exit__(self, *args, **kwargs)

        def __setattr__(self, name, value):
            if name not in builtins:
                object.__setattr__(self, name, None)
            return setattr(unwrap(self), name, value)

        def __getattribute__(self, name):
            if name not in builtins:
                try:
                    v = object.__getattribute__(self, name)
                    if v is not None:
                        return v
                except AttributeError:
                    pass
            return getattr(unwrap(self), name)

    return wrapper

def is_node(node):
    try:
        object.__getattribute__(node, "_mandalka_node")
        return True
    except AttributeError:
        return False

def evaluate(node):
    try:
        params = object.__getattribute__(node, "_mandalka_node")
    except AttributeError:
        raise ValueError("Not a mandalka node: " + str(node))

    params["evaluate"]()
    return node

def describe(node):
    try:
        params = object.__getattribute__(node, "_mandalka_node")
    except AttributeError:
        raise ValueError("Not a mandalka node: " + str(node))

    return params["call"]
