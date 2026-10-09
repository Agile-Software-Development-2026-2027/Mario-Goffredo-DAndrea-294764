#!/bin/sh

# Prefer the shell script to check instead of multiple steps in a Github
# action, so that they can also be run locally and on pre-commit.
# This was said during the lecture on CI/CD pipelines.

set -eux

uv run ruff check *.py
uv run pylint *.py
uv run pytest

for t in test-cases/*.in; do
  id=$(basename "$t" .in)
  echo "$id"
  uv run metro.py < "test-cases/$id.in" > "test-cases/$id.out"
  uv run lint.py "test-cases/$id.out"
  uv run check.py "test-cases/$id.in" "test-cases/$id.out" "solutions/$id.out"
done
