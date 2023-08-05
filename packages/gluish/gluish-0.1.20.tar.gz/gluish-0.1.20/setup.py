# coding: utf-8

"""
Some glue around luigi.

Provides a base class, that autogenerates its output filenames based on some
tag, classname and parameters.

Additionally, provide some smaller utilities, like a TSV format, a benchmark
decorator and some task templates.
"""
from setuptools import setup


setup(name='gluish',
      version='0.1.20',
      description='Utils around Luigi.',
      url='https://github.com/miku/gluish',
      author='Martin Czygan',
      author_email='martin.czygan@gmail.com',
      packages=[
        'gluish',
      ],
      package_dir={'gluish': 'gluish'},
      install_requires=[
        # 'MySQL-python==1.2.5',
        'BeautifulSoup==3.2.1',
        'colorama==0.2.7',
        'elasticsearch==1.0.0',
        'luigi>=1.0.13',
        'nose==1.3.1',
        'python-dateutil==2.2',
        'requests>=2.2.1',
        'six==1.6.1',
        'sqlitebck==1.2.1',
        'urllib3==1.8',
        'wsgiref==0.1.2',
      ],
)
