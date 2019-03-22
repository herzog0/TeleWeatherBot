from setuptools import setup, find_packages

authors = [
    ('Tiago de Paula', 'tiagodepalves@gmail.com'),
]

with open('README.md') as f:
    readme = f.read()

setup(
    name             = 'vai_chover_bot',
    version          = '0.1.0',
    description      = 'Bot para o Telegram com funcionalidades especiais relacionadas ao clima local dx usuárix.',
    long_description = readme,
    author           = ', '.join(author[0] for author in authors),
    author_email     = ', '.join(author[1] for author in authors),
    url              = 'https://gitlab.com/teobmendes/vai_chover_bot',
    packages         = find_packages(exclude=('tests', 'docs', 'main'))
)
