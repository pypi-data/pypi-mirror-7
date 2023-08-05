from distutils.core import setup

setup(
    name='keystok',
    version='0.1.5',
    author='Kenneth Falck',
    author_email='kennu@iki.fi',
    packages=['keystok'],
    scripts=['bin/keystok'],
    url='https://keystok.com',
    license='LICENSE.txt',
    description='Keystok Python Client',
    keywords=['keystok', 'client'],
    long_description=open('README.txt').read(),
    install_requires=[
        'pycrypto',
        'pbkdf2',
        'requests',
    ],
)
