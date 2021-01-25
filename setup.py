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

try:
    from setuptools import setup, Extension # , Command, find_packages
    from setuptools.command.build_ext import build_ext
except ImportError:
    from distutils.core import setup, Extension # , Command, find_packages
    from distutils.command.build_ext import build_ext

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


# if DOWNLOAD_SOURCE:
#     PACKAGE_NAME = 'gco-v3.0.zip'
#     GCO_LIB = 'http://vision.csd.uwo.ca/code/' + PACKAGE_NAME
#     try:
#         import urllib3
#         import zipfile
#         import shutil
#         # download code
#         if not os.path.exists(PACKAGE_NAME):
#             http = urllib3.PoolManager()
#             with http.request('GET', GCO_LIB, preload_content=False) as resp, \
#                     open(PACKAGE_NAME, 'wb') as out_file:
#                 shutil.copyfileobj(resp, out_file)
#             resp.release_conn()
#
#         # unzip the package
#         with zipfile.ZipFile(PACKAGE_NAME, 'r') as zip_ref:
#             zip_ref.extractall(LOCAL_SOURCE)
#     except Exception:
#         logging.warning('Fail download or unzip source, so local VCS is used.')


SOURCE_FILES = [
    'graph.cpp',
    'maxflow.cpp',
    'LinkedBlockList.cpp',
    'GCoptimization.cpp',
]
gco_files = [os.path.join(LOCAL_SOURCE, f) for f in SOURCE_FILES]
gco_files += [os.path.join('gco', 'cgco.cpp')]

install_reqs = _parse_requirements(os.path.join(HERE, 'requirements.txt'))

setup(name='gco-wrapper',
      url='http://vision.csd.uwo.ca/code/',
      packages=['gco'],
      version='3.0.4',
      license='MIT',

      author='Yujia Li & A. Mueller',
      author_email='yujiali@cs.tornto.edu',
      maintainer='Jiri Borovec',
      maintainer_email='jiri.borovec@fel.cvut.cz',
      description='pyGCO: a python wrapper for the graph cuts package',
      download_url='https://github.com/Borda/pyGCO',
      platforms=['Linux'],

      zip_safe=False,
      cmdclass={'build_ext': BuildExt},
      ext_modules=[
          Extension('gco.libcgco',
                    gco_files,
                    language='c++',
                    include_dirs=[LOCAL_SOURCE],
                    library_dirs=[LOCAL_SOURCE],
                    # extra_compile_args=["-fpermissive"],
                    ),
      ],
      setup_requires=['numpy<1.17'],  # numpy v1.17 drops support for py2
      install_requires=install_reqs,
      # test_suite='nose.collector',
      # tests_require=['nose'],
      include_package_data=True,

      long_description='This is a python wrapper for gco package '
                       '(http://vision.csd.uwo.ca/code/), '
                       'which implements a graph cuts based move-making '
                       'algorithm for optimization in Markov Random Fields.',
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
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
      ],
)
