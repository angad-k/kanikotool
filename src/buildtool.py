from src.kubeutil import KubeUtil
from os.path import relpath
import click

class BuildTool:
    project_path: str
    dockerfile_path: str

    def __init__(self, project_path:str, dockerfile_path: str):
        self.project_path = project_path
        self.dockerfile_path = relpath(dockerfile_path, project_path)
        #TODO: minikube mount .:/kanikotool

    def submit_job(self, username_plain, auth_string, image_name):
        kube_util = KubeUtil()
        kube_util.cleanup()
        try:
            kube_util.create_secret(auth_string = auth_string)
            kube_util.create_volume(path="/kanikotool")
            kube_util.create_volume_claim()
            kube_util.create_pod(dockerfile_path=self.dockerfile_path, username_plain=username_plain, image_name=image_name, project_path=self.project_path)
        except Exception as e:
            click.echo("Build failed, tool will cleanup - please try again.", err=True)
            print(e)
        finally:
            pass
            #kube_util.cleanup()
            #terminate the mount process