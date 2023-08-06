from distutils.core import setup
requires = [
'numpy',
'pandas'
]


setup(name='Quandl',
      version='2.0',
      description = "Package for Quandl API access",
      requires = requires,      
      author = "Mark Hartney, Chris Stevens",
      maintainer = 'Chris Stevens',
      maintainer_email = "connect@quandl.com",
      license = 'MIT',
      packages=['Quandl'],
      )