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

        if line.startswith("TOTAL_SCORE:"):

            try:

                score_text = (
                    line.replace(
                        "TOTAL_SCORE:",
                        ""
                    )
                    .replace(
                        "/100",
                        ""
                    )
                    .strip()
                )

                sections["score"] = int(score_text)

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

    Score the code using EXACTLY these categories:

    CORRECTNESS (0-20)

    * Logic correctness
    * Bug likelihood
    * Edge case handling

    READABILITY (0-20)

    * Naming quality
    * Code clarity
    * Maintainability

    PERFORMANCE (0-20)

    * Efficiency
    * Memory usage
    * Scalability

    SECURITY (0-20)

    * Input validation
    * Sensitive data handling
    * Security risks

    BEST PRACTICES (0-20)

    * Language conventions
    * Design quality
    * Code organization

    TOTAL_SCORE:
    (sum of all categories, 0-100)

    Scoring Rules:

    0-20 = Very Poor
    21-40 = Poor
    41-60 = Average
    61-80 = Good
    81-90 = Very Good
    91-100 = Production Quality

    When generating IMPROVED_CODE:

    * Fix every bug you identify.
    * Apply all reasonable improvements.
    * Apply all reasonable optimizations.
    * Follow modern best practices.
    * Generate code that would score at least 95/100 under this rubric.
    * Do not leave known issues unfixed.

    Give your response in this EXACT format:

    CORRECTNESS: <score>/20
    READABILITY: <score>/20
    PERFORMANCE: <score>/20
    SECURITY: <score>/20
    BEST_PRACTICES: <score>/20

    TOTAL_SCORE: <score>/100

    BUGS:

    * bullet points only

    IMPROVEMENTS:

    * bullet points only

    OPTIMIZATIONS:

    * bullet points only

    IMPROVED_CODE:
    <only code here, no markdown, no backticks>

    ADDITIONAL_NOTES:

    * bullet points only

    Keep the response clean and professional.
    Do NOT use markdown.
    Do NOT use ###
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
    
