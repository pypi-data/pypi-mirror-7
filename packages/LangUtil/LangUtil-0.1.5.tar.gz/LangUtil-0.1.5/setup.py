from distutils.core import setup

setup(
    name='LangUtil',
    version='0.1.5',
    author='Andrew Udvare',
    author_email='audvare@gmail.com',
    packages=['langutil'],
    url='http://pypi.python.org/pypi/LangUtil/',
    license='LICENSE.txt',
    description='Helpers for generating code.',
    long_description=open('README.rst').read(),
    install_requires=[
        'phpserialize==1.3',
    ],
)
