import click
from os.path import isfile, abspath

@click.group()
def cli():
    pass

@click.command()
@click.option('--dockerfile', default="./Dockerfile", help='Path to the Dockerfile')
@click.option('--project', default=".", help='Path to the Dockerfile')
def deploy(dockerfile, project):
    ProjectPath = abspath(project)
    DockerfilePath = abspath(dockerfile)
    
    click.echo(f"Project directory: {ProjectPath}")

    if isfile(dockerfile):
        click.echo(f"Dockerfile is provided at path: {DockerfilePath}")
    else:
        click.echo(f"No file found at path: {DockerfilePath}")


cli.add_command(deploy)

if __name__ == "__main__":
    # app()
    cli()