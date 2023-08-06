from setuptools import setup, find_packages

version = '2.0.6'

setup(name='plone.app.viewletmanager',
      version=version,
      description="configurable viewlet manager",
      long_description=open("README.rst").read() + "\n" + \
                       open("CHANGES.rst").read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
        ],
      keywords='',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.viewletmanager',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'zope.publisher',
            'zope.testing',
            'Products.CMFPlone',
            'Products.PloneTestCase',
        ]
      ),
      install_requires=[
        'setuptools',
        'zope.component',
        'zope.contentprovider',
        'zope.interface',
        'zope.site',
        'zope.viewlet',
        'Products.GenericSetup',
        'ZODB3',
        'Acquisition',
        'Zope2',
        'plone.app.vocabularies',
      ],
      )
