from setuptools import setup, find_packages
import sys, os

version = '1.0.1'
shortdesc = 'Node Implementation with ZODB persistence'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'CHANGES.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()

setup(name='node.ext.zodb',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Operating System :: OS Independent',
            'Programming Language :: Python', 
            'Topic :: Utilities',
            'License :: OSI Approved :: BSD License',
      ],
      keywords='node odict zodb persistent tree',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['node', 'node.ext'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'node',
          'ZODB3',
      ],
      extras_require = dict(
          test=[
                'interlude',
          ]
      ),
      tests_require=['interlude'],
      test_suite="node.ext.zodb.tests.test_suite"
)

