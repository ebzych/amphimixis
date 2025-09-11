class Project:
    def __init__(self, repo_path: str, builds_path: str = "builds/"):
        self.path = repo_path
        self.builds_path = builds_path
        self.build_system = "cmake"
        self.targets = []
