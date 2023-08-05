# -*- coding: utf-8 -*-

import os

from setuptools import find_packages
from setuptools import setup

version = '2.0a2'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'deform', 'tests', 'test_deform.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.deform',
    version=version,
    description="Fanstatic packaging of deform",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Andreas Kaiser',
    author_email='disko@binary-punks.com',
    url='https://github.com/Kotti/js.deform',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=[],
    install_requires=[
        'deform>=2.0a',
        'fanstatic',
        'js.jquery',
        'js.jquery_form',
        'js.jquery_maskedinput',
        'js.jquery_maskmoney',
        'js.jquery_sortable',
        'js.jquery_timepicker_addon',
        'js.jqueryui',
        'js.modernizr',
        'js.tinymce',
        'js.typeahead',
        'setuptools',
    ],
    entry_points={
        'fanstatic.libraries': [
            'deform = js.deform:library',
        ],
    },
)
