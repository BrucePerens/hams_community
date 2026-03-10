#!/bin/bash
# 1. Install Debian's official Python packaging tools
sudo apt-get update
sudo apt-get install -y python3-stdeb fakeroot python3-all python3-setuptools build-essential wget dh-python

# 2. Download the official PyPDF2 source from PyPI
wget https://pypi.io/packages/source/P/PyPDF2/PyPDF2-2.12.1.tar.gz

# 3. Extract the source code
tar -xzf PyPDF2-2.12.1.tar.gz
cd PyPDF2-2.12.1

# 4. Inject a shim setup.py
# PyPDF2 >= 2.12 transitioned to pyproject.toml and Flit, removing setup.py. 
# stdeb requires setup.py to build the Debian package, so we create a minimal shim.
cat << 'EOF' > setup.py
from setuptools import setup, find_packages

setup(
    name='PyPDF2',
    version='2.12.1',
    packages=find_packages(),
    include_package_data=True,
    description='A pure-python PDF library',
)
EOF

# Explicitly configure stdeb to build the Python 3 package
echo -e "[DEFAULT]\nX-Python3-Version: >= 3.6" > stdeb.cfg

# 5. Build the actual Debian package (.deb)
python3 setup.py --command-packages=stdeb.command bdist_deb

# 6. Install the newly compiled package
sudo dpkg -i deb_dist/python3-pypdf2_2.12.1-1_all.deb

# 7. Clean up the build files
cd ..
rm -rf PyPDF2-2.12.1 PyPDF2-2.12.1.tar.gz
