from openai import OpenAI
import os
import ast

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
    