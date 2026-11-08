from pathlib import Path
OLLAMA_MODEL="gemma3:1b"
temperature=0.0
MAX_ATTEMPTS=3
DB_Path=(
    Path(__file__).resolve().parents[1]
    /"data"
    /"sales.db"
)

# Added for consistent results:
SEED=42          # same seed -> same output for the same prompt
NUM_CTX=8192     # Ollama's default context is 2048 tokens and silently cuts the start of longer prompts
MAX_ROWS=100     # max rows returned by a query
