from setuptools import setup

setup(name='ksmyvoteinfo',
      version='1.3',
      description='Query the KS SOS site for voter registration',
      url='http://github.com/BlueprintKansas/ksmyvoteinfo-py',
      author='Peter Karman',
      author_email='peter@peknet.com',
      license='MIT',
      packages=['ksmyvoteinfo'],
      zip_safe=False,
      install_requires=['python-dateutil', 'requests', 'beautifulsoup4'])

