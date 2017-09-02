#!/bin/bash

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

TMPDIR=$(mktemp -d) || exit 1
trap "rm -rf $TMPDIR" EXIT

export PYTHONPATH="$(pwd):$PYTHONPATH"

if [ "x$1" != x ]; then
    TEST_FILE="$1"
    [ -f "$TEST_FILE" ] || TEST_FILE="tests/$TEST_FILE"
    [ -f "$TEST_FILE" ] || TEST_FILE="$TEST_FILE.py"
    export DEBUG=1
    echo "import debug" > "$TMPDIR/run.py"
    cat "$TEST_FILE" >> "$TMPDIR/run.py"
    (cd "$TMPDIR" && python3 "./run.py")
    exit $?
fi

ID=1
for test in demo.py $(find tests -name '*.py' | sort); do
    echo -n "Test: $test... "
    mkdir "$TMPDIR/$ID" || exit 1

    cat "$test" > "$TMPDIR/$ID/run.py"

    OUT_FILE="${test%.*}.out"
    if [ -f "$OUT_FILE" ]; then
        cat "$OUT_FILE"
    fi > "$TMPDIR/ans"

    ( \
        cd "$TMPDIR/$ID" \
        && python3 "./run.py" \
        && ( \
            ! grep -q '^---$' "$TMPDIR/ans" \
            || (echo "---" && python3 "./run.py") \
        ) \
    ) </dev/null >"$TMPDIR/out" 2>/dev/null
    RESULT=$?

    if ! [ "x$RESULT" = x0 ]; then
        echo FAIL
        echo
        echo "EXIT CODE $RESULT: $test"
        echo
    elif ! diff -b -q "$TMPDIR/ans" "$TMPDIR/out" >/dev/null; then
        echo FAIL
        echo
        echo "INCORRECT OUTPUT: $test"
        echo
        diff -b --color=auto "$TMPDIR/ans" "$TMPDIR/out"
    else
        echo OK
    fi

    rm -rf "$TMPDIR/$ID" || true
    let ID=ID+1
done
