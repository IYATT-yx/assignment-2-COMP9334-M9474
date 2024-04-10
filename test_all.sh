#!/usr/bin/env sh

sh ./run_test.sh 0
sh ./run_test.sh 1
sh ./run_test.sh 2
sh ./run_test.sh 3
sh ./run_test.sh 4
sh ./run_test.sh 5
sh ./run_test.sh 6

python3 cf_output_with_ref.py 0
python3 cf_output_with_ref.py 1
python3 cf_output_with_ref.py 2
python3 cf_output_with_ref.py 3
python3 cf_output_with_ref.py 4
python3 cf_output_with_ref.py 5
python3 cf_output_with_ref.py 6