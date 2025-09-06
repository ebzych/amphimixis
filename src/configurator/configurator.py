from non_amphimixis import non_amphimixis
import json


def configure(project: non_amphimixis.Project):
    args = []
    while True:
        arg = input("Enter arg\n")
        if arg == "":
            break

        args.append(arg)
    config = {
        "args": str(args),
        "project_path": project.path,
        "build_path": project.builds_path,
    }
    with open("config.json", "w") as file:
        json.dump(config, file)
