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
import re
import sys
from importlib.util import module_from_spec, spec_from_file_location

try:
    from setuptools import Extension, find_packages, setup
    from setuptools.command.build_ext import build_ext
except ImportError:
    from distutils.command.build_ext import build_ext
    from distutils.core import Extension, setup

PACKAGE_NAME = os.path.join("gco-v3.0.zip")
URL_LIB_GCO = "http://vision.csd.uwo.ca/code/" + PACKAGE_NAME
LOCAL_SOURCE = os.path.join("src", "gco_cpp")


def _load_py_module(name: str, location: str):
    spec = spec_from_file_location(name, location)
    py = module_from_spec(spec)
    spec.loader.exec_module(py)
    return py


class BuildExt(build_ext):
    """build_ext command for use when numpy headers are needed.
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


GCO_FILES = [
    os.path.join(LOCAL_SOURCE, f) for f in ("graph.cpp", "maxflow.cpp", "LinkedBlockList.cpp", "GCoptimization.cpp")
]
GCO_FILES += [os.path.join("src", "gco", "cgco.cpp")]

if sys.version_info.major == 2:
    # numpy v1.17 drops support for py2
    SETUP_REQUIRES = INSTALL_REQUIRES = ["Cython>=0.23.1", "numpy>=1.8.2, <1.17"]
else:
    SETUP_REQUIRES = INSTALL_REQUIRES = ["Cython>=0.23.1", "numpy>=1.8.2"]

ABOUT = _load_py_module(name="about", location=os.path.join("src", "gco", "__about__.py"))

with open("README.md", encoding="utf_8") as fp:
    readme = re.sub(
        # replace image pattern
        pattern=r"\!\[([\w ]+)\]\(\./(.+)\)",
        # with static urls and the same format
        repl=rf"![\1](https://raw.githubusercontent.com/borda/pyGCO/{ABOUT.__version__}/\2)",
        # for whole README
        string=fp.read(),
    )

setup(
    name="gco-wrapper",
    url="http://vision.csd.uwo.ca/code/",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # edit also gco.__init__.py!
    version=ABOUT.__version__,
    license="MIT",
    author="Yujia Li & A. Mueller",
    author_email="yujiali@cs.tornto.edu",
    maintainer="Jiri Borovec",
    maintainer_email="jiri.borovec@fel.cvut.cz",
    description="pyGCO: a python wrapper for the graph cuts package",
    long_description=readme,
    long_description_content_type="text/markdown",
    download_url="https://github.com/Borda/pyGCO",
    project_urls={
        "Source Code": "https://github.com/Borda/pyGCO",
    },
    zip_safe=False,
    cmdclass={"build_ext": BuildExt},
    ext_modules=[
        Extension(
            "gco.libcgco",
            GCO_FILES,
            language="c++",
            include_dirs=[LOCAL_SOURCE],
            library_dirs=[LOCAL_SOURCE],
            # Downgrade some diagnostics about nonconformant code from errors to warnings.
            # extra_compile_args=["-fpermissive"],
        ),
    ],
    setup_requires=SETUP_REQUIRES,
    install_requires=INSTALL_REQUIRES,
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
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
