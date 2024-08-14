from src.kubeutil import KubeUtil
from os.path import relpath

class BuildTool:
    project_path: str
    dockerfile_path: str

    def __init__(self, project_path:str, dockerfile_path: str):
        self.project_path = project_path
        self.dockerfile_path = relpath(dockerfile_path, project_path)

    def submit_job(self, username, username_plain, password, image_name):
        kube_util = KubeUtil()
        try:
            kube_util.create_secret(username=username, password=password)
            kube_util.create_volume(path=self.project_path)
            kube_util.create_volume_claim()
            kube_util.create_pod(dockerfile_path=self.dockerfile_path, username_plain=username_plain, image_name=image_name)
        finally:
            pass
            # kube_util.cleanup()