import os
import detectlanguage

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'detectlanguage',
    packages = ['detectlanguage'],
    version = detectlanguage.__version__,
    description = 'Language Detection API Client',
    author = 'Laurynas Butkus',
    author_email = 'info@detectlanguage.com',
    url = 'https://github.com/detectlanguage/detectlanguage-python',
    download_url = 'https://github.com/detectlanguage/detectlanguage-python',
    keywords = ['language', 'identification', 'detection', 'api', 'client'],
    install_requires= ['requests>=1.2.0'],
    classifiers = [],
    license = 'MIT',
)
