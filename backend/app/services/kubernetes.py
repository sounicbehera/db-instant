from kubernetes import client, config


def load_kubernetes_client() -> client.CoreV1Api:
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    return client.CoreV1Api()


def get_cluster_nodes() -> list[str]:
    core_api = load_kubernetes_client()
    nodes = core_api.list_node()
    return [node.metadata.name for node in nodes.items]