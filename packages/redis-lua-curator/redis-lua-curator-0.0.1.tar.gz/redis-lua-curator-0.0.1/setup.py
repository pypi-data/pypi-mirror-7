import os
import re

from setuptools import (
    find_packages,
    setup,
)

version_re = re.compile(r"__version__\s*=\s*['\"](.*?)['\"]")


def get_version():
    base = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base, 'curator/__init__.py')) as initf:
        for line in initf:
            m = version_re.match(line.strip())
            if not m:
                continue
            return m.groups()[0]

setup(
    name='redis-lua-curator',
    version=get_version(),
    description='Helper for working with lua scripts.',
    packages=find_packages(),
    author='Michael Hahn',
    author_email='mwhahn@gmail.com',
    url='https://github.com/mhahn/curator/',
    download_url='https://github.com/mhahn/curator/tarball/%s' % (
        get_version(),
    ),
    setup_requires=[
        'nose>=1.0',
        'coverage>=1.0',
        'ipython==0.13.2',
        'ipdb==0.8',
    ],
    install_requires=[
        'redis==2.10.1',
        'jinja2==2.7.2',
    ],
    keywords=['redis', 'lua'],
)
