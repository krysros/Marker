import json
import os

import google.genai as genai


def extract_fields_llm(html: str, api_key: str = None) -> dict:
    """
    Sends HTML to Gemini (Google Generative AI) and expects a JSON response with form fields (company or project).
    """
    if api_key is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")
    prompt = (
        "Extract the following form fields from the HTML below: "
        "name, street, postcode, city, subdivision, country, NIP, REGON, KRS. "
        "Return the result as JSON.\nHTML:\n" + html
    )
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
    except Exception as e:
        err = str(e)
        err_lower = err.lower()
        if "429" in err or "too many requests" in err_lower:
            raise RuntimeError(
                "Gemini API rate limit reached (HTTP 429 Too Many Requests). Please wait and try again. "
                "More info: https://ai.google.dev/gemini-api/docs/rate-limits"
            )
        if "resource_exhausted" in err_lower or "quota" in err_lower:
            raise RuntimeError(
                "Gemini API quota exceeded. Please check your plan, billing details, and rate limits. "
                "See: https://ai.google.dev/gemini-api/docs/rate-limits and https://ai.dev/rate-limit for more information.\n"
                f"Details: {e}"
            )
        if "not found" in err_lower or "404" in err:
            raise RuntimeError(
                "Requested Gemini model is not available or not supported by your API key. "
                "Check your model name or Google Gemini documentation for available models.\n"
                f"Details: {e}"
            )
        raise
    try:
        return json.loads(response.text)
    except Exception as e:
        raise RuntimeError(
            f"LLM response decode error: {e}\nResponse: {getattr(response, 'text', str(response))}"
        )
