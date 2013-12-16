import os
from setuptools import setup

requires = [
        "Flask==0.10.1",
        "uWSGI==1.9.20",
        "celery==3.1.5",
        "redis==2.8.0",
        "hiredis==0.1.1",
        "requests==2.0.1",
        "furl==0.3.6",
        "python-dateutil==2.2",
        "gevent==1.0",
        "grequests==0.2.0",
]

if os.environ.has_key('MOZ_UPHEADLINER_DEV'):
    requires.extend([
        "ipython==1.1.0",
        "nose==1.3.0",
    ])
if os.environ.has_key('MOZ_UPHEADLINER_PROD'):
    requires.extend([
        "uWSGI==1.9.20",
    ])

setup(
        name = "headliner",
        version = "0.1",
        description = "Demo content provider based on Mozilla UP interests",
        author = "Mozilla",
        packages=["up.headliner"],
        namespace_packages=["up", "up.headliner"],
        include_package_data=True,
        install_requires = requires,
        scripts=["scripts/up-headliner-server"],
)
