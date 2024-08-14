import click
import base64
from os.path import isfile, abspath, normpath
from src.buildtool import BuildTool
import base64

@click.group()
def cli():
    pass

@click.command()
@click.option('--dockerfile', default="./Dockerfile", help="Path to the Dockerfile")
@click.option('--project', default=".", help="Path to the Project. Please make sure the Dockerfile is inside this.")
@click.option('--imagename', required="true", help="Name of the image that will be uploaded to Dockerhub.")
def deploy(dockerfile, project, imagename):
    project_path = abspath(project)
    dockerfile_path = abspath(dockerfile)
    print(project, project_path, normpath(project_path))
    click.echo(f"Project directory: {project_path}")

    if isfile(dockerfile):
        click.echo(f"Dockerfile is provided at path: {dockerfile_path}")
    else:
        click.echo(f"No file found at path: {dockerfile_path}")

    username = click.prompt("Please enter your Dockerhub username")
    username_encoded = base64.b64encode(username.encode()).decode()
    password = click.prompt("Please enter your Dockerhub password", hide_input=True)
    password_encoded = base64.b64encode(password.encode()).decode()
    buildtool = BuildTool(project_path=project_path, dockerfile_path=dockerfile_path)
    buildtool.submit_job(username=username_encoded, username_plain = username, password=password_encoded, image_name=imagename)

cli.add_command(deploy)

if __name__ == "__main__":
    # app()
    cli()