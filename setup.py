import os
from os import path
# os.system("pip3 install gitpython")

# import git
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# requires_list = []
# with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
#     for line in f:
#         requires_list.append(str(line))

setup(
    name='src',
    version='1.0',
    keywords='src',
    description='SafeExp library',
    license='MIT',
    url='https://github.com/StriderOne/PainterControl',
    packages=['src'],
    include_package_data=True,
)