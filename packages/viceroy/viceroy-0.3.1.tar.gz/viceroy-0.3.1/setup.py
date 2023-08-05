from setuptools import setup, find_packages

from viceroy import __version__

setup(
    name='viceroy',
    version=__version__,
    packages=find_packages(),
    url='https://github.com/ojii/viceory',
    license='BSD',
    author='Jonas Obrist',
    author_email='ojiidotch@gmail.com',
    description='',
    install_requires=[
        'selenium',
        'slimit',
    ],
    tests_require=[
        'Django',
        'flask-testing',
        'flask',
    ],
    test_suite='viceroy.tests',
    zip_safe=False,
)
