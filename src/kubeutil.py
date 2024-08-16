import click
import os
from kubernetes import client, config
import base64

class KubeUtil:
    v1 : client.CoreV1Api
    volume_name: str = "kt-target-project-volume"
    volume_claim_name: str = "kt-target-project-volume-claim"
    # namespace: str = "kaniko-build-tool"
    namespace: str = "default"
    secret_name: str = "kaniko-build-tool-secret"
    pod_name: str = "kaniko"
    
    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()

    def get_pod_status(self):
        pod_list = self.v1.list_namespaced_pod(namespace=self.namespace).items
        for pod in pod_list:
            if(pod.metadata.name == self.pod_name):
                return pod.status.phase
        return None

    def get_logs(self):
        logs = self.v1.read_namespaced_pod_log(name = self.pod_name, namespace=self.namespace)
        click.echo("Logs: ")
        click.echo(logs)

    def create_secret(self, auth_string):
        api_version = "v1"
        metadata = client.V1ObjectMeta(name=self.secret_name)
        type = "generic"
        b64data = '{"auths": {"https://index.docker.io/v1/": {"auth": "'+ auth_string + '"}}}'
        b64data=base64.b64encode(b64data.encode()).decode()
        data = {'config.json': b64data}
        secret_body = client.V1Secret(
            api_version=api_version, 
            metadata=metadata, 
            type=type, 
            data=data)
        self.v1.create_namespaced_secret(namespace=self.namespace, body=secret_body)
        click.echo("Created a secret.")

    def create_volume(self, path: str):
        api_version = "v1"
        kind = "PersistentVolume"
        metadata = client.V1ObjectMeta(name=self.volume_name, labels={"type": "local"})

        spec = client.V1PersistentVolumeSpec(
            capacity={"storage": "5Gi"}, 
            access_modes=["ReadWriteOnce"], 
            storage_class_name="local-storage",
            host_path={
                "path": path
            })
        pv_body = client.V1PersistentVolume(api_version=api_version, kind=kind, metadata=metadata, spec=spec)
        self.v1.create_persistent_volume(body=pv_body)
        click.echo("Created a volume.")

    def create_volume_claim(self):
        api_version = "v1"
        kind = "PersistentVolumeClaim"
        metadata = client.V1ObjectMeta(name=self.volume_claim_name)
        spec = client.V1PersistentVolumeClaimSpec( 
            access_modes=["ReadWriteOnce"],
            resources={"requests": {"storage": "5Gi"}},
            storage_class_name="local-storage")
        pvc_body = client.V1PersistentVolumeClaim(api_version=api_version, kind=kind, metadata=metadata, spec=spec)
        self.v1.create_namespaced_persistent_volume_claim(namespace=self.namespace, body=pvc_body)
        click.echo("Created a volume claim.")

    def create_pod(self, username_plain, image_name):
        api_version = "v1"
        kind = "Pod"
        metadata = client.V1ObjectMeta(name=self.pod_name)
        spec = client.V1PodSpec(
            containers=[{
                "name": "kaniko",
                "image": "gcr.io/kaniko-project/executor:latest",
                "args": ["--dockerfile=/workspace/dockerfile", #TODO: dockerfile could be anywhere
                         "--context=dir://workspace", 
                         "--destination=" + username_plain + "/" + image_name],
                "volumeMounts": [
                    {
                        "name": self.secret_name,
                        "mountPath": "/kaniko/.docker/config.json",
                        "subPath": "config.json"
                    },
                    {
                        "name": self.volume_name,
                        "mountPath": "/workspace"
                    }
                ]
            }],
            security_context={"privileged": True},
            restart_policy="Never",
            volumes=[
                {
                    "name": self.secret_name,
                    "secret": {
                        "secretName": self.secret_name,
                        "items": [{
                             "key": "config.json",
                             "path": "config.json"
                        }]
                    }
                },
                {
                    "name": self.volume_name,
                    "persistentVolumeClaim":{"claimName": self.volume_claim_name}
                }
            ]
        )
        pod_body = client.V1Pod(api_version=api_version, 
                                kind=kind, 
                                metadata=metadata,
                                spec=spec)
        self.v1.create_namespaced_pod(namespace=self.namespace, body=pod_body)
        click.echo("Pod created")

    def cleanup(self):
        try:
            self.v1.delete_namespaced_secret(self.secret_name, self.namespace)
            click.echo("Deleted the created secret.")
        except:
            click.echo("No secrets deleted, proceeding.")
        
        try:
            self.v1.delete_namespaced_pod(self.pod_name, self.namespace)
            click.echo("Deleted the created pod.")
        except:
            click.echo("No pods deleted, proceeding.")

        try:
            self.v1.delete_namespaced_persistent_volume_claim(namespace=self.namespace, name=self.volume_claim_name)
            click.echo("Deleted the created volume claim.")
        except:
            click.echo("No volume claim deleted, proceeding.")

        try:
            self.v1.delete_persistent_volume(name=self.volume_name)
            click.echo("Deleted the created volume.")
        except:
            click.echo("No volume, proceeding.")

        click.echo("Completed cleanup, safe to exit.")                