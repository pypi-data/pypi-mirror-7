from setuptools import setup

setup(name='royweb',
      version='0.1.1',
      url='http://github.com/tamasgal/royweb/',
      description='Restless Oyster online monitoring tool',
      author='Tamas Gal',
      author_email='tgal@km3net.de',
      packages=['royweb'],
      include_package_data=True,
      platforms='any',
      install_requires=[
          'tornado==3.2.2',
      ],
      entry_points={
          'console_scripts': [
              'royweb=royweb.royweb:main',
              'royweb_tester=royweb.royweb:send_test_parameter',
          ],
      },
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
      ],
)

__author__ = 'Tamas Gal'
