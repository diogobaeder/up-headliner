import os
from setuptools import setup, find_packages

requires = [
        "Flask==0.10.1",
        "celery==3.1.5",
        "redis==2.8.0",
        "hiredis==0.1.1",
        "requests==2.0.1",
        "furl==0.3.6",
        "python-dateutil==2.2",
        "Fabric==1.8.1",
        "bleach==1.4",
]

if os.environ.has_key('MOZ_UPHEADLINER_DEV'):
    requires.extend([
        "ipython==1.1.0",
        "nose==1.3.0",
        "coverage==3.7.1",
        "mock==1.0.1",
        "flake8==2.1.0",
    ])
if os.environ.has_key('MOZ_UPHEADLINER_PROD'):
    requires.extend([
        "gunicorn==18.0",
        "gevent==1.0",
    ])

setup(
        name = "headliner",
        version = "0.5",
        description = "Demo content provider based on Mozilla UP interests",
        author = "Mozilla",
        packages=find_packages(),
        package_data={"": ["*.lua"]},
        include_package_data=True,
        install_requires = requires,
        scripts=["scripts/up-headliner-server", "scripts/up-headliner-scheduler", "scripts/up-headliner-worker", "scripts/populate_nytimes_mostpopular.py"],
)
