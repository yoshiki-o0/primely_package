import os, sys

from setuptools import setup, find_packages


def read_requirements():
    """Parse requirements from requirements.txt."""

    reqs_path = os.path.join('.', 'requirements.txt')
    with open(reqs_path, 'r') as f:
        requirements = [line.rstrip() for line in f]
    return requirements

setup(
    name='primelyr',
    version='0.0.1',
    description='Converts paychecks and returns json parameters',
    long_description='README.md',
    author='Yoshiki Nakagawa',
    author_email='ben.nakagawa01@gmail.com',
    install_requires=read_requirements(),
    url='https://github.com/yoshiki-o0/primely_package',
    lincense='LICENCE',
    # package_dir={'': 'primely'},
    packages=find_packages(),
    # packages=[
    #     'core_primely.controller',
    #     'core_primely.models',
    #     'core_primely.templates',
    #     'core_primely.views',
    #     'tools'
    # ],
    test_suite='tests'
)