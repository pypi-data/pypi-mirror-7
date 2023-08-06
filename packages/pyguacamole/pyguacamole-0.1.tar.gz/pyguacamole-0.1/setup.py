from setuptools import setup, find_packages

from guacamole import VERSION


with open('README.md') as f:
    README = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()


setup(
    name='pyguacamole',
    version=VERSION,
    url='https://github.com/mohabusama/pyguacamole',
    author='Mohab Usama',
    author_email='mohab.usama@gmail.com',
    description=('A Guacamole python client library.'),
    long_description=README,
    license=LICENSE,
    zip_safe=False,
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
