"""Categorize companies into FAANG+, Quant, or Other.

Mirrors the grouping used by popular new-grad job boards so the UI can offer
the same FAANG+ / Quant / Other tabs. Matching is done on a normalized
(lowercased, alphanumeric) company name and tolerant of common suffixes.
"""

import re

CATEGORY_FAANG = "FAANG+"
CATEGORY_QUANT = "Quant"
CATEGORY_OTHER = "Other"

# Big tech and other highly sought-after product companies.
_FAANG_PLUS = {
    "meta",
    "facebook",
    "apple",
    "amazon",
    "amazonweb services",
    "aws",
    "netflix",
    "google",
    "alphabet",
    "microsoft",
    "nvidia",
    "openai",
    "anthropic",
    "tesla",
    "tiktok",
    "bytedance",
    "uber",
    "lyft",
    "airbnb",
    "linkedin",
    "salesforce",
    "adobe",
    "oracle",
    "ibm",
    "intel",
    "qualcomm",
    "amd",
    "snap",
    "snapchat",
    "spotify",
    "pinterest",
    "reddit",
    "stripe",
    "databricks",
    "snowflake",
    "palantir",
    "doordash",
    "instacart",
    "robinhood",
    "coinbase",
    "dropbox",
    "twilio",
    "atlassian",
    "servicenow",
    "workday",
    "vmware",
    "cisco",
    "samsung",
    "bloomberg",
    "figma",
    "notion",
    "discord",
    "asana",
    "airtable",
    "samsara",
    "scale",
    "scaleai",
    "cloudflare",
    "gitlab",
    "github",
    "datadog",
    "plaid",
    "roblox",
    "block",
    "square",
    "paypal",
    "zoom",
    "ramp",
    "brex",
    "rippling",
    "anduril",
    "waymo",
    "rivian",
    "affirm",
    "unity",
    "cohere",
    "perplexity",
    "mistral",
    "huggingface",
}

# Quantitative trading / hedge funds / market makers.
_QUANT = {
    "jane street",
    "janestreet",
    "two sigma",
    "twosigma",
    "citadel",
    "citadel securities",
    "hudson river trading",
    "hrt",
    "jump trading",
    "de shaw",
    "deshaw",
    "d e shaw",
    "optiver",
    "imc",
    "imc trading",
    "drw",
    "five rings",
    "fiverings",
    "akuna capital",
    "akuna",
    "susquehanna",
    "sig",
    "tower research",
    "tower research capital",
    "virtu",
    "virtu financial",
    "millennium",
    "point72",
    "radix trading",
    "old mission",
    "flow traders",
    "qube",
    "qube research",
    "g research",
    "gresearch",
    "wintermute",
    "headlands",
    "cubist",
    "balyasny",
}

_NORMALIZE_RE = re.compile(r"[^a-z0-9 ]+")
_WS_RE = re.compile(r"\s+")
_SUFFIXES = (" inc", " llc", " ltd", " corp", " co", " technologies", " labs", " ai")


def _normalize(name: str) -> str:
    text = _NORMALIZE_RE.sub(" ", name.lower())
    text = _WS_RE.sub(" ", text).strip()
    for suffix in _SUFFIXES:
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()
    return text


def categorize_company(name: str | None) -> str:
    if not name:
        return CATEGORY_OTHER
    normalized = _normalize(name)
    if not normalized:
        return CATEGORY_OTHER

    collapsed = normalized.replace(" ", "")
    if normalized in _FAANG_PLUS or collapsed in _FAANG_PLUS:
        return CATEGORY_FAANG
    if normalized in _QUANT or collapsed in _QUANT:
        return CATEGORY_QUANT

    # Token-level fallback so "google llc" / "meta platforms" still match.
    tokens = set(normalized.split())
    if tokens & _FAANG_PLUS:
        return CATEGORY_FAANG
    return CATEGORY_OTHER
