from openai import OpenAI
import os
import ast
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

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



def collect_code_files(owner, repo):

    branches_to_try = ["main", "master"]

    data = None

    for branch in branches_to_try:

        url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}/git/trees/"
            f"{branch}?recursive=1"
        )

        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json"
            },
            timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            break

    if not data:
        return []

    collected = []

    for item in data.get("tree", []):

        if item.get("type") != "blob":
            continue

        path = item.get("path", "")

        if path.endswith(ALLOWED_EXTENSIONS):
            collected.append(path)

    return collected

def fetch_file_contents(
    owner,
    repo,
    files
):

    combined_code = ""

    for file_path in files:

        try:

            github_url = (
                f"https://api.github.com/repos/"
                f"{owner}/{repo}/contents/{file_path}"
            )

            response = requests.get(
                github_url,
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}"
                },
                timeout=10
            )

            if response.status_code != 200:
                continue

            file_data = response.json()

            download_url = (
                file_data.get(
                    "download_url"
                )
            )

            if not download_url:
                continue

            raw_response = requests.get(
                download_url,
                timeout=10
            )

            combined_code += (
                f"\n\nFILE: {file_path}\n"
            )

            combined_code += (
                raw_response.text
            )

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
    
def review_repository_files(
    owner,
    repo,
    files
):

    results = []

    for file_path in files:

        try:

            code = fetch_file_contents(
                owner,
                repo,
                [file_path]
            )

            if not code.strip():
                continue

            extension = (
                file_path.split(".")[-1]
                .lower()
            )

            language_map = {
                "py": "python",
                "js": "javascript",
                "jsx": "javascript",
                "ts": "typescript",
                "tsx": "typescript",
                "java": "java",
                "cpp": "cpp",
                "c": "c",
                "cs": "csharp",
                "go": "go",
                "php": "php"
            }

            language = language_map.get(
                extension,
                "text"
            )

            review = review_repo_file(
                code,
                language
            )

            results.append({
                "file": file_path,
                "review": review
            })

        except Exception as e:

            results.append({
                "file": file_path,
                "error": str(e)
            })

    return results

def test_github_api(owner, repo):

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/contents"
    )

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}"
        }
    )

    return {
        "status_code": response.status_code,
        "items": len(response.json())
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
    
def review_repo_file(
    code,
    language
):

    prompt = f"""
You are an expert software engineer.

Review this file.

Provide ONLY:

SCORE:
BUGS:
IMPROVEMENTS:
OPTIMIZATIONS:
ADDITIONAL_NOTES:

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

        return response.choices[0].message.content

    except Exception as e:

        return str(e)
    
def summarize_repository_reviews(reviews):

    combined_reviews = ""

    for item in reviews:

        combined_reviews += (
            f"\nFILE: {item['file']}\n"
            f"{item['review']}\n"
        )

    prompt = f"""
You are a senior software architect.

Below are reviews generated for every file
in a GitHub repository.

{combined_reviews}

Generate:

OVERALL_SCORE:
(number between 0 and 100)

ARCHITECTURE:
- bullet points

SECURITY:
- bullet points

PERFORMANCE:
- bullet points

BEST_PARTS:
- bullet points

TOP_10_FIXES:
- bullet points
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

        return response.choices[0].message.content

    except Exception as e:

        return str(e)