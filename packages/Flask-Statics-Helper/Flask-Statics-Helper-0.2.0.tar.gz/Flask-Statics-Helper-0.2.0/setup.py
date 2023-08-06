import ast
from codecs import open  # To use a consistent encoding
import os
import setuptools
import setuptools.command.sdist
from setuptools.command.test import test
import sys


setattr(setuptools.command.sdist, 'READMES',
        tuple(list(getattr(setuptools.command.sdist, 'READMES', ())) + ['README.md']))
here = os.path.abspath(os.path.dirname(__file__))


# Get the long description and other data from the relevant files
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
with open(os.path.join(here, 'flask_statics', '__init__.py'), encoding='utf-8') as f:
    lines = [l.strip() for l in f if l.startswith('__')]
metadata = ast.literal_eval("{'" + ", '".join([l.replace(' = ', "': ") for l in lines]) + '}')
__author__, __license__, __version__ = [metadata[k] for k in ('__author__', '__license__', '__version__')]
if not all((__author__, __license__, __version__)):
    raise ValueError('Failed to obtain metadata from module.')


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        setattr(self, 'test_args', ['tests'])
        setattr(self, 'test_suite', True)

    def run_tests(self):
        # Import here, cause outside the eggs aren't loaded.
        pytest = __import__('pytest')
        err_no = pytest.main(self.test_args)
        sys.exit(err_no)


class PyTestCov(PyTest):
    def finalize_options(self):
        test.finalize_options(self)
        setattr(self, 'test_args', ['--cov', 'flask_statics', 'tests'])
        setattr(self, 'test_suite', True)


# Setup definition.
setuptools.setup(
    name='Flask-Statics-Helper',
    version=__version__,

    description='Provides Bootstrap3 and other static resources in a modular fashion.',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/Robpol86/Flask-Statics-Helper',

    # Author details
    author=__author__,
    author_email='robpol86@gmail.com',

    # Choose your license
    license=__license__,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='flask',

    packages=['flask_statics'],
    include_package_data=True,
    zip_safe=False,

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=['Flask'],

    tests_require=['pytest'],
    cmdclass=dict(test=PyTest, testcov=PyTestCov),
)
