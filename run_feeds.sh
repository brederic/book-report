#! /bin/bash    
cd ~/Projects/test_env
source bin/activate

cd ../book_report

# virtualenv is now active, which means your PATH has been modified.
# Don't try to run python from /usr/bin/python, just run "python" and
# let the PATH figure out which version to run (based on what your
# virtualenv has configured).

python -u feeds.py  >> feed.log 2>&1 &

python -u track_books.py -a chase-lowest-price  >> price.log 2>&1 &

python -u track_orders.py  >> orders.log 2>&1 &

python -u reconcile.py  >> reconcile.log 2>&1 &

