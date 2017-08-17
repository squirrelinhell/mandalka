
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

class _mandalka_node:
    pass

def is_node(obj):
    return isinstance(obj, _mandalka_node)

def node(cls=None, save=True):
    if cls is None:
        return lambda c: _wrap_class(c, save)
    else:
        return _wrap_class(cls, save)

def _wrap_class(cls, save=True):
    class _class_wrapper(_mandalka_node, cls):
        def __init__(self, *args, **kwargs):
            params = {}
            params["cls"] = cls
            params["save"] = save
            params["args"] = args
            params["kwargs"] = kwargs
            params["call"] = _describe_call(cls, *args, **kwargs)
            params["nodeid"] = _hash(params["call"])
            object.__setattr__(self, "_mandalka_params", params)

        def __str__(self):
            params = object.__getattribute__(self, "_mandalka_params")
            return "<" + cls.__name__ + " " + params["nodeid"] + ">"

        def __repr__(self):
            params = object.__getattribute__(self, "_mandalka_params")
            return "<" + cls.__name__ + " " + params["nodeid"] + ">"

        def __enter__(self, *args, **kwargs):
            return evaluate(self).__enter__(*args, **kwargs)

        def __exit__(self, *args, **kwargs):
            return evaluate(self).__exit__(*args, **kwargs)

        def __setattr__(self, name, value):
            return setattr(evaluate(self), name, value)

        def __getattribute__(self, name):
            return getattr(evaluate(self), name)

    return _class_wrapper

def evaluate(node):
    if not is_node(node):
        raise ValueError("Not a mandalka node: " + node)

    params = object.__getattribute__(node, "_mandalka_params")
    if "obj" not in params:
        params["obj"] = _evaluate_node(**params)
        del params["args"], params["kwargs"]

    return params["obj"]

def describe(node):
    if not is_node(node):
        raise ValueError("Not a mandalka node: " + node)

    params = object.__getattribute__(node, "_mandalka_params")
    return params["call"]

def _evaluate_node(cls, save, args, kwargs, call, nodeid):
    nodeid = cls.__name__.lower() + "_" + nodeid
    cache_dir = _get_env("MANDALKA_CACHE", "./__saved__")
    save_path = cache_dir + "/" + nodeid

    # Tell the object to load itself from cache
    if os.path.exists(save_path):
        obj = cls.__new__(cls)
        obj.__load__(save_path)
        return obj

    # Or create an actual new instance
    obj = cls(*args, **kwargs)

    if save:
        # And then save it to cache
        os.makedirs(save_path + ".save", exist_ok=True)
        obj.__save__(save_path + ".save")
        os.rename(save_path + ".save", save_path)

        # Also save the description of this node
        with open(cache_dir + "/graph.txt", "a") as f:
            f.write(nodeid + "\t" + call + "\n")

    return obj

def _hash(s):
    h = hashlib.sha256(bytes("mandalka:" + s, "UTF-8"))
    return h.digest()[0:8].hex()

def _describe_arg(obj):
    if obj is None:
        return "None"
    if isinstance(obj, (int, str, bytes, bool, _mandalka_node)):
        return repr(obj)
    if isinstance(obj, list):
        return "[" + ", ".join(map(_describe_arg, obj)) + "]"
    if isinstance(obj, tuple):
        if len(obj) == 1:
            return "(" + _describe_arg(obj[0]) + ",)"
        else:
            return "(" + ", ".join(map(_describe_arg, obj)) + ")"
    if isinstance(obj, dict):
        return "{" + ", ".join([
            _describe_arg(k) + ": " + _describe_arg(v)
            for k, v in obj.items()
        ]) + "}"
    raise ValueError("Invalid argument type: " + str(type(obj)))

def _describe_call(obj, *args, **kwargs):
    args_str = list(map(_describe_arg, args))
    for k in sorted(kwargs):
        args_str.append(str(k) + "=" + _describe_arg(kwargs[k]))
    return obj.__name__ + "(" + ", ".join(args_str) + ")"

def _get_env(name, default = None):
    if name in os.environ and len(os.environ[name]) >= 1:
        return os.environ[name]
    return default
