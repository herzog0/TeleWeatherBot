import os


def _read_file(name: str) -> str:
    directory = os.path.dirname(__file__)
    filepath = os.path.join(directory, name)
    with open(filepath, 'r') as file:
        return file.read()


class Author:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    def __repr__(self):
        return f'Author({repr(self.name)}, {repr(self.email)})'


name = "vai_chover_bot"
project = "WeatherBot"

version = "0.1"
release = "0.1.5"

description = "Bot para o Telegram com funcionalidades especiais relacionadas ao clima local dx usuárix."
url = "https://gitlab.com/teobmendes/vai_chover_bot"

authors = [
    Author("João Hergert", "joaohergert@gmail.com"),
    Author("João Paulo Penalber", "joao.p.penalber@gmail.com"),
    Author("Pedro Barros Bastos", "pedro.bbastos123@gmail.com"),
    Author("Teodoro Bertolozzi", "teobmendes@gmail.com"),
    Author("Tiago de Paula", "tiagodepalves@gmail.com")
]

by_name = lambda author: f'{author.name}'
by_email = lambda author: f'{author.name}'
by_first_name = lambda author: f'{author.name.split()[0]}'
by_last_name = lambda author: f'{author.name.split()[-1]}'
by_both = lambda author: f'{author.name} ({author.email})'

def join_authors(func=by_both, sep=', '):
    return sep.join(func(author) for author in authors)

readme = _read_file("README.md")
license = None
copyright = ""
