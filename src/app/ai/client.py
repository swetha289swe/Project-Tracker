import json
import time

from google import genai
from google.genai.errors import ServerError

from app.core.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

SYSTEM_PROMPT = (
    "You extract structured task data from free text. "
    "Respond with ONLY a JSON object, no other text, no markdown fences. "
    'Shape: {"title": str, "priority": "low"|"medium"|"high"|"urgent", '
    '"due_date": "YYYY-MM-DD" or null}'
)


def parse_task_text(text: str, max_retries: int = 3) -> dict:
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=text,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "response_mime_type": "application/json",
                },
            )
            raw = response.text.strip()
            return json.loads(raw)

        except ServerError as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 1s, then 2s

    raise last_error

# import json

# from google import genai

# from app.core.config import settings

# client = genai.Client(api_key=settings.gemini_api_key)

# SYSTEM_PROMPT = (
#     "You extract structured task data from free text. "
#     "Respond with ONLY a JSON object, no other text, no markdown fences. "
#     'Shape: {"title": str, "priority": "low"|"medium"|"high"|"urgent", '
#     '"due_date": "YYYY-MM-DD" or null}'
# )


# def parse_task_text(text: str) -> dict:
#     response = client.models.generate_content(
#         model="gemini-flash-latest",
#         contents=text,
#         config={
#             "system_instruction": SYSTEM_PROMPT,
#             "response_mime_type": "application/json",
#         },
#     )

#     print("RAW GEMINI RESPONSE:", repr(response.text))  # TEMP debug

#     raw = response.text.strip()
#     return json.loads(raw)



{
  "project_id": "5c17b4ff-a3f9-43f3-8f56-cc1b7f19b9fa",
  "text": "Fix the login bug by Friday, high priority"
}

# # {
# #   "email": "abi@gmail.com",
# #   "password": "pass@123"
# # }

# {
#   "project_id": "5c17b4ff-a3f9-43f3-8f56-cc1b7f19b9fa",
#   "text": "Fix the login bug by Friday, high priority, assign to '1344f557-04b2-48db-86df-8586518621c9' and due date on 3 october 2026. Use following parameter for json title, assignee_id, due_date"
# }