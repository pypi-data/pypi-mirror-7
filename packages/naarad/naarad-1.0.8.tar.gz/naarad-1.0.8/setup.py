#! /usr/bin/python

from setuptools import setup, find_packages

naarad_version = '1.0.8'

with open('requirements.txt') as f:
      required = f.read().splitlines()

setup(name="naarad",
      description='A performance analysis tool',
      url='https://github.com/linkedin/naarad',
      author='Naarad Developers',
      author_email='naarad-dev@googlegroups.com',
      version=naarad_version,
      packages=['naarad', 'naarad.metrics', 'naarad.graphing', 'naarad.reporting', 'naarad.run_steps', 'naarad.resources'],  
      scripts = ['bin/naarad', 'bin/PrintGCStats'],
      package_dir={ '' : 'src'},
      package_data={ '' : ['src/naarad/resources/*.html']},
      include_package_data=True,
      install_requires=required,
      license='Apache 2.0',
      download_url='https://github.com/linkedin/naarad/archive/v' + naarad_version + '.zip'
      )
