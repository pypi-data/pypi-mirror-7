from distutils.core import setup

setup(name='ish_parser',
      version='0.0.3',
      author_email='thayden@gmail.com',
      description='Parser for NOAA ISH (integrated surface hourly) reports',
      author='thayden',
      url='https://github.com/haydenth/ish_parser',
      package_dir={'': 'src'},
      py_modules=['ish_parser', 'ish_report'])
