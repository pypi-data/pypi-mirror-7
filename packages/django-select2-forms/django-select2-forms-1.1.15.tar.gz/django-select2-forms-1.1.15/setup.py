#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup_kwargs = {}

try:
    setup_kwargs['long_description'] = open('README.rst').read()
except IOError:
    # Use the create_readme_rst command to convert README to reStructuredText
    pass

setup(
    name='django-select2-forms',
    version=__import__('select2').__version__,
    description='Django form fields using the Select2 jQuery plugin',
    author='Frankie Dintino',
    author_email='fdintino@theatlantic.com',
    url='https://github.com/theatlantic/django-select2-forms',
    packages=find_packages(),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'distutils.commands': [
            'create_readme_rst = select2.build:create_readme_rst',
        ],
    },
    **setup_kwargs)
