import click
import os
from kubernetes import client, config

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
        self.cleanup()
        # try:
        #     self.v1.create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=self.namespace)))
        # except:
        #     click.echo("ERROR: Couldn't create namespace. If you ran the tool recently, please wait a few moments and try again.", 
        #                err=True)
        #     os._exit(status=1)
    
    def create_secret(self, username, password):
        api_version = "v1"
        metadata = client.V1ObjectMeta(name=self.secret_name)
        type = "docker-registry"
        data = {"username": username, "password": password}
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
        # spec = client.V1PersistentVolumeSpec(
        #     capacity={"storage": "5Gi"}, 
        #     access_modes=["ReadWriteOnce"], 
        #     storage_class_name="local-storage",
        #     volume_mode="Filesystem",
        #     local={
        #         "path": path
        #     },
        #     node_affinity={
        #         "required": {
        #             "nodeSelectorTerms": [
        #                 {
        #                     "matchExpressions": [
        #                         {
        #                             "key": "kubernetes.io/hostname",
        #                             "operator": "In",
        #                             "values": ["minikube"]
        #                         }
        #                     ]
        #                 }
        #             ]
        #         }
        #     })

        spec = client.V1PersistentVolumeSpec(
            capacity={"storage": "5Gi"}, 
            access_modes=["ReadWriteOnce"], 
            storage_class_name="manual",
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
        # spec = client.V1PersistentVolumeClaimSpec( 
        #     access_modes=["ReadWriteOnce"],
        #     resources={"requests": {"storage": "5Gi"}},
        #     storage_class_name="local-storage")
        spec = client.V1PersistentVolumeClaimSpec( 
            access_modes=["ReadWriteOnce"],
            resources={"requests": {"storage": "5Gi"}},
            storage_class_name="manual")
        pvc_body = client.V1PersistentVolumeClaim(api_version=api_version, kind=kind, metadata=metadata, spec=spec)
        self.v1.create_namespaced_persistent_volume_claim(namespace=self.namespace, body=pvc_body)
        click.echo("Created a volume claim.")

    def create_pod(self, dockerfile_path, username_plain, image_name):
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
                        "mountPath": "/kaniko/.docker"
                    },
                    {
                        "name": self.volume_name,
                        "mountPath": "/workspace"
                    }
                ]

            }],
            restart_policy="Never",
            volumes=[
                {
                    "name": self.secret_name,
                    "secret": {
                        "secretName": self.secret_name
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
        


    def cleanup(self):
        # self.clear_namespace()
        self.v1.delete_namespaced_secret(self.secret_name, self.namespace)
        self.clear_volume_and_volume_claims()
        click.echo("Completed cleanup, safe to exit.")
    
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