#! /bin/bash    
cd ~/Projects/prod
source bin/activate

cd /etc/prod/book-report

# virtualenv is now active, which means your PATH has been modified.
# Don't try to run python from /usr/bin/python, just run "python" and
# let the PATH figure out which version to run (based on what your
# virtualenv has configured).

# check to see if review has completed, and if so, start it again
python -u review.py  >> ~/Projects/book_report/prod_track.log 2>&1 &

