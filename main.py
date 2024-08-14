import click
from os.path import isfile, abspath
from src.buildtool import BuildTool

@click.group()
def cli():
    pass

@click.command()
@click.option('--dockerfile', default="./Dockerfile", help='Path to the Dockerfile')
@click.option('--project', default=".", help='Path to the Project. Please make sure the Dockerfile is inside this.')
def deploy(dockerfile, project):
    project_path = abspath(project)
    dockerfile_path = abspath(dockerfile)
    
    click.echo(f"Project directory: {project_path}")

    if isfile(dockerfile):
        click.echo(f"Dockerfile is provided at path: {dockerfile_path}")
    else:
        click.echo(f"No file found at path: {dockerfile_path}")

    buildtool = BuildTool(project_path=project_path, dockerfile_path=dockerfile_path)
    buildtool.submit_job()


cli.add_command(deploy)

if __name__ == "__main__":
    # app()
    cli()