from __future__ import with_statement
import os
import re
import operator
from setuptools import setup, find_packages
from dev_appserver import EXTRA_PATHS, OAUTH_CLIENT_EXTRA_PATHS


try:
    from os.path import relpath
except ImportError:
    def relpath(abs_path, start=None):
        pos = abs_path.index(start)
        path = abs_path[pos + len(start):]
        if path.startswith('/'):
            path = path[1:]
        return path
try:
    next
except:
    def next(*args):
        params = list(args)
        try:
            return params.pop(0).next()
        except StopIteration:
            if params:
                return params.pop(0)
            else:
                raise

SETUP_DIRPATH = os.path.dirname(os.path.realpath(__file__))
PATHS = EXTRA_PATHS + OAUTH_CLIENT_EXTRA_PATHS

path_packages = dict([path, find_packages(path)] for path in PATHS
    if 'google.appengine._internal.graphy' not in path)
packages = reduce(operator.add, path_packages.values())

package_dir = dict()
for path, pkgs in path_packages.items():
    pkg_relpath = relpath(path, SETUP_DIRPATH)
    data = ([p, os.path.join(pkg_relpath, p)] for p in pkgs if '.' not in p)
    package_dir.update(data)

version_regex = re.compile('release: "(?P<version_string>[^"]+)"')
with open('VERSION', 'r') as f:
    filters = (re.match(version_regex, l).group(
        'version_string') for l in f if re.match(version_regex, l))
    version = next(filters, None)

setup(
    name='googleappengine-python',
    version=version,
    license='Apache License, Version 2.0',
    url='http://code.google.com/appengine/',
    packages=packages,
    package_dir=package_dir,
    include_package_data=True,
    package_data={'google.appengine.ext.builtins': ['admin_redirect/*yaml',
                                                    'appstats/*yaml',
                                                    'datastore_admin/*yaml',
                                                    'default/*yaml',
                                                    'deferred/*yaml',
                                                    'django_wsgi/*yaml',
                                                    'mapreduce/*yaml',
                                                    'remote_api/*yaml']},
    data_files=[('', ['VERSION']),
                ('lib/cacerts', ['lib/cacerts/cacerts.txt',
                                'lib/cacerts/urlfetch_cacerts.txt'])],
    scripts=['google/appengine/tools/dev_appserver_main.py',
             'google/appengine/tools/appcfg.py'],
    zip_safe=False,
    )
