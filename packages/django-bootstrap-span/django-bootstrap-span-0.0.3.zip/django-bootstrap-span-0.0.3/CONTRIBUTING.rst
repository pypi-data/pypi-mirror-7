
How to get set up for development.
==================================

    Start with python 2.7.6
    Get pip:        see web for instructions here: http://www.pip-installer.org/en/latest/installing.html
    Get tox :       pip install tox
    Get pytest:     pip install pytest
    Get coverage :  pip install coverage
    Get pylint :    pip install pylint
    Get sphinx :    pip install sphinx
    
    The github project (from your new dev directory): 
       git clone https://github.com/stumc/django-bootstrap-span.git

How to run the tests.
=====================

Multi Python platform running before pushing:
    tox
    (I couldn't get pypy to work in my local win32 dev env, but it does in Travis CI environment)

Code coverage report:
    coverage run -m pytest
    coverage html
    # read htmlcov/index.html in your browser
    
Build the docs (also a test of the docs)
    ( cd docs ; make html ) - on Unix
    ( cd docs && make html ) - on Windows

What to include in a bug report.
================================

    1. Version of django-bootstrap-span
    2) Version of django-bootstrap
    3) Version of django
    4) Version of python
    5) Symptoms of problem (stack trace, output of html)
    6) Sample code re-creating the problem (1 file)

Coding standards, test coverage standards, documentation...
===========================================================

    tox tests passing on python 2.7, 3.4 and pypy
    pylint - shows no failures or warnings - required
    code coverage 100% - required
    Travis CI - fully passing - required
    
    
Places to update version number increments:
===========================================
    setup.py (version)
    CHANGES.rst (add change log)
    docs/conf.py (release and version)
    
Git commands reminder sheet
===========================
    # Get a new repo
    git status
    git clone https://github.com/stumc/django-bootstrap-span.git
    
    # make your changes
    git log --oneline
    git add myNewFile.py
    git commit -m "Changed something"
    # set up remote repos (if created locally)
    git remote -v
    git remote add origin https://github.com/stumc/django-bootstrap-span
    
    # tag a new version
    git tag -a 0.0.2 -m "the next release"
    
    # merge tag to master on remote
    git checkout master
    git pull origin master
    git merge 0.0.2       #to bring changes to local master from your develop branch
    git push origin master #push current HEAD to remote master branch
    git status
    
    # delete an unwanted tag
    git tag
    git tag -d unwanted_tag
    git push origin :refs/tags/unwanted_tag
    
PyPI Release
============
    # Push to git hub tag and master first (only authorised PyPI users can do this)...
    python setup.py register -r pypitest
    python setup.py sdist upload -r pypitest
    python setup.py register -r pypi
    python setup.py sdist upload -r pypi
    
    
Git, Documentation And Continuous Integration Links
===================================================
    https://github.com/stumc/django-bootstrap-span
    https://readthedocs.org/projects/django-bootstrap-span/
    https://travis-ci.org/stumc/django-bootstrap-span
    https://coveralls.io/r/stumc/django-bootstrap-span

