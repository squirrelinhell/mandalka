
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
node_by_nodeid = {}

def str_hash(s):
    h = hashlib.sha256(bytes("mandalka:" + s, "UTF-8"))
    return h.digest()[0:8].hex()

described_nodes = []

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
    p = params.get(obj)
    if p is not None:
        described_nodes.append(obj)
        return "<" + p["cls"].__name__ + " " + p["nodeid"] + ">"
    raise ValueError("Invalid argument type: " + str(type(obj)))

def describe_call(obj, *args, **kwargs):
    args_str = list(map(describe_obj, args))
    for k in sorted(kwargs):
        args_str.append(str(k) + "=" + describe_obj(kwargs[k]))
    return obj.__name__ + "(" + ", ".join(args_str) + ")"

def evaluate(node):
    p = params.get(node)
    if "initialized" not in p:
        p["initialized"] = True
        args, kwargs = p["args"], p["kwargs"]
        del p["args"], p["kwargs"]

        p["cls"].__init__(node, *args, **kwargs)

    return node

def evaluate_all_children(node, visited=None):
    if visited is None:
        visited = ByInstanceStorage()
    for child in params.get(node)["children"]:
        if not visited.get(child):
            visited.add(child, True)
            evaluate(child)
            evaluate_all_children(child, visited)
    return node

def node(cls):
    class Node(cls):
        def __new__(node_cls, *args, **kwargs):
            if node_cls != Node:
                raise ValueError("Do not inherit from mandalka nodes")

            call = describe_call(cls, *args, **kwargs)
            nodeid = str_hash(call)

            try:
                return node_by_nodeid[nodeid]
            except KeyError:
                pass

            node = cls.__new__(node_cls)

            p = {}
            p["cls"] = cls
            p["args"] = args
            p["kwargs"] = kwargs
            p["call"] = call
            p["nodeid"] = nodeid
            p["children"] = []

            params.add(node, p)
            node_by_nodeid[nodeid] = node

            global described_nodes
            for parent in described_nodes:
                params.get(parent)["children"].append(node)
            described_nodes = []

            return node

        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self, *args, **kwargs):
            evaluate(self)
            return cls.__enter__(self, *args, **kwargs)

        def __exit__(self, *args, **kwargs):
            evaluate_all_children(self)
            return cls.__exit__(self, *args, **kwargs)

        def __setattr__(self, name, value):
            evaluate(self)
            return object.__setattr__(self, name, value)

        def __getattribute__(self, name):
            if name == "__class__":
                return cls
            evaluate(self)
            return object.__getattribute__(self, name)

    def to_str(o):
        return "<" + cls.__name__ + " " + params.get(o)["nodeid"] + ">"

    cls.__str__ = to_str
    cls.__repr__ = to_str

    return Node

def is_node(node):
    return params.get(node) is not None

def describe(node):
    return params.get(node)["call"]

def unique_id(node):
    return params.get(node)["nodeid"]
