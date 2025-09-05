import sys
from analyzer import Analyzer

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <repo_path>")
        sys.exit(1)
    analyzer = Analyzer(sys.argv[1])
    analyzer.analyze()
