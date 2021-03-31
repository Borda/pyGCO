"""
The builder / installer

>> pip install -r requirements.txt
>> python setup.py build_ext --inplace
>> python setup.py install

For uploading to PyPi follow instructions
http://peterdowns.com/posts/first-time-with-pypi.html

Pre-release package
>> python setup.py sdist upload -r pypitest
>> pip install --index-url https://test.pypi.org/simple/ --upgrade gco-wrapper
Release package
>> python setup.py sdist upload -r pypi
>> pip install --upgrade gco-wrapper
"""

import os
import sys

try:
    from setuptools import Extension, setup  # , Command, find_packages
    from setuptools.command.build_ext import build_ext
except ImportError:
    from distutils.command.build_ext import build_ext
    from distutils.core import Extension, setup  # , Command, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))
PACKAGE_NAME = 'gco-v3.0.zip'
URL_LIB_GCO = 'http://vision.csd.uwo.ca/code/' + PACKAGE_NAME
LOCAL_SOURCE = 'gco_source'


def _parse_requirements(file_path):
    with open(file_path) as fp:
        reqs = [r.rstrip() for r in fp.readlines() if not r.startswith('#')]
        return reqs


class BuildExt(build_ext):
    """ build_ext command for use when numpy headers are needed.
    SEE: https://stackoverflow.com/questions/2379898
    SEE: https://stackoverflow.com/questions/19919905/how-to-bootstrap-numpy-installation-in-setup-py
    """

    def get_export_symbols(self, ext):
        return None

    def finalize_options(self):
        build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        # __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())


SOURCE_FILES = [
    'graph.cpp',
    'maxflow.cpp',
    'LinkedBlockList.cpp',
    'GCoptimization.cpp',
]
gco_files = [os.path.join(LOCAL_SOURCE, f) for f in SOURCE_FILES]
gco_files += [os.path.join('gco', 'cgco.cpp')]

if sys.version_info.major == 2:
    # numpy v1.17 drops support for py2
    setup_reqs = ['Cython', 'numpy<1.17']
    install_reqs = _parse_requirements(os.path.join(HERE, 'requirements-py2.txt'))
else:
    setup_reqs = ['Cython', 'numpy']
    install_reqs = _parse_requirements(os.path.join(HERE, 'requirements.txt'))

setup(
    name='gco-wrapper',
    url='http://vision.csd.uwo.ca/code/',
    packages=['gco'],
    version='3.0.7',
    license='MIT',
    author='Yujia Li & A. Mueller',
    author_email='yujiali@cs.tornto.edu',
    maintainer='Jiri Borovec',
    maintainer_email='jiri.borovec@fel.cvut.cz',
    description='pyGCO: a python wrapper for the graph cuts package',
    download_url='https://github.com/Borda/pyGCO',
    project_urls={
        "Source Code": "https://github.com/Borda/pyGCO",
    },
    zip_safe=False,
    cmdclass={'build_ext': BuildExt},
    ext_modules=[
        Extension(
            'gco.libcgco',
            gco_files,
            language='c++',
            include_dirs=[LOCAL_SOURCE],
            library_dirs=[LOCAL_SOURCE],
            # extra_compile_args=["-fpermissive"],
        ),
    ],
    setup_requires=setup_reqs,
    install_requires=install_reqs,
    # test_suite='nose.collector',
    # tests_require=['nose'],
    include_package_data=True,

    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        # "Topic :: Scientific/Engineering :: Image Segmentation",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
