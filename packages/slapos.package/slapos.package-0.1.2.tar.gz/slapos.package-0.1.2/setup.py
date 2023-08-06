from setuptools import setup, find_packages

version = '0.1.2'
name = 'slapos.package'
long_description = open("README.txt").read() + "\n" + \
    open("CHANGES.txt").read() + "\n"

setup(name=name,
      version=version,
      description="SlapOS Package Utils",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='slapos package update',
      license='GPLv3',
      url='http://www.slapos.org',
      author='VIFIB',
      namespace_packages=['slapos'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'slapos.libnetworkcache>=0.14.1',
          'iniparse',
      ],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              # Those entry points are development version and
              # self updatable API
              'slappkg-update-raw = slapos.package.update:do_update',
              'slappkg-discover-raw = slapos.package.distribution:do_discover',
              'slappkg-upload-key-raw = slapos.package.upload_key:main',
              'slappkg-conf-raw = slapos.package.conf:do_conf',
              'slappkg-update = slapos.package.autoupdate:do_update',
              'slappkg-discover = slapos.package.autoupdate:do_discover',
              'slappkg-upload-key = slapos.package.autoupdate:do_upload',
              'slappkg-conf = slapos.package.autoupdate:do_conf',
          ],

        # Not supported yet
        #'slapos.cli': [
        #  'package upload-key = slapos.package.upload_key:main'
        #  ]
      },
      test_suite="slapos.package.test",
)
