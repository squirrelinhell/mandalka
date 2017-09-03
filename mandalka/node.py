
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
import threading

def str_hash(s):
    h = hashlib.sha256(bytes("mandalka:" + s, "UTF-8"))
    return h.digest()[0:8].hex()

class ByInstanceStorage:
    def __init__(self):
        by_id = {}

        def get(obj):
            obj_id = id(obj)
            try:
                return by_id[obj_id]
            except KeyError:
                return None

        def add(obj, value):
            if value is not None:
                obj_id = id(obj)
                assert not obj_id in by_id
                by_id[obj_id] = value

        self.get = get
        self.add = add

params = ByInstanceStorage()
node_class_by_obj = ByInstanceStorage()
class_obj_by_name = {}
node_obj_by_nodeid = {}
global_lock = threading.Lock()

global_config = {
    "debug": False
}

def config(*args, debug=None):
    assert len(args) == 0

    if debug is not None:
        global_config["debug"] = bool(debug)

def safe_copy(obj):
    if obj is None:
        return None

    if isinstance(obj, (int, bool, float, complex, str, bytes)):
        return obj

    if isinstance(obj, tuple):
        return tuple(safe_copy(v) for v in obj)

    if isinstance(obj, list):
        return [safe_copy(v) for v in obj]

    if isinstance(obj, (set, frozenset)):
        return set(safe_copy(v) for v in obj)

    if isinstance(obj, dict):
        return {safe_copy(k): safe_copy(v) for k, v in obj.items()}

    if isinstance(obj, type):
        cls_name = node_class_by_obj.get(obj)
        if cls_name is None:
            raise ValueError("Type is not a node: " + str(obj))
        return obj

    if params.get(obj) is not None:
        return obj

    raise ValueError("Invalid type: " + str(type(obj)))

def describe(obj, depth=1):
    depth = int(depth)

    if obj is None:
        return "None"

    if isinstance(obj, (int, bool, float, complex, str, bytes)):
        return repr(obj)

    if isinstance(obj, tuple):
        if len(obj) == 1:
            return "(" + describe(obj[0], depth) + ",)"
        else:
            return "(" + ", ".join([describe(o, depth) for o in obj]) + ")"

    if isinstance(obj, list):
        return "[" + ", ".join([describe(o, depth) for o in obj]) + "]"

    if isinstance(obj, (set, frozenset)):
        return "set(" + ", ".join(sorted(
            describe(o, depth) for o in obj
        )) + ")"

    if isinstance(obj, dict):
        return "{" + ", ".join(sorted(
            describe(k, depth) + ": " + describe(v, depth)
            for k, v in obj.items()
        )) + "}"

    if isinstance(obj, type):
        cls_name = node_class_by_obj.get(obj)
        if cls_name is None:
            raise ValueError("Type is not a node: " + str(obj))
        return "<class " + repr(cls_name) + ">"

    p = params.get(obj)
    if p is not None:
        if depth == 0:
            return "<" + p["clsname"] + " " + p["nodeid"] + ">"
        else:
            args = [describe(o, depth-1) for o in p["args"]]
            for k in sorted(p["kwargs"]):
                args.append(k + "=" + describe(p["kwargs"][k], depth-1))
            return p["clsname"] + "(" + ", ".join(args) + ")"

    raise ValueError("Invalid type: " + str(type(obj)))

def evaluate(node):
    p = params.get(node)
    with p["lock"]:
        if "error" in p:
            raise RuntimeError("%s.__init__() failed" % node)
        if "initialized" not in p:
            p["initialized"] = True
            args = safe_copy(p["args"])
            kwargs = safe_copy(p["kwargs"])
            cls = class_obj_by_name[p["clsname"]]
            try:
                cls.__init__(node, *args, **kwargs)
            except:
                p["error"] = True
                raise
    return node

def node(cls):
    with global_lock:
        # Make sure class names are unique
        cls_name = str(cls.__name__)
        assert not cls_name in class_obj_by_name
        class_obj_by_name[cls_name] = cls

    class Node(cls):
        def __new__(node_cls, *args, **kwargs):
            if node_cls != Node:
                raise ValueError("Do not inherit from mandalka nodes")

            # Build a full description of this constructor call
            nodeid = repr(cls_name)
            for a in args:
                nodeid += "|" + describe(a, 0)
            for k, v in kwargs.items():
                nodeid += "|" + k + "=" + describe(v, 0)
            nodeid = str_hash(nodeid)

            with global_lock:
                # Make sure the object is unique
                try:
                    return node_obj_by_nodeid[nodeid]
                except KeyError:
                    pass

                # It's really the first time
                node = cls.__new__(node_cls)
                node_obj_by_nodeid[nodeid] = node

                # Store arguments to run cls.__init__() later
                p = {}
                p["clsname"] = cls_name
                p["args"] = safe_copy(args)
                p["kwargs"] = safe_copy(kwargs)
                p["nodeid"] = nodeid
                p["lock"] = threading.RLock()

                params.add(node, p)
                return node

        def __init__(self, *args, **kwargs):
            if global_config["debug"]:
                evaluate(self)

        def __setattr__(self, name, value):
            evaluate(self)
            return object.__setattr__(self, name, value)

        def __getattribute__(self, name):
            if name == "__class__":
                return Node
            evaluate(self)
            return object.__getattribute__(self, name)

    def to_str(o):
        return "<" + cls_name + " " + params.get(o)["nodeid"] + ">"

    Node.__name__ = cls_name
    Node.__qualname__ = cls_name
    Node.__str__ = to_str
    Node.__repr__ = to_str

    def wrap(f):
        def wrapped_f(self, *args, **kwargs):
            evaluate(self)
            return f(self, *args, **kwargs)
        return wrapped_f

    for tpe in cls.__mro__:
        if tpe == object:
            continue
        for name, value in tpe.__dict__.items():
            if not name.startswith("__"):
                continue
            if name in ("__dict__", "__weakref__"):
                continue
            if name in Node.__dict__:
                continue
            setattr(Node, name, wrap(value))

    with global_lock:
        node_class_by_obj.add(Node, cls_name)

    return Node

def is_node(node):
    return params.get(node) is not None

def unique_id(node):
    return params.get(node)["nodeid"]

def inputs(node):
    result = set()
    def visit(obj):
        if isinstance(obj, (tuple, list, set, frozenset)):
            [visit(o) for o in obj]
        if isinstance(obj, dict):
            [visit(o) for o in obj.keys()]
            [visit(o) for o in obj.values()]
        if params.get(obj) is not None:
            result.add(obj)
    p = params.get(node)
    [visit(o) for o in p["args"]]
    [visit(o) for o in p["kwargs"].values()]
    return result
