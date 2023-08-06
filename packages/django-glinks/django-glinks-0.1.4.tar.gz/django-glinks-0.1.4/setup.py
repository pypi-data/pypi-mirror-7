from distutils.core import setup
import os

README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-glinks',
    version='0.1.4',
    author='Shawn Simon',
    author_email='shawn.simon.developer@gmail.com',
    packages=['glinks'],
    url='http://pypi.python.org/pypi/django-glinks/',
    license='LICENSE.txt',
    description='Interal add manager for django sites.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.6.0",
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)