from openai import OpenAI
import os
import ast
import requests

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
def parse_review(response_text):

    sections = {
        "score": 0,
        "bugs": "",
        "improvements": "",
        "optimizations": "",
        "improved_code": "",
        "notes": ""
    }

    current_section = None

    for line in response_text.splitlines():

        line = line.rstrip()

        if line.startswith("SCORE:"):

            try:
                sections["score"] = int(
                    line.replace("SCORE:", "").strip()
                )

            except:
                sections["score"] = 0

            continue

        if line.startswith("BUGS:"):
            current_section = "bugs"
            continue

        elif line.startswith("IMPROVEMENTS:"):
            current_section = "improvements"
            continue

        elif line.startswith("OPTIMIZATIONS:"):
            current_section = "optimizations"
            continue

        elif line.startswith("IMPROVED_CODE:"):
            current_section = "improved_code"
            continue

        elif line.startswith("ADDITIONAL_NOTES:"):
            current_section = "notes"
            continue

        if current_section:
            sections[current_section] += line + "\n"

    return sections

def check_syntax(code, language):

    if language != "python":
        return []

    try:
        ast.parse(code)

        return []

    except SyntaxError as e:

        return [
            {
                "line": e.lineno,
                "message": e.msg
            }
        ]


ALLOWED_EXTENSIONS = (
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".cs",
    ".go",
    ".php"
)

SKIP_FOLDERS = {
    "node_modules",
    "dist",
    "build",
    ".git",
    "coverage"
}

def get_repo_info(repo_url):

    parts = repo_url.rstrip("/").split("/")

    owner = parts[-2]
    repo = parts[-1]

    return owner, repo

def collect_code_files(
    owner,
    repo,
    path="",
    collected=None
):

    if collected is None:
        collected = []

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/contents/{path}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return collected

    items = response.json()

    for item in items:

        if len(collected) >= 30:
            return collected

        if item["type"] == "dir":

            if item["name"] in SKIP_FOLDERS:
                continue

            collect_code_files(
                owner,
                repo,
                item["path"],
                collected
            )

        elif item["type"] == "file":

            filename = item["name"].lower()

            if filename.endswith(
                ALLOWED_EXTENSIONS
            ):

                collected.append(
                    item["path"]
                )

    return collected

def fetch_file_contents(
    owner,
    repo,
    files
):

    combined_code = ""

    for file_path in files:

        url = (
            f"https://raw.githubusercontent.com/"
            f"{owner}/{repo}/main/{file_path}"
        )

        try:

            response = requests.get(
                url,
                timeout=10
            )

            if response.status_code == 200:

                combined_code += (
                    f"\n\nFILE: {file_path}\n"
                )

                combined_code += response.text

        except:
            continue

    return combined_code

def review_repository(repo_code):

    prompt = f"""
Review this GitHub repository strictly.

Scoring Guide:

0-30 = Unusable / severe bugs
31-50 = Poor quality
51-70 = Average
71-85 = Good
86-95 = Very good
96-100 = Production quality

Use the full range.

Repository Code:

{repo_code}

Provide:

Score:
Bugs:
Improvements:
Optimizations:
Additional Notes:
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return {
            "raw_response":
            response.choices[0].message.content
        }

    except Exception as e:

        return {
            "error": str(e)
        }

def review_code(
        code,
        language
    ):

    prompt = f"""
    You are an expert senior software engineer.

    Review the following code strictly.

    Scoring Guide:

    0-30 = Unusable / severe bugs
    31-50 = Poor quality
    51-70 = Average
    71-85 = Good
    86-95 = Very good
    96-100 = Production quality

    Use the full range of scores.

    Give your response in this exact format:

    SCORE: <number between 0 and 100>

    BUGS:
    - bullet points only

    IMPROVEMENTS:
    - bullet points only

    OPTIMIZATIONS:
    - bullet points only

    IMPROVED_CODE:
    <only code here, no markdown, no backticks>

    ADDITIONAL_NOTES:
    - bullet points only

    Keep the response clean and professional.
    Do NOT use markdown.
    Do NOT use ###.
    Do NOT use ```.

    Programming Language:
    {language}

    Code:
    {code}
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        parsed = parse_review(
            response.choices[0].message.content
        )   

        return {
            "review": parsed,
            "syntax_errors": check_syntax(
                code,
                language
            )
        }

    except Exception as e:
        return f"AI service temporarily unavailable: {str(e)}"
    