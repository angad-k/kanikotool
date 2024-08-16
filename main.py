import click
import base64
from os.path import isfile, abspath, normpath
from src.buildtool import BuildTool
import base64

@click.group()
def cli():
    pass

@click.command()
@click.option('--project', default=".", help="Path to the Project. Please make sure the Dockerfile is at the root of the directory.")
@click.option('--imagename', required="true", help="Name of the image that will be uploaded to Dockerhub.")
def deploy(project, imagename):
    project_path = project
    
    click.echo(f"Proceeding with project directory: {project_path}")

    username = click.prompt("Please enter your Dockerhub username")
    password = click.prompt("Please enter your Dockerhub password", hide_input=True)
    auth_string = base64.b64encode((username + ":" + password).encode()).decode()

    buildtool = BuildTool(project_path=project_path)
    buildtool.submit_job(username_plain = username, auth_string=auth_string, image_name=imagename)

cli.add_command(deploy)

if __name__ == "__main__":
    # app()
    cli()