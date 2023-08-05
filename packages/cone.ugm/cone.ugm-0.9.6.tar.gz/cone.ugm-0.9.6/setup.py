import os
from setuptools import (
    setup,
    find_packages,
)


version = '0.9.6'
shortdesc = 'cone.ugm'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()


setup(name='cone.ugm',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          'Environment :: Web Environment',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'http://github.com/bluedynamics/cone.ugm',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['cone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'cone.app',
          'yafowil.widget.array',
          'yafowil.widget.autocomplete',
          'yafowil.widget.datetime',
          'yafowil.widget.dict',
          'yafowil.widget.image',
          'node.ext.ldap',
          #'repoze.profile',
      ],
      extras_require = dict(
          test=[
                'interlude',
          ]
      ),
      tests_require=[
          'interlude',
      ],
      test_suite = "cone.ugm.tests.test_suite",
      message_extractors = {
          '.': [
              ('**.py', 'lingua_python', None),
              ('**.pt', 'lingua_xml', None),
          ]
      }
      )
