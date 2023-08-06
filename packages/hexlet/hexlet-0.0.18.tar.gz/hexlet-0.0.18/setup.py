from setuptools import setup, find_packages
import os
from os import path

data_files = [path.join(dp.split(os.sep, 1)[1], f)
        for dp, dn, filenames in os.walk("hexlet/data")
        for f in filenames
        if f[0] != '.']

# raise Exception(data_files)

setup(
    name='hexlet',
    version='0.0.18',
    description="CLI for hexlet.io",
    long_description=open('README.rst').read(),
    # packages=['towelstuff',],
    license='MIT',
    author="Kirill Mokevnin",
    author_email="mokevnin@gmail.com",
    url="http://hexlet.io",
    packages=find_packages(),
    tests_require=[
        "pytest",
        "clint",
        "responses",
    ],
    install_requires=[
        'pyyaml==3.11',
        'requests==2.3.0',
        'python-i18n==0.3.0',
        'click==2.4',
        'purl==0.8'
    ],
    include_package_data = True,
    # # NOTE hack for tox
    package_data = {
        'hexlet': data_files
        },
    # dependency_links = ['[-e] git+https://github.com/mitsuhiko/click.git'],
    entry_points = {
        'console_scripts': [
            'hexlet=hexlet.cli:main',
            'hexlet-lesson=hexlet.lesson_cli:main'
            ],
    }
)
