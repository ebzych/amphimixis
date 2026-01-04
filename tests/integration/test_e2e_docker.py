"""Tests for the full launch of the application on a specific project"""

import subprocess
import time

import docker
import pytest


@pytest.mark.integration
def test_e2e_remote_machine_between_containers(clone_repo, _docker_compose):
    """This integration test checks whether the application can successfully build the project
    on the remote machine with using two containers"""

    docker_client = docker.from_env()

    client_container = docker_client.containers.get("build-client")
    server_container = docker_client.containers.get("build-server")

    check_env_is_ready_cmd = ["bash", "-c", "ls secret_ishtar"]

    while (
        client_container.exec_run(check_env_is_ready_cmd)[0]
        or server_container.exec_run(check_env_is_ready_cmd)[0]
    ):
        time.sleep(5)

    get_ip_cmd = [
        "docker",
        "inspect",
        "-f",
        "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
        "build-server",
    ]
    ip_build_server = subprocess.run(
        get_ip_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
    )

    ip_address = ip_build_server.stdout.decode().strip()

    add_ip_cmd = [
        "bash",
        "-c",
        f"sed '5s/.*/  address: {ip_address}/' "
        f"/workspace/input_remote.yml > /workspace/input.yml.tmp && "
        f"mv /workspace/input.yml.tmp /workspace/input.yml",
    ]
    exit_code = client_container.exec_run(add_ip_cmd)[0]
    assert exit_code == 0

    repo_path = clone_repo("https://github.com/jbeder/yaml-cpp.git")
    copy_cmd = ["docker", "cp", repo_path, "build-client:/workspace/yaml-cpp"]
    subprocess.run(copy_cmd, check=True)

    build_cmd = ["bash", "-c", "python3 /app/amixis.py /workspace/yaml-cpp"]
    exit_code = client_container.exec_run(build_cmd, workdir="/workspace")[0]

    assert exit_code == 0
