from kubernetes import client, config

def init_client():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    return v1

def create_volume():
    pass

def create_volume_claim():
    pass

def create_pod():
    pass