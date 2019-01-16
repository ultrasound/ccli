
from setuptools import setup, find_packages
from ccli.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='ccli',
    version=VERSION,
    description='Manage Public Cloud',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Nick Kim',
    url='https://github.com/ultrasound/ccli',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'ccli': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        ccli = ccli.main:main
    """,
)
