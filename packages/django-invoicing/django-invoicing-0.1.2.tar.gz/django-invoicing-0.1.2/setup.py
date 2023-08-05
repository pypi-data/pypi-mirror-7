#!/usr/bin/env python
from setuptools import setup


setup(
    name='django-invoicing',
    version='0.1.2',
    description='Django app for invoicing.',
    long_description=open('README.rst').read(),
    author='Pragmatic Mates',
    author_email='info@pragmaticmates.com',
    maintainer='Pragmatic Mates',
    maintainer_email='info@pragmaticmates.com',
    url='https://github.com/PragmaticMates/django-invoicing',
    packages=[
        'invoicing',
    ],
    include_package_data=True,
    install_requires=('django',),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 3 - Alpha'
    ],
    license='GPL License',
    keywords = "django invoice invoicing billing issuer buyer commerce products taxes pdf",
)
