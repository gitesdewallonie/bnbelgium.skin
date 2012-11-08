from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='bnbelgium.skin',
      version=version,
      description="Skin for bnbelgium.be",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='Affinitic Team',
      author_email='info@affinitic.be',
      url='http://svn.affinitic.be/plone/gites/bnbelgium.skin',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bnbelgium'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.editskinswitcher',
          'z3c.jbot'])
