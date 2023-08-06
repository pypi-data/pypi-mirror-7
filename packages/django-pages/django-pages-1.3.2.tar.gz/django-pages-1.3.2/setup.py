# -*- encoding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-pages',
    version='1.3.2',
    author=u'Lukas Nemec',
    author_email='lu.nemec@gmail.com',
    url='https://github.com/lunemec/django-pages',
    license='see LICENCE.txt',
    description='Simple CMS for django',
    long_description='''https://github.com/lunemec/django-pages''',
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'django>=1.4',
        'pytz',
        'pillow',
        'django-grappelli',
        'django-filebrowser',
    ],
    packages=find_packages(),
)
