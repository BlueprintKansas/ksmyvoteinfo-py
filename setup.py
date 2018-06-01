from setuptools import setup

setup(name='ksmyvoteinfo',
      version='0.2',
      description='Query the KS SOS site for voter registration',
      url='http://github.com/BlueprintKansas/ksmyvoteinfo-py',
      author='Peter Karman',
      author_email='peter@peknet.com',
      license='MIT',
      packages=['ksmyvoteinfo'],
      zip_safe=False,
      install_requires=['python-dateutil', 'robobrowser'])

