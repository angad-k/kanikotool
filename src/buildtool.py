from src.kubeutil import KubeUtil
from os.path import relpath

class BuildTool:
    project_path: str
    dockerfile_path: str
    dockerfile_relpath: str
    def __init__(self, project_path:str, dockerfile_path: str):
        self.project_path = project_path
        self.dockerfile_path = dockerfile_path
        self.dockerfile_relpath = relpath(dockerfile_path, project_path)

    def submit_job(self):
        kube_util = KubeUtil()
        kube_util.create_volume(path=self.project_path)
        kube_util.create_volume_claim()
        kube_util.create_pod()
        kube_util.cleanup()
        pass