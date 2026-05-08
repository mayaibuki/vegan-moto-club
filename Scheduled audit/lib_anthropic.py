"""
Thin Anthropic SDK wrapper for the product audit pipeline.

Two narrow capabilities:
  1. write_description(...) - replaces the template-based stub with a Haiku-written
     4-6 sentence product description following the humanizer rules.
  2. adjudicate_vegan(...) - called only when keyword logic is ambiguous; returns
     one of the three canonical statuses with a one-line rationale.

Design notes:
  - Uses prompt caching (cache_control on the system prompt) so within a batch
    the system + humanizer rules become a ~10x cheaper cache hit.
  - Defaults to claude-haiku-4-5-20251001 - the cheapest model that still handles
    constrained writing reliably. Override with VMC_LLM_MODEL.
  - If ANTHROPIC_API_KEY is missing, both functions fall back to deterministic
    stubs so the script keeps working without the key (Layer 1 still ships).
"""

import os
import logging
from typing import Optional

log = logging.getLogger(__name__)

MODEL_ID = os.environ.get("VMC_LLM_MODEL", "claude-haiku-4-5-20251001")
API_KEY  = os.environ.get("ANTHROPIC_API_KEY")

_client = None
def _get_client():
    global _client
    if _client is not None:
        return _client
    if not API_KEY:
        return None
    try:
        from anthropic import Anthropic
        _client = Anthropic(api_key=API_KEY)
        return _client
    except ImportError:
        log.warning("anthropic SDK not installed; falling back to template descriptions")
        return None

DESCRIPTION_SYSTEM = """You write product descriptions for Vegan Moto Club, a curated database of vegan motorcycle gear.

Rules for every description:
- 4 to 6 sentences, plain prose. No bullet points, no headers, no internal notes.
- Tone: clear, useful, friendly, active voice. No hype, no over-selling.
- NO em dashes or double hyphens. Rewrite the sentence instead.
- NO emojis.
- NO AI vocabulary: seamlessly, elevate, delve, cutting-edge, robust, transformative, leverage, harness, tapestry, multifaceted, pivotal, nuanced, comprehensive, intricate, spearhead, paradigm, underscored, underpin.
- NO negative parallelisms ("not just X but Y", "not only X but also Y").
- NO rule-of-three lists repeated across sentences.
- NO conjunctive pile-ups (moreover, furthermore, additionally stacked together).
- Vary sentence rhythm: mix short and longer sentences.
- Be honest: include sizing quirks, limitations, or worth-knowing context where the source page mentions them.

Output ONLY the description text. No preamble, no quotes around it."""

VEGAN_SYSTEM = """You adjudicate the vegan status of a motorcycle product based on its page text.

Return exactly one of these three labels on the first line, then a one-line rationale on the second line:
  Confirmed Vegan by maker
  Verified Vegan by AI
  Waiting for confirmation as Vegan

Decision rules:
- "Confirmed Vegan by maker" only if the brand or page explicitly states the product is vegan, animal-free, or cruelty-free.
- "Verified Vegan by AI" if all listed materials read as synthetic and there is no animal material mentioned.
- "Waiting for confirmation as Vegan" if any animal material is mentioned (leather, suede, wool, down, fur, sheepskin, nubuck) OR materials are unclear.

Format:
<label>
<one-line rationale, no more than 20 words>"""


def _fallback_description(name, brand, category, price) -> str:
    """Used when no API key is available. Same shape as the old template stub."""
    cat  = (category or "motorcycle gear").lower()
    br   = brand or "the manufacturer"
    p    = f"${price:.0f}" if price else "prices vary"
    return (
        f"The {name} is a {cat} from {br} designed for riders who want "
        f"synthetic, animal-free construction. At {p}, it sits in a range "
        f"that should suit most budgets without forcing a major quality compromise. "
        f"The materials listed on the product page read as all-synthetic, which is "
        f"consistent with what we look for when adding gear to the site. "
        f"Check the sizing guide before ordering, since fit varies between brands "
        f"and a proper fit changes both comfort and protection."
    )


def write_description(
    name: str,
    brand: str,
    category: str,
    full_text: str,
    price: Optional[float],
    materials: Optional[list] = None,
) -> str:
    client = _get_client()
    if client is None:
        return _fallback_description(name, brand, category, price)

    excerpt = (full_text or "")[:2000]
    mats = ", ".join(materials) if materials else "(not parsed)"
    user_msg = (
        f"Product name: {name}\n"
        f"Brand: {brand or 'unknown'}\n"
        f"Category: {category or 'unknown'}\n"
        f"Price: {f'${price:.0f}' if price else 'unknown'}\n"
        f"Mapped materials: {mats}\n\n"
        f"Source page excerpt:\n{excerpt}\n\n"
        f"Write the description now."
    )
    try:
        resp = client.messages.create(
            model=MODEL_ID,
            max_tokens=400,
            system=[{
                "type": "text",
                "text": DESCRIPTION_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": user_msg}],
        )
        text = resp.content[0].text.strip()
        # Strip accidental quotes/em dashes the humanizer rules already forbid.
        text = text.replace("—", ",").replace("--", ",").strip('"').strip()
        return text
    except Exception as e:
        log.warning(f"Haiku description failed ({e}); using fallback for {name}")
        return _fallback_description(name, brand, category, price)


def adjudicate_vegan(full_text: str) -> tuple[str, str]:
    """
    Returns (label, rationale). Caller decides whether to call this -
    only invoke when keyword logic is ambiguous to keep cost down.
    """
    client = _get_client()
    if client is None:
        return ("Waiting for confirmation as Vegan", "no LLM available, defaulting to safer label")

    excerpt = (full_text or "")[:3000]
    try:
        resp = client.messages.create(
            model=MODEL_ID,
            max_tokens=120,
            system=[{
                "type": "text",
                "text": VEGAN_SYSTEM,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": f"Page text:\n{excerpt}"}],
        )
        out = resp.content[0].text.strip().splitlines()
        label = out[0].strip() if out else "Waiting for confirmation as Vegan"
        rationale = out[1].strip() if len(out) > 1 else ""
        valid = {
            "Confirmed Vegan by maker",
            "Verified Vegan by AI",
            "Waiting for confirmation as Vegan",
        }
        if label not in valid:
            label = "Waiting for confirmation as Vegan"
        return (label, rationale)
    except Exception as e:
        log.warning(f"Haiku vegan adjudication failed ({e}); defaulting")
        return ("Waiting for confirmation as Vegan", f"LLM error: {e}")
