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
import pip
import logging
import pkg_resources
# import traceback
try:
    from setuptools import setup, Extension # , Command, find_packages
    from setuptools.command.build_ext import build_ext
except ImportError:
    from distutils.core import setup, Extension # , Command, find_packages
    from distutils.command.build_ext import build_ext

PACKAGE_NAME = 'gco-v3.0.zip'
GCO_LIB = 'http://vision.csd.uwo.ca/code/' + PACKAGE_NAME
LOCAL_SOURCE = 'gco_source'
DOWNLOAD_SOURCE = False


def _parse_requirements(file_path):
    pip_version = list(map(int, pkg_resources.get_distribution('pip').version.split('.')[:2]))
    if pip_version >= [6, 0]:
        raw = pip.req.parse_requirements(file_path, session=pip.download.PipSession())
    else:
        raw = pip.req.parse_requirements(file_path)
    return [str(i.req) for i in raw]


class BuildExt(build_ext):
    """ build_ext command for use when numpy headers are needed.
    SEE: https://stackoverflow.com/questions/2379898
    SEE: https://stackoverflow.com/questions/19919905/how-to-bootstrap-numpy-installation-in-setup-py
    """

    def finalize_options(self):
        build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        # __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())


if DOWNLOAD_SOURCE:
    try:
        import urllib3
        import zipfile
        import shutil
        # download code
        if not os.path.exists(PACKAGE_NAME):
            http = urllib3.PoolManager()
            with http.request('GET', GCO_LIB, preload_content=False) as resp, \
                    open(PACKAGE_NAME, 'wb') as out_file:
                shutil.copyfileobj(resp, out_file)
            resp.release_conn()

        # try:
        #     if not os.path.exists(LOCAL_SOURCE):
        #         os.mkdir(LOCAL_SOURCE)
        # except:
        #     print('no permission to create a directory')

        # unzip the package
        with zipfile.ZipFile(PACKAGE_NAME, 'r') as zip_ref:
            zip_ref.extractall(LOCAL_SOURCE)
    except:
        logging.warning('Fail source download or unzip, so last VCS will be used.')
        #logging.warning(traceback.format_exc())


source_files = ['graph.cpp', 'maxflow.cpp',
                'LinkedBlockList.cpp', 'GCoptimization.cpp']
gco_files = [os.path.join(LOCAL_SOURCE, f) for f in source_files]
gco_files += [os.path.join('gco', 'cgco.cpp')]


# parse_requirements() returns generator of pip.req.InstallRequirement objects
try:
    install_reqs = _parse_requirements("requirements.txt")
except:
    logging.warning('Fail load requirements file, so using default ones.')
    install_reqs = ['Cython', 'numpy']


setup(name='gco-wrapper',
      url='http://vision.csd.uwo.ca/code/',
      packages=['gco'],
      version='3.0.2',
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
      ext_modules=[Extension('gco.libcgco',
                             gco_files,
                             language='c++',
                             include_dirs=[LOCAL_SOURCE],
                             library_dirs=[LOCAL_SOURCE],
                             extra_compile_args=["-fpermissive"]
                   )],
      setup_requires=['numpy'],
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
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],
)
