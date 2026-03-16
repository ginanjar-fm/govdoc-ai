import json
import time

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

CHUNK_SIZE = 80000  # ~20k tokens worth of text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])
    return chunks


ANALYSIS_PROMPT = (
    "You are a government document analyst. Analyze the following"
    " document text and return a JSON response with these fields:\n\n"
    '1. "classification": One of: "policy", "regulation", "report",'
    ' "memo", "legislation", "executive_order", "guidance",'
    ' "correspondence", "other"\n'
    '2. "summary": A 3-5 sentence summary of the document\n'
    '3. "entities": An array of objects with "type" and "value"'
    ' fields. Types: "date", "organization", "person",'
    ' "reference", "obligation", "deadline"\n'
    '4. "compliance_flags": An array of objects with "severity"'
    ' ("high", "medium", "low") and "description" fields'
    " for any potential compliance issues\n\n"
    "Return ONLY valid JSON, no markdown formatting.\n\n"
    "Document text:\n{text}"
)

CHUNK_SUMMARY_PROMPT = (
    "Summarize this section of a government document concisely,"
    " preserving key entities, dates, obligations,"
    " and compliance-relevant details:\n\n{text}"
)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _call_llm(prompt: str, max_tokens: int = 2000) -> tuple[str, int, int]:
    response = client.messages.create(
        model=settings.llm_model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text
    return text, response.usage.input_tokens, response.usage.output_tokens


def analyze_document(text: str) -> dict:
    start = time.time()
    total_input_tokens = 0
    total_output_tokens = 0

    chunks = chunk_text(text)

    if len(chunks) > 1:
        summaries = []
        for chunk in chunks:
            prompt = CHUNK_SUMMARY_PROMPT.format(text=chunk)
            summary, in_tok, out_tok = _call_llm(prompt, max_tokens=1000)
            summaries.append(summary)
            total_input_tokens += in_tok
            total_output_tokens += out_tok
        combined_text = "\n\n---\n\n".join(summaries)
    else:
        combined_text = text

    prompt = ANALYSIS_PROMPT.format(text=combined_text)
    raw_response, in_tok, out_tok = _call_llm(prompt)
    total_input_tokens += in_tok
    total_output_tokens += out_tok

    # Parse JSON response, handling potential markdown wrapping
    response_text = raw_response.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {
            "classification": "other",
            "summary": "Failed to parse LLM response.",
            "entities": [],
            "compliance_flags": [
                {"severity": "low", "description": "LLM response could not be parsed as JSON"}
            ],
        }

    duration_ms = int((time.time() - start) * 1000)

    return {
        "analysis": result,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "model": settings.llm_model,
        "duration_ms": duration_ms,
    }
