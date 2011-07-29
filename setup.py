from os.path import join
from setuptools import setup, find_packages, Extension, Feature

version = '1.1'

base = join('experimental', 'btree')

codeoptimization = Feature("Optional code optimizations",
    standard=True,
      ext_modules=[
        Extension(
          name='experimental.btree.difference',
          sources=[join(base, 'difference.c')]
        ),
        Extension(
          name='experimental.btree.intersection',
          sources=[join(base, 'intersection.c')],
        ),
      ],
)

setup(name='experimental.btree',
      version=version,
      description="ZODB BTree optimizations",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        ],
      keywords='plone zodb btree',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['experimental'],
      include_package_data=True,
      zip_safe=False,
      features = {'codeoptimization': codeoptimization},
      install_requires=[
          'setuptools',
          'Products.ExtendedPathIndex',
          'Products.ZCatalog',
          'ZODB3',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
