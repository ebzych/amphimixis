class Analyzer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def analyze(self):
        print(f"Analyzing {self.repo_path}")
