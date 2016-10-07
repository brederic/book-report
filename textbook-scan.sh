#! /bin/bash    
cd ~/Projects/test_env
source bin/activate

cd ../book_report

# virtualenv is now active, which means your PATH has been modified.
# Don't try to run python from /usr/bin/python, just run "python" and
# let the PATH figure out which version to run (based on what your
# virtualenv has configured).

python -u book-report.py -a scan-textbooks >> textbook.log 2>&1 &
python -u weekly.py
