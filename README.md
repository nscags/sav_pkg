# sav_pkg

## Tutorial
```
# create virtual env
python3 -m venv venv

# activate virtual env
source venv/bin/activate

# clone the repo
git clone git@github.com:nscags/sav_pkg.git

# install BGPy
cd sav_pkg
pip install -e .[test]
# alternatively you can install BGPy directly
pip install bgpy_pkg==8.1.1

# NOTE: if this doesn't work please let me know
#       also can use pypy3
```
