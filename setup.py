import os
import re
from setuptools import setup, find_packages


def get_version():
    version_file = os.path.join(os.path.dirname(
        __file__), 'MultiRepoPatch', '__init__.py')
    with open(version_file, 'r') as f:
        version_content = f.read()
        version_match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", version_content, re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


setup(
    name='multi repo patch',
    version=get_version(),
    packages=find_packages(),
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'mrpatch=MultiRepoPatch.multi_repo_patch:main',
        ],
    },
    author='Shota Iuchi',
    author_email='shotaiuchi.develop@gmail.com',
    description='Applying patches to multiple repositories.',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='repository, git, multi, patch',
    url='https://github.com/ShotaIuchi/multi_repo_patch',
)
