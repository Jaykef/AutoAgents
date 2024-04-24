from autoagents.provider.anthropic_api import Claude2 as Claude

DEFAULT_LLM = Claude()
CLAUDE_LLM = Claude()


async def ai_func(prompt):
    return await DEFAULT_LLM.aask(prompt)
