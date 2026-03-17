import sys
from pathlib import Path


def read_md_docs_tool(filepath: Path, keywords: list[str]) -> list[str]:
    with open(filepath, "r", encoding="UTF-8") as f:
        previous_line: str = ""
        current_line: str
        is_reading_header = False
        header_context = []
        for current_line in f:  # searching a header
            if not is_reading_header:
                if "----" in current_line:
                    for keyword in keywords:
                        if keyword.lower() in previous_line.lower():
                            is_reading_header = True
                            header_context.append(previous_line)
                            header_context.append(current_line)
                            break
                i = 0
                while i < len(current_line) and current_line[i] == "#":
                    i += 1
                if 0 < i < len(current_line) - 1 and current_line[i] == " ":
                    for keyword in keywords:
                        if keyword.lower() in previous_line.lower():
                            is_reading_header = True
                            header_context.append(current_line)
                            break

                previous_line = current_line
            else:
                if "----" in current_line:
                    break
                i = 0
                while i < len(current_line) and current_line[i] == "#":
                    i += 1
                if 0 < i < len(current_line) - 1 and current_line[i] == " ":
                    is_reading_header = True
                    header_context.append(current_line)
                    break
                header_context.append(current_line)
                previous_line = current_line
        return header_context


if __name__ == "__main__":
    print("".join(read_md_docs_tool(sys.argv[1], sys.argv[2:])))
