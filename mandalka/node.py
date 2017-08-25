
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

def str_hash(s):
    h = hashlib.sha256(bytes("mandalka:" + s, "UTF-8"))
    return h.digest()[0:8].hex()

def describe_call(function, *args, **kwargs):
    described_nodes = []

    def d(obj):
        if obj is None:
            return "None"
        if isinstance(obj, (int, str, bytes, bool)):
            return repr(obj)
        if isinstance(obj, list):
            return "[" + ", ".join(map(d, obj)) + "]"
        if isinstance(obj, tuple):
            if len(obj) == 1:
                return "(" + d(obj[0]) + ",)"
            else:
                return "(" + ", ".join(map(d, obj)) + ")"
        if isinstance(obj, dict):
            return "{" + ", ".join([
                d(k) + ": " + d(v)
                for k, v in obj.items()
            ]) + "}"
        p = params.get(obj)
        if p is not None:
            described_nodes.append(obj)
            return "<" + p["cls"].__name__ + " " + p["nodeid"] + ">"
        raise ValueError("Invalid argument type: " + str(type(obj)))

    args_str = list(map(d, args))
    for k in sorted(kwargs):
        args_str.append(str(k) + "=" + d(kwargs[k]))
    description = function.__name__ + "(" + ", ".join(args_str) + ")"
    return description, described_nodes

def evaluate(node):
    p = params.get(node)
    with p["lock"]:
        if "error" in p:
            raise RuntimeError("%s.__init__() failed" % node)
        if "initialized" not in p:
            p["initialized"] = True
            args, kwargs = p["args"], p["kwargs"]
            del p["args"], p["kwargs"]

            try:
                p["cls"].__init__(node, *args, **kwargs)
            except:
                p["error"] = True
                raise
    return node

def evaluate_subgraph(node):
    visited = ByInstanceStorage()
    def visit(n):
        if not visited.get(n):
            visited.add(n, True)
            evaluate(n)
            for child in params.get(n)["outputs"]:
                visit(child)
    visit(node)
    return node

def node(cls):
    node_by_nodeid = {}
    lock = threading.Lock()

    class Node(cls):
        def __new__(node_cls, *args, **kwargs):
            if node_cls != Node:
                raise ValueError("Do not inherit from mandalka nodes")

            call, inputs = describe_call(cls, *args, **kwargs)
            nodeid = str_hash(call)

            with lock:
                try:
                    return node_by_nodeid[nodeid]
                except KeyError:
                    node = cls.__new__(node_cls)
                    node_by_nodeid[nodeid] = node

            p = {}
            p["cls"] = cls
            p["args"] = args
            p["kwargs"] = kwargs
            p["call"] = call
            p["nodeid"] = nodeid
            p["lock"] = threading.RLock()
            p["inputs"] = inputs
            p["outputs"] = []

            for i in inputs:
                params.get(i)["outputs"].append(node)

            params.add(node, p)
            return node

        def __init__(self, *args, **kwargs):
            pass

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

    Node.__str__ = to_str
    Node.__repr__ = to_str

    def wrap(f, prepare=evaluate):
        def wrapped_f(self, *args, **kwargs):
            prepare(self)
            return f(self, *args, **kwargs)
        return wrapped_f

    if "__enter__" in cls.__dict__:
        Node.__enter__ = wrap(cls.__enter__)

    if "__exit__" in cls.__dict__:
        Node.__exit__ = wrap(cls.__exit__, evaluate_subgraph)

    return Node

def is_node(node):
    return params.get(node) is not None

def describe(node):
    return params.get(node)["call"]

def unique_id(node):
    return params.get(node)["nodeid"]

def inputs(node):
    return params.get(node)["inputs"].copy()

def outputs(node):
    return params.get(node)["outputs"].copy()
