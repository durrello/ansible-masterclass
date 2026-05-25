#!/usr/bin/env python3
import json
import subprocess

def get_docker_containers():
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}} {{.Ports}}"],
        capture_output=True, text=True
    )
    containers = {}
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        name, ports = line.split(" ", 1)
        ssh_port = None
        for part in ports.split(","):
            if "->22/tcp" in part:
                ssh_port = part.split(":")[1].split("->")[0]
                break
        if ssh_port:
            containers[name] = {
                "ansible_host": "127.0.0.1",
                "ansible_port": ssh_port,
                "ansible_user": "devuser",
                "ansible_ssh_private_key_file": "~/.ssh/id_rsa"
            }
    return containers

if __name__ == "__main__":
    inventory = {
        "all": {
            "hosts": list(get_docker_containers().keys()),
            "_meta": {"hostvars": get_docker_containers()}
        }
    }
    print(json.dumps(inventory, indent=2))
