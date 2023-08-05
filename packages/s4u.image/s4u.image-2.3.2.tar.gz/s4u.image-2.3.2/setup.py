from setuptools import setup
from setuptools import find_packages

version = '2.3.2'

requires = [
    'setuptools',
    's4u.sqlalchemy >=1.2',
    'repoze.filesafe >=2.0',
    'Pillow',
    'requests',
    ]

test_requires = [
    'mock >=0.8',
    's4u.upgrade',
    ]

setup(name='s4u.image',
      version=version,
      description='2Style4You image library',
      long_description=open('README.rst').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Framework :: Pyramid',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      author='Simplon B.V. - Wichert Akkerman',
      author_email='wichert@wiggy.net',
      url='https://s4uimage.readthedocs.org/en/latest/',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      namespace_packages=['s4u'],
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={
          'docs': ['sphinx'],
          'tests': test_requires,
      },
      test_suite='s4u.image')
