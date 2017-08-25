
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

all_wrappers = {}
wrapper_by_id = {}

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
    if obj in all_wrappers:
        described_nodes.append(obj)
        return ("<" + all_wrappers[obj]["cls"].__name__
            + " " + all_wrappers[obj]["nodeid"] + ">")
    raise ValueError("Invalid argument type: " + str(type(obj)))

def describe_call(obj, *args, **kwargs):
    args_str = list(map(describe_obj, args))
    for k in sorted(kwargs):
        args_str.append(str(k) + "=" + describe_obj(kwargs[k]))
    return obj.__name__ + "(" + ", ".join(args_str) + ")"

def evaluate(node):
    if not node in all_wrappers:
        raise ValueError("Not a mandalka node: " + str(node))

    p = all_wrappers[node]
    if "initialized" not in p:
        p["initialized"] = True
        args, kwargs = p["args"], p["kwargs"]
        del p["args"], p["kwargs"]

        p["cls"].__init__(node, *args, **kwargs)

    return node

def evaluate_with_children(node):
    evaluate(node)
    for child in all_wrappers[node]["children"]:
        evaluate_with_children(child)
    return node

def node(cls):
    class Node(cls):
        def __init__(self, *args, **kwargs):
            if type(self) != Node:
                raise ValueError("Do not inherit from mandalka nodes")

            call = describe_call(cls, *args, **kwargs)
            nodeid = str_hash(call)

            if nodeid in wrapper_by_id:
                all_wrappers[self] = wrapper_by_id[nodeid]
                return

            params = {}
            params["obj"] = self
            params["cls"] = cls
            params["args"] = args
            params["kwargs"] = kwargs
            params["call"] = call
            params["nodeid"] = nodeid
            params["children"] = []

            global described_nodes
            for parent in described_nodes:
                all_wrappers[parent]["children"].append(self)
            described_nodes = []

            all_wrappers[self] = params
            wrapper_by_id[nodeid] = params

        def __str__(self):
            return ("<" + cls.__name__
                + " " + all_wrappers[self]["nodeid"] + ">")

        def __repr__(self):
            return ("<" + cls.__name__
                + " " + all_wrappers[self]["nodeid"] + ">")

        def __enter__(self, *args, **kwargs):
            self = evaluate(all_wrappers[self]["obj"])
            return cls.__enter__(self, *args, **kwargs)

        def __exit__(self, *args, **kwargs):
            self = evaluate_with_children(all_wrappers[self]["obj"])
            return cls.__exit__(self, *args, **kwargs)

        def __setattr__(self, name, value):
            self = evaluate(all_wrappers[self]["obj"])
            return object.__setattr__(self, name, value)

        def __getattribute__(self, name):
            if name == "__class__":
                return cls
            self = evaluate(all_wrappers[self]["obj"])
            return object.__getattribute__(self, name)

    return Node

def is_node(node):
    return node in all_wrappers

def describe(node):
    if not node in all_wrappers:
        raise ValueError("Not a mandalka node: " + str(node))

    return all_wrappers[node]["call"]

def unique_id(node):
    if not node in all_wrappers:
        raise ValueError("Not a mandalka node: " + str(node))

    return all_wrappers[node]["nodeid"]
