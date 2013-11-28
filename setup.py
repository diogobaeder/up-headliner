import os
from setuptools import setup

requires = [
        "Flask==0.10.1",
        "uWSGI==1.9.20",
]

if os.environ.has_key('MOZ_UPHEADLINER_DEV'):
    requires.extend([
        "ipython==1.1.0",
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
        scripts=["scripts/up-headliner-server"]
)
