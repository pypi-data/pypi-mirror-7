#! /usr/bin/env python

''' Setup script for django-cms-ajax-text-plugin
'''

import glob
import re
import sys
import os

from setuptools import setup, find_packages
from setuptools.command.install_lib import install_lib as _install_lib
from distutils.command.build import build as _build
from distutils.command.sdist import sdist
from distutils.cmd import Command

class compile_translations(Command):
    description = 'compile message catalogs to MO files via django compilemessages'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            from django.core.management.commands.compilemessages import \
                compile_messages
            for path in ['cms_ajax_text_plugin']:
                if path.endswith('.py'):
                    continue
                if not os.path.isdir(os.path.join(path, 'locale')):
                    continue
                curdir = os.getcwd()
                os.chdir(os.path.realpath(path))
                compile_messages(sys.stderr)
                os.chdir(curdir)
        except ImportError:
            print
            sys.stderr.write('!!! Please install Django >= 1.4 to build translations')
            print
            print

class build(_build):
    sub_commands = [('compile_translations', None)] + _build.sub_commands

class install_lib(_install_lib):
    def run(self):
        self.run_command('compile_translations')
        _install_lib.run(self)

class eo_sdist(sdist):

    def run(self):
        if os.path.exists('VERSION'):
            os.remove('VERSION')
        version = get_version()
        if '.g' in version:
            print "creating VERSION file"
            version_file = open('VERSION', 'w')
            version_file.write(version)
            version_file.close()
        sdist.run(self)
        if os.path.exists('VERSION'):
            os.remove('VERSION')

def get_version():

    version = None
    if os.path.exists('VERSION'):
        version_file = open('VERSION', 'r')
        version = version_file.read()
        version_file.close()
        return version
    for d in glob.glob('*'):
        if not os.path.isdir(d):
            continue
        module_file = os.path.join(d, '__init__.py')
        if not os.path.exists(module_file):
            continue
        for v in re.findall("""__version__ *= *['"](.*)['"]""",
                open(module_file).read()):
            assert version is None
            version = v
        if version:
            break
    assert version is not None
    if os.path.exists('.git'):
        import subprocess
        p = subprocess.Popen(['git','describe','--dirty','--match=v*'],
                stdout=subprocess.PIPE)
        result = p.communicate()[0]
        assert p.returncode == 0, 'git returned non-zero'
        new_version = result.split()[0][1:]
        assert new_version.split('-')[0] == version, '__version__ must match the last git annotated tag'
        version = new_version.replace('-', '.')
    return version


setup(name="django-cms-ajax-text-plugin",
      version=get_version(),
      license="BSD license",
      description="",
      author="Entr'ouvert",
      author_email="info@entrouvert.org",
      maintainer="Serghei Mihai",
      maintainer_email="smihai@entrouvert.com",
      include_package_data=True,
      packages=find_packages(),
      setup_requires=[
            'django>=1.4',
      ],
      install_requires=[
            'django-cms<3',
            'djangocms-text-ckeditor',
      ],
      cmdclass={'build': build, 'install_lib': install_lib,
          'compile_translations': compile_translations,
          'sdist': eo_sdist},
)
