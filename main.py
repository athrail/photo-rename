import typer

app = typer.Typer()

@app.command()
def say_hi(name: str):
    print(f'Hello {name}')

@app.command()
def say_bye(name: str):
    print(f'Bye {name}')

if __name__ == "__main__":
    app()