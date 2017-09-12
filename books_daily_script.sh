#! /bin/bash    
cd ~/Projects/prod
source bin/activate

cd ../book_report

# virtualenv is now active, which means your PATH has been modified.
# Don't try to run python from /usr/bin/python, just run "python" and
# let the PATH figure out which version to run (based on what your
# virtualenv has configured).

python -u price-drop.py  >> price-drop.log 2>&1 &

python -u daily_charts.py  >> charts.log 2>&1 &


