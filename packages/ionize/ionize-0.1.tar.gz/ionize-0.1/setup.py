from distutils.core import setup

setup(name='ionize',
      version='0.1',
      author='Lewis A. Marshall',
      author_email='lewis.a.marshall@gmail.com',
      url="http://lewisamarshall.github.io/ionize/",
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
          "Operating System :: OS Independent",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Scientific/Engineering :: Chemistry",
          ],
      license='LICENSE',
      description='A unified Python package for calculating buffer properties.',
      long_description=open('README.txt').read(),
      packages=['ionize'],
      requires=['numpy', 'scipy']
      )
