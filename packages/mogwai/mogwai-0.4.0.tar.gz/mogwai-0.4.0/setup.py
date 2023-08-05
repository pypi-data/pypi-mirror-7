import sys
from setuptools import setup, find_packages

#next time:
#python setup.py register
#python setup.py sdist upload

version = open('mogwai/VERSION', 'r').readline().strip()
develop_requires = [dep.strip() for dep in open('requirements.pip', 'r').readlines()]

long_desc = """
mogwai is an Object-Graph Mapper (OGM) for Python

`Documentation <https://mogwai.readthedocs.org/en/latest/>`_

`Report a Bug <https://bitbucket.org/wellaware/mogwai/issues>`_
"""

setup(
    name='mogwai',
    version=version,
    description='Titan Object-Graph Mapper (OGM)',
    dependency_links=['https://bitbucket.org/wellaware/mogwai/archive/{0}.tar.gz#egg=mogwai-{0}'.format(version)],
    long_description=long_desc,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Environment :: Other Environment",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='cassandra,titan,ogm,mogwai,thunderdome',
    install_requires=['pyparsing>=1.5.7',
                      'rexpro>=0.2.0',
                      'six>=1.6.1',
                      'argparse>=1.2.1',
                      'factory-boy>=2.3.1',
                      'pyformance==0.2.4',
                      'Twisted>=13.2.0',
                      'pytz>=2013.9'],
    extras_require={
        'develop': develop_requires,
        'newrelic': ['newrelic>=2.18.1.15'],
        'docs': ['Sphinx>=1.2.2', 'sphinx-rtd-theme>=0.1.6', 'watchdog>=0.7.1', 'newrelic>=2.18.1.15'],
        'gevent': ['rexpro[gevent]>=0.2.0'],
        'eventlet': ['rexpro[eventlet]>=0.2.0'],
    },
    test_suite='nose.collector',
    tests_require=develop_requires,
    author='Cody Lee',
    author_email='codylee@wellaware.us',
    maintainer='Cody Lee',
    maintainer_email='codylee@wellaware.us',
    url='https://bitbucket.org/wellaware/mogwai',
    license='Apache Software License 2.0',
    packages=find_packages(),
    include_package_data=True,
)
