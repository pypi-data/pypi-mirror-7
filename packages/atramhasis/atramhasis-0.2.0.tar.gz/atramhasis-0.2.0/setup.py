import os
import distutils.file_util

from setuptools import setup, find_packages, distutils, Command

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()


def copy_files_scaffolds(filename, output_dir):
    source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
    dest_dir = os.path.join(os.path.dirname(__file__), 'atramhasis', 'scaffolds', output_dir, filename + '_tmpl')
    distutils.file_util.copy_file(source_dir, dest_dir, update=True)


class PrepareScaffold(Command):

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        copy_files_scaffolds("requirements.txt", "atramhasis_demo")
        copy_files_scaffolds("requirements-dev.txt", "atramhasis_demo")
        copy_files_scaffolds("requirements.txt", "atramhasis_scaffold")
        copy_files_scaffolds("requirements-dev.txt", "atramhasis_scaffold")


requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'skosprovider',
    'skosprovider_sqlalchemy',
    'pyramid_skosprovider',
    'pyramid_jinja2',
    'alembic',
    'babel',
    'colander',
    'requests',
    'dogpile.cache'
]

setup(name='atramhasis',
      version='0.2.0',
      description='atramhasis',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4"
      ],
      author='Flanders Heritage Agency',
      author_email='ict@onroerenderfgoed.be',
      url='http://atramhasis.readthedocs.org',
      keywords='web wsgi pyramid skos thesaurus',
      license='GPLv3',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='atramhasis',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = atramhasis:main
      [console_scripts]
      initialize_atramhasis_db = atramhasis.scripts.initializedb:main
      [pyramid.scaffold]
        atramhasis_scaffold=atramhasis.scaffolds:AtramhasisTemplate
        atramhasis_demo=atramhasis.scaffolds:AtramhasisDemoTemplate
      """,
      cmdclass={
          'prepare': PrepareScaffold
      }
)
