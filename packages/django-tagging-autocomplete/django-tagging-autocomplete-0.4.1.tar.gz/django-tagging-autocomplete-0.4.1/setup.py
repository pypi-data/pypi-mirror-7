# -*- coding: utf-8 -*-
from distutils.core import setup

long_description = open('README.rst').read()

setup(
    name='django-tagging-autocomplete',
    version='0.4.1',
    description='Autocompletion for django-tagging',
    long_description=long_description,
    author='Ludwik Trammer',
    author_email='ludwik@gmail.com',
    url='https://github.com/ludwiktrammer/django-tagging-autocomplete/',
    packages=['tagging_autocomplete'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    package_data={
        'tagging_autocomplete': [
            'static/tagging_autocomplete/js/*.js',
            'static/tagging_autocomplete/css/*.css',
            'static/tagging_autocomplete/css/base/*.css',
            'static/tagging_autocomplete/css/base/images/*.png',
        ],
        '': [
            'README.rst'
        ]
    },
)
