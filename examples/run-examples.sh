#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PYTHONPATH="$(realpath "$DIR/../src"):$PYTHONPATH"
pushd $DIR

failed=0
for example_py in *.py; do
    example="$(basename -s .py $example_py)"
    echo "Running '$example'"
    if python "$example_py" datafile.txt 2>&1 1>"$example.out"; then
        if [[ -f "$example.txt" ]] && diff "$example.out" "$example.txt" 2>&1 1>/dev/null; then
            echo "'$example' done"
            rm -f "$example.out"
        elif [[ -f "$example.txt" ]]; then
            failed=1
            echo "ERROR: '$example' generated wrong output"
        else
            echo "WARNING: '$example' does not have expected output file"
        fi
    else
        failed=1
        echo "ERROR: '$example' failed to run"
    fi
done

popd

exit $failed
