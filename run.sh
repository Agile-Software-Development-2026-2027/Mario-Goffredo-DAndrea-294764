for t in test-cases/*.in; do
  id=$(basename "$t" .in)
  echo "$id"
  python3 metro.py < test-cases/$id.in > test-cases/$id.out
  python3 lint.py test-cases/$id.out
  python3 check.py test-cases/$id.in test-cases/$id.out solutions/$id.out
done
