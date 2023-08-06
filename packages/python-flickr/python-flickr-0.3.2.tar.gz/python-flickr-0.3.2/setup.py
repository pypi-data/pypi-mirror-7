#!/usr/bin/env python

from setuptools import setup

setup(
    name='python-flickr',
    version='0.3.2',
    install_requires=['httplib2', 'oauth2', 'simplejson'],
    author='Mike Helmick',
    author_email='me@michaelhelmick.com',
    license='MIT License',
    url='https://github.com/michaelhelmick/python-flickr/',
    keywords='python flickr oauth api',
    description='A Python Library to interface with Flickr REST API, OAuth & JSON Responses',
    long_description=open('README.rst').read(),
    download_url="https://github.com/michaelhelmick/python-flickr/zipball/master",
    py_modules=["flickr"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet'
    ]
)
