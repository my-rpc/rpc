import os
from setuptools import setup, find_packages


# ===================================

PROJECT_NAME = 'rpc-mis'
VERSION = '0.8.11'
DESCRIPTION = 'user_profile, removed the extra bootstrap file from template.js and fixed the issue of spelling in employee details'
AUTHOR = 'IMOR and RPC Team'
AUTHOR_EMAIL = 'sau.ahmadi@gmail.com'
URL = f''

# ===================================

# read the contents of your README file
with open("README.md", "r", encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

# Version Number
try:
    # used for teamcity builds (library is uploaded to nexus)
    VERSION = os.environ['BUILD_NUMBER']
except Exception as e:
    # used for local builds
    VERSION = VERSION

# Requirements
with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

# ===================================

setup(
    name=PROJECT_NAME,
    version=VERSION,
    description=DESCRIPTION,
    url=URL,
    install_requires=REQUIREMENTS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license='(c) Reliance Power Group Afghanistan',
    packages=find_packages(exclude=["car_code/notebooks", "car_code", "car_code.*", "*.car_code", "*.car_code.*"]),
    long_description_content_type="text/markdown",
    python_requires='>=3.8.4',
    include_package_data=True
)
