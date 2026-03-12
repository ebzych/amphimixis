"""LLM Agent Analyzer using GigaChat"""

import os
import re
from pathlib import Path

import yaml
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_gigachat.chat_models import GigaChat

LLM_ANALYSIS_FILE = "amphimixis_llm.analyzed"
MAX_MESSAGES = 50
MAX_FILES_IN_TREE = 300
MAX_ITERATIONS = 10


@tool
def directory_tree(proj_path: str) -> str:
    """
    Returns file tree in the project. Each line contains relative path to one file.
    Returns max 300 files to avoid token limits.

    Args:
        proj_path: Absolute path to the project directory
    """
    base = Path(proj_path)
    paths = [str(p.relative_to(base)) for p in base.rglob("*") if p.is_file()]
    return "\n".join(sorted(paths)[:MAX_FILES_IN_TREE])


@tool
def get_file_content(proj_path: str, relative_path: str) -> str:
    """
    Returns content from a text file at the given relative path.

    Args:
        proj_path: Absolute path to the project directory
        relative_path: Relative path to the file from project root
    """
    real_proj = os.path.realpath(proj_path)
    full_path = os.path.join(real_proj, relative_path)
    real_full = os.path.realpath(full_path)

    if not real_full.startswith(real_proj + os.sep):
        return "Error: path is outside project"

    if not os.path.isfile(full_path):
        return f"Error: File {relative_path} not found"

    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


TOOLS = [
    directory_tree,
    get_file_content,
]

SYSTEM_PROMPT = """You are a software repository analysis agent.

Analyze a project directory and identify:
- tests: paths to executable files of tests (relative to root directory)
- benchmarks: paths to executable files of benchmarks (relative to root directory)
- ci: continuous integration configuration files
- build_systems: ALL build systems used (cmake, meson, make, bazel, etc.)
- dependencies: third-party dependencies, CMakeLists.txt find_package dependencies

Many projects only have test/benchmark executables AFTER compilation. Find their FUTURE paths by examining:
- CMakeLists.txt (add_test, add_executable commands)
- CTestTestfile.cmake, CTestConfig.cmake
- meson.build (test function)
- Makefile (check for test: targets)
- CI configs (.github/workflows, .gitlab-ci.yml)
- etc.

For build systems, check for:
- CMakeLists.txt -> cmake
- *meson* -> meson
- Makefile, makefile -> make
- BUILD, WORKSPACE -> bazel
- configure.ac, configure.in -> autoconf
- etc.

Example output:
```yaml
tests:
  - project/test
benchmarks: []
ci:
  - .github/workflows/test.yml
build_systems:
  - first found build system
  - second found build system
dependencies: []
```

Process:
1. Use directory_tree to discover the project structure
2. Get information about project by presence of files and directories
3. Use get_file_content to examine build configs (CMakeLists.txt, meson.build, Makefile, etc.) and CI files
4. Analyze CMakeLists.txt, meson.build, CI configs, etc. for test/benchmark paths
5. Analyze all build system files to find what systems are used
6. Analyze third-party directory, CMakeLists.txt find_package, etc. to find dependencies
7. Put found information in YAML file format
8. Repeat until you have all information

IMPORTANT:
- You must use provided tools
- Never invent facts - only use information from tools
- Output ONLY valid YAML
- If not found, leave empty list
- For tests/benchmarks, show path to executable file relative to project root directory
- List ALL build systems found
"""

TOOLS_MAP = {
    "directory_tree": directory_tree,
    "get_file_content": get_file_content,
}


def create_model():
    """Create GigaChat model."""
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if not credentials:
        raise ValueError("GigaChat credentials environment variable not set")

    model = GigaChat(
        credentials=credentials,
        scope="GIGACHAT_API_PERS",
        model="GigaChat-2-pro",
        verify_ssl_certs=False,
        timeout=120,
        temperature=0.3,
    )
    return model


def analyze_with_agent(proj_path: str) -> bool:
    """Analyze project using GigaChat agent.

    Args:
        proj_path: Absolute path to the project directory

    Returns:
        True on success, False on failure
    """
    try:
        model = create_model()
    except ValueError as e:
        raise e

    model_with_tools = model.bind_tools(TOOLS)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Analyze project at: {proj_path}"),
    ]

    max_iterations = MAX_ITERATIONS
    for _ in range(max_iterations):
        result = model_with_tools.invoke(messages)
        messages.append(result)

        if len(messages) > MAX_MESSAGES:
            messages = messages[-MAX_MESSAGES:]

        if not isinstance(result, AIMessage):
            break

        tool_calls = result.tool_calls
        if not tool_calls:
            break

        for tc in tool_calls:
            try:
                args = tc.get("args", {})
                if isinstance(args, str):
                    args = yaml.safe_load(args) or {}
                tool_name = tc["name"]
                tool_func = TOOLS_MAP.get(tool_name)
                if tool_func:
                    tool_result = tool_func.invoke(args)
                    messages.append(
                        ToolMessage(content=tool_result, tool_call_id=tc["id"])
                    )
            except (TypeError, KeyError) as e:
                messages.append(
                    ToolMessage(content=str(e), tool_call_id=tc["id"], status="error")
                )

    last_message = messages[-1]
    content = last_message.content
    if isinstance(content, list):
        output_text = str(content)
    else:
        output_text = content if content else ""

    data = _parse_and_clean_output(output_text)

    if not data:
        return False

    with open(LLM_ANALYSIS_FILE, "w", encoding="utf8") as f:
        f.write(data)

    return True


def _parse_and_clean_output(text: str) -> str:
    """Extract and clean YAML from LLM output."""
    if not text:
        return ""

    yaml_match = re.search(r"```yaml\s*(.*?)\s*```", text, re.DOTALL)
    if yaml_match:
        text = yaml_match.group(1).strip()

    text = re.sub(r"^```yaml", "", text)
    text = re.sub(r"```$", "", text)
    text = text.strip()

    text = re.sub(r"^\s*#.*$", "", text, flags=re.MULTILINE)
    text = text.strip()

    return text
