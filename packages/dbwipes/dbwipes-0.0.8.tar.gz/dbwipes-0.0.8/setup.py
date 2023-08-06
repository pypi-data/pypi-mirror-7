#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
from setuptools import setup, find_packages
import dbwipes

setup(name="dbwipes",
      version=dbwipes.__version__,
      description="dbwipes a database",
      license="MIT",
      author="Eugene Wu",
      author_email="eugenewu@mit.edu",
      url="http://github.com/sirrice/summary",
      packages = find_packages(),
      include_package_data = True,      
      package_data = {
        'static': 'dbwipes/static',
        'templates': 'dbwipes/templates'
      },
      package_dir = {'dbwipes' : 'dbwipes'},
      scripts = [
        'bin/dbwipesserver.py',
        'bin/summarizedb.py'
      ],
      #zip_safe = False,
      install_requires = [
        'flask', 'psycopg2', 'sqlalchemy', 
        'flask-compress', 'scorpionsql', 'click'
      ],
      keywords= "")
