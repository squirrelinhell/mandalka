
# Install

~~~~
pip install --upgrade git+https://github.com/squirrelinhell/mandalka.git
~~~~

# What is it?

Mandalka makes Python objects unique, based on arguments
passed to `__init__`. So this kind of code will run fast:

```python
import mandalka

@mandalka.node
class Fib:
    def __init__(self, n):
        if n <= 1:
            self.n = n
        else:
            self.n = Fib(n-1).n + Fib(n-2).n

print(Fib(100).n) # prints "354224848179261915075"
```

It also provides lazy evaluation, which makes it possible to
transparently cache and re-use data:

```python
import os
import numpy as np

@mandalka.node
class Data:
    def __init__(self, size):
        # This code will not run if Model doesn't need it
        print("Computing...")
        self.squares = np.square(np.arange(size))

@mandalka.node
class Model:
    def __init__(self, data):
        path = mandalka.unique_id(self) + ".npy"
        if os.path.exists(path):
            self.weights = np.load(path)
        else:
            self.weights = data.squares * 10
            np.save(path, self.weights)

model = Model(Data(5))

# Prints "Computing..." only for the first time this script is run:
print(model.weights)
```

Arguments passed to constructors of nodes can only
be made out of other nodes and basic Python types
(`int`, `bool`, `str`, `bytes`, `list`, `tuple`, `dict`).

The uniqueness of mandalka nodes makes it possible
to write code more similar to what one would expect from
functional programming, or mathematical notation:

```python
@mandalka.node
class S:
    def __init__(*_):
        pass

two = S(S(0))
three = S(S(S(0)))
assert three == S(two)

def add(a, b):
    counter = 0
    while counter != b:
        a = S(a)
        counter = S(counter)
    return a

five = add(two, three)
print(mandalka.describe(five, -1)) # prints "S(S(S(S(S(0)))))"
```

# License

This code is distributed under the MIT license, as quoted below:

> Copyright (c) 2017 SquirrelInHell
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this software and associated documentation files (the "Software"), to deal
> in the Software without restriction, including without limitation the rights
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all
> copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
> SOFTWARE.
