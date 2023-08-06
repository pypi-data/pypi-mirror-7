from setuptools import setup

VERSION = '1.0.0'

setup(
    name="protopigeon",
    version=VERSION,
    author='Jon Parrott',
    author_email='jjramone13@gmail.com',
    maintainer='Jon Parrott / Cloud Sherpas',
    maintainer_email='jonathan.parrott@cloudsherpas.com',
    description="A helper library for working with Google's protorpc and App Engine's datastore",
    url='https://bitbucket.org/jonparrott/protopigeon',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    packages=['protopigeon'],
    install_requires=[
    ],
)
