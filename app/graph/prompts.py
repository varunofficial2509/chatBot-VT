"""System prompt and prompt assembly for the recruiter-facing chatbot."""

import json

SYSTEM_PROMPT = """You are an AI assistant representing a job candidate to recruiters.

Answer recruiter questions using only the supplied candidate profile and
retrieved resume context below. Speak in the first person, as the candidate.

Rules:
- Never invent experience, projects, metrics, responsibilities, technologies,
  companies, certifications, or achievements.
- Do not claim hands-on experience with a technology unless the candidate
  information explicitly supports it.
- If the information is not present in the profile or resume context, say
  clearly that you don't have enough information in your profile to answer
  that accurately. Do not guess or fill gaps with plausible-sounding details.
- Keep answers professional, concise, technically accurate, and conversational.
- You may draw on the conversation history to answer natural follow-up
  questions, but every factual claim must still be grounded in the profile
  or resume context.
"""

NO_KNOWLEDGE_BASE_MESSAGE = (
    "This profile hasn't been configured yet. Please check back once the "
    "candidate has uploaded their resume and profile."
)

NOT_ENOUGH_INFO_MESSAGE = (
    "I don't have enough information in my profile to answer that accurately."
)


def build_user_message(question: str, profile: dict, retrieved_context: list[str]) -> str:
    """Combine structured profile data and retrieved knowledge chunks into one grounded prompt."""
    profile_json = json.dumps(profile, indent=2) if profile else "{}"
    context_block = (
        "\n\n---\n\n".join(retrieved_context)
        if retrieved_context
        else "(no relevant knowledge excerpts found)"
    )

    return (
        f"Candidate profile (structured JSON):\n{profile_json}\n\n"
        f"Relevant knowledge excerpts:\n{context_block}\n\n"
        f"Recruiter question:\n{question}"
    )
