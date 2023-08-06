from setuptools import setup

packages = [
    'classes',
]

setup(
    name = 'Highton',
    version = '1.1.1',
    license = 'Apache License 2.0',
    description = 'A Python library for Highrise',
    long_description = 'A beautiful Python - Highrise - API. Less is more.',
    url = 'https://github.com/seibert-media/Highton',
    author = 'Michael Bykovski',
    author_email = 'mbykovski@seibert-media.net',
    py_modules=['highton', 'custom_exceptions'],
    packages=packages,
    install_requires = ['requests', 'lxml'],
    keywords = 'bykof seibertmedia seibert media python api highrise highton',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)