from __future__ import print_function

# the name of the project
name = "metasetup"

#-----------------------------------------------------------------------------
# Minimal Python version sanity check
#-----------------------------------------------------------------------------

import sys

minimum_version = (2, 7)

if sys.version_info < minimum_version:
    prefix = "ERROR: %s " % name
    error =  "requires Python version %s.%s or above." % minimum_version
    print(prefix + error, file=sys.stderr)
    sys.exit(1)

#-----------------------------------------------------------------------------
# get on with it
#-----------------------------------------------------------------------------

import os
import os.path as osp
from glob import glob
from distutils.core import setup


here = osp.abspath(osp.dirname(__file__))
root = osp.join(here, name)

packages = []
for d, _, _ in os.walk(root):
    if osp.exists(osp.join(d, '__init__.py')):
        packages.append(d[len(here)+1:].replace(osp.sep, '.'))

version_ns = {}
with open(osp.join(here, 'version.py')) as f:
    exec(f.read(), {}, version_ns)

with open("summary.rst", "r") as f:
    long_description = f.read()

setup_args = dict(
    name = name,
    version = version_ns['__version__'],
    scripts = glob(osp.join('scripts', '*')),
    packages = packages,
    description = "metasetup",
    long_description = long_description,
    author = "Ryan Morshead",
    author_email = "ryan.morshead@gmail.com",
    url = "https://github.com/rmorshea/metasetup",
    license = "MIT",
    platforms = "Linux, Mac OS X, Windows",
    keywords = ["settings", "configuration"],
    classifiers = [
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        ],
)

if __name__ == '__main__':
    setup(**setup_args)
