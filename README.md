
# Install

~~~~
pip install --upgrade git+https://github.com/squirrelinhell/mandalka.git
~~~~

# What is it?

Mandalka makes your Python objects unique, based on arguments
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

print(Fib(100).n) # prints '354224848179261915075'
```

It also provides lazy evaluation, which makes it possible to
transparently cache and re-use data:

```python
import os
import numpy as np

@mandalka.node
class Data:
    def __init__(self, data):
        print("Computing...")
        self.squares = np.square(data)

@mandalka.node
class Model:
    def __init__(self, data):
        path = mandalka.unique_id(self) + ".npy"
        if os.path.exists(path):
            self.weights = np.load(path)
        else:
            self.weights = data.squares * 10
            np.save(path, self.weights)

model = Model(Data([1, 2, 3]))

# This will print 'Computing...' only for the first time:
print(model.weights)
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
