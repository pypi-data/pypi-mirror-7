from setuptools import setup
from setuptools import find_packages

version = '4.0'

requires = [
    'setuptools',
    'pyramid_sqlalchemy',
    'SQLAlchemy >= 0.8.0',
    'IPy',
    ]

tests_require = [
    'mock',
    's4u.upgrade',
    ]

setup(name='s4u.sqlalchemy',
      version=version,
      description='SQLAlchemy integration for pyramid',
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
          'Topic :: Database',
          'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      author='Simplon B.V. - Wichert Akkerman',
      author_email='wichert@wiggy.net',
      url='https://s4usqlalchemy.readthedocs.org',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      namespace_packages=['s4u'],
      zip_safe=False,
      install_requires=requires,
      tests_require=tests_require,
      extras_require={
          'docs': ['sphinx'],
          'tests': tests_require,
          },
      test_suite='s4u.sqlalchemy')
