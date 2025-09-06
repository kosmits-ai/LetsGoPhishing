#Define the final features of parsed email.

from pydantic import BaseModel #a class that defines how your data looks like and the validation requirements it needs to pass in order to be valid.
from typing import List

class ParsedEmail(BaseModel):
    subject: str = ""
    from_name: str = ""
    from_addr: str = ""
    reply_to: str = ""
    body_text: str = ""
    urls_in_text: List[str] = []