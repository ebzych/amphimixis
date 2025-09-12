import os


class Project:
    def __init__(self, repo_path: str, builds_path: str = "build/"):
        self.path = repo_path
        self.builds_path = os.path.join(repo_path, builds_path)
        self.build_system = "cmake"
        self.targets = []
