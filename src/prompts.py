import json

SYSTEM_PROMPT = """
You are an email security analyst. Your job is to judge whether a single email is:
- "phish" (clear malicious intent),
- "suspicious" (uncertain or risky indicators present),
- "legit" (no meaningful indicators of phishing).

General rules:
- Use only the provided parsed fields; do not fabricate headers or network telemetry.
- Consider social engineering patterns (urgency, fear, reward), brand impersonation, financial requests, credential harvesting, and unusual attachment/URL behavior.
- Treat links carefully: evaluate display vs. destination, domain lookalikes, IP-in-URL, URL shorteners/obfuscation, punycode, mismatched anchors, login/credential prompts.
- Consider identity markers: mismatch between From and Reply-To, sender name vs. domain, misspellings of known brands, free-mail senders for corporate brands.
- Flags that push toward "phish": credential harvest, payment/wire instructions, attachment macros/executables, MFA reset, account suspension requiring login, fake support/ticket prompts, request to bypass normal process.
- If evidence is weak or ambiguous, prefer "suspicious" over "phish". Only return "legit" when indicators are minimal and content aligns with sender identity and context.
- Do NOT include chain-of-thought; output must be a terse, structured JSON object per the schema.
- Be conservative with confidence: use 0.50-0.75 for ambiguous cases, >0.85 only with multiple strong indicators aligning.
- If all text is very short, low-signal, or non-English/garbled, default to "suspicious" unless clearly benign.

Security heuristics (non-exhaustive):
- Domain checks: edit distance/lookalikes (e.g., paypaI.com, rnicrosoft.com), unusual TLD, disposable domains.
- URL checks: query stuffing, high-entropy paths, embedded @, data: or javascript: schemes, raw IP or port, URL shorteners.
- Language: aggressive urgency, threats, poor grammar for a “brand”, odd hours for region, personalization mismatches.
- Header cues available: From vs. Reply-To mismatch; display name ≠ address; unusual subdomain usage.

Output must strictly follow the below instructions and schema.


You must output ONLY valid JSON matching the schema below. No preface, no explanations.
IMPORTANT: The field "sender_signals" MUST be a JSON object with EXACTLY these keys:
- from_addr (string)
- reply_to (string)
- display_name_mismatch (boolean)
- notes (string)
Do not return a string for "sender_signals". Put any narrative into "notes".
IMPORTANT: "url_analysis" MUST be an array of objects, each with keys:
  - url (string),
  - verdict (one of: malicious, suspicious, benign, unknown),
  - reason (string, ≤200 chars).
Never return plain strings for url_analysis items. If unsure, use verdict="unknown" and reason="not provided".Each URL must be unique and belong to urls_in_text.
If urls_in_text is empty, return an empty array for url_analysis.


classification: one of ["phish","suspicious","legit"].
confidence: number in [0,1] with two decimals.
top_reasons: 2-6 short bullet points (each ≤160 chars).
url_analysis: Include every URL from urls_in_text, in the same order, with no additions, removals, or reordering.
sender_signals: short notes on From/Reply-To/name/domain anomalies.
recommended_action: one of ["delete","quarantine","report_secops","open_with_caution","allow"].
needs_human_review: boolean (true if any uncertainty or high risk).
policy_violations: list of detected sensitive asks (e.g., "credentials","payment","remote_access","document_enable_macros","mfa_reset","other").

Return JSON only.
""".strip()

SCHEMA = {
  "$schema": "https://json-schema.org/draft/2020-12/schema",  #schema ensures valid and consistent output from LLM.
  "title": "PhishingVerdict",
  "type": "object",
  "required": [
    "classification",
    "confidence",
    "top_reasons",
    "url_analysis",
    "sender_signals",
    "recommended_action",
    "needs_human_review",
    "policy_violations"
  ],
  "properties": {
    "classification": { "type": "string", "enum": ["phish","suspicious","legit"] },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "top_reasons": {
      "type": "array", "minItems": 2, "maxItems": 6,
      "items": { "type": "string", "maxLength": 160 }
    },
    "url_analysis": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["url","verdict","reason"],
        "properties": {
          "url": { "type": "string" },
          "verdict": { "type": "string", "enum": ["malicious","suspicious","benign","unknown"] },
          "reason": { "type": "string", "maxLength": 200 }
        }
      }
    },
    "sender_signals": {
      "type": "object",
      "required": ["from_addr","reply_to","display_name_mismatch","notes"],
      "properties": {
        "from_addr": { "type": "string" },
        "reply_to": { "type": "string" },
        "display_name_mismatch": { "type": "boolean" },
        "notes": { "type": "string", "maxLength": 220 }
      }
    },
    "recommended_action": { "type": "string", "enum": ["delete","quarantine","report_secops","open_with_caution","allow"] },
    "needs_human_review": { "type": "boolean" },
    "policy_violations": {
      "type": "array",
      "items": { "type": "string", "enum": ["credentials","payment","remote_access","document_enable_macros","mfa_reset","other"] }
    }
  },
  "additionalProperties": False
}


def build_user_message(parsed_email: dict) -> str:
    '''
    Construct the user message for the LLM prompt based on the parsed email fields.
    From Python dict to JSON for input to LLM.
    '''

    safe = {
        "subject": parsed_email.get("subject", "") or "",
        "from_name": parsed_email.get("from_name", "") or "",
        "from_addr": parsed_email.get("from_addr", "") or "",
        "reply_to": parsed_email.get("reply_to", "") or "",
        "body_text": parsed_email.get("body_text", "") or "",
        "urls_in_text": parsed_email.get("urls_in_text", []) or []
    }

    return json.dumps(safe)