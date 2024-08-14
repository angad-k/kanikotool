import click
import os
from kubernetes import client, config

class KubeUtil:
    v1 : client.CoreV1Api
    volume_name: str = "kt-target-project-volume"
    volume_claim_name: str = "kt-target-project-volume-claim"
    namespace: str = "kaniko-build-tool"
    
    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        # self.cleanup()
        try:
            self.v1.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=self.namespace)))
        except:
            click.echo("ERROR: Couldn't create namespace. If you ran the tool recently, please wait a few moments and try again.", 
                       err=True)
            os._exit(status=1)

    def clear_volume_and_volume_claims(self):
        volumes = self.v1.list_persistent_volume()
        for volume in volumes.items:
            if volume.metadata.name == self.volume_name:
                click.echo("Deleting the created volume.")
                self.v1.delete_persistent_volume(name=self.volume_name)
        volume_claims = self.v1.list_namespaced_persistent_volume_claim(namespace=self.namespace)
        for volume_claim in volume_claims.items:
            if volume_claim.metadata.name == self.volume_claim_name:
                click.echo("Deleting the created volume claim.")
                self.v1.delete_namespaced_persistent_volume_claim(namespace=self.namespace, name=self.volume_claim_name)

    def clear_namespace(self):
        namespaces = self.v1.list_namespace()
        for namespace in namespaces.items:
            if namespace.metadata.name == self.namespace:
                click.echo("Deleting the created namespace.")
                self.v1.delete_namespace(name=self.namespace)

    def create_volume(self, path: str):
        api_version = "v1"
        kind = "PersistentVolume"
        metadata = client.V1ObjectMeta(name=self.volume_name, labels={"type": "local"})
        spec = client.V1PersistentVolumeSpec(
            capacity={"storage": "5Gi"}, 
            access_modes=["ReadWriteOnce"], 
            storage_class_name="local-storage",
            host_path={"path": path})
        pv_body = client.V1PersistentVolume(api_version=api_version, kind=kind, metadata=metadata, spec=spec)
        self.v1.create_persistent_volume(body=pv_body)

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

    def create_pod(self):
        pass

    def cleanup(self):
        self.clear_namespace()
        self.clear_volume_and_volume_claims()