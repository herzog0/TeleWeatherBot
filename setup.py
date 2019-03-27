from setuptools import setup, find_packages

import conf

setup(
    name             = conf.name,
    version          = conf.release,
    description      = conf.description,
    long_description = conf.readme,
    long_description_content_type = "text/markdown",
    author           = conf.join_authors(conf.by_name),
    author_email     = conf.join_authors(conf.by_email),
    url              = conf.url,
    packages         = find_packages(exclude=('tests', 'docs')),
    python_requires  = "~=3.6",
    install_requires = [
        "telepot",
        "pyowm"
    ],
    classifiers      = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
