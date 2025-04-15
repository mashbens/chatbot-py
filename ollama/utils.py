def clean_prompt(prompt):
    return prompt.replace('\n', ' ').strip()

MAX_PROMPT_TOKENS = 2048  # Sesuaikan dengan batas model

def truncate_prompt(prompt: str) -> str:
    """Potong prompt jika terlalu panjang (asumsi 1 token ≈ 4 karakter)."""
    max_length = MAX_PROMPT_TOKENS * 4
    if len(prompt) > max_length:
        return prompt[:max_length]
    return prompt
