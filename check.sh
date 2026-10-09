#!/bin/sh

# Prefer the shell script to check instead of multiple steps in a Github
# action, so that they can also be run locally and on pre-commit.
# This was said during the lecture on CI/CD pipelines.

set -eux

ruff check *.py

pylint *.py

pytest

for t in test-cases/*.in; do
  id=$(basename "$t" .in)
  echo "$id"
  python3 metro.py < "test-cases/$id.in" > "test-cases/$id.out"
  python3 lint.py "test-cases/$id.out"
  python3 check.py "test-cases/$id.in" "test-cases/$id.out" "solutions/$id.out"
done
