from bs4 import BeautifulSoup
import re
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from .models import ParsedEmail

URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>()\"']+", re.IGNORECASE) #find urls in text starting with http(s) or www. Exclude unusual chars.



def _html_to_text(html: str) -> str:        #function for converting html to txt with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+"," ", text).strip()

def _get_preferred_body(msg) -> str:            #email can be multiparted or not.Based on this, we extract the body for each case.
    if msg.is_multipart():
        plain, html = None, None
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                try: plain = part.get_content()
                except: pass
            elif ctype == "text/html":
                try: html = part.get_content()
                except: pass
        if plain:
            return re.sub(r"\s+", " ", plain).strip()
        if html:
            return _html_to_text(html)
        return ""
    else:
        payload = msg.get_content()
        if msg.get_content_type() == "text/html":
            return _html_to_text(payload)
        return re.sub(r"\s+", " ", payload).strip() if isinstance(payload, str) else ""
            

def parse_email_bytes(raw_bytes: bytes) -> ParsedEmail:
    msg = BytesParser(policy=policy.default).parsebytes(raw_bytes) #takes raw .eml bytes and parses it into an EmailMessage

    subject = msg.get("subject", "") or ""
    from_name, from_addr = parseaddr(msg.get("from", "") or "")
    reply_to = parseaddr(msg.get("To", "") or "")[1]
    body_text = _get_preferred_body(msg)
    urls_in_text = URL_RE.findall(body_text)

    return ParsedEmail(
        subject = subject[:300],
        from_name = (from_name or "")[:100],
        from_addr = (from_addr or "").lower(),
        reply_to = (reply_to or "").lower(),
        body_text = body_text[:10000],
        urls_in_text = urls_in_text[:50]
    )