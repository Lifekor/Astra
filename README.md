# Astra

Astra is an experimental conversational companion powered by GPT models. The project
combines memory management, emotion analysis and dual model integration.

## Requirements
* Python 3.11+
* An OpenAI API key available in `.env` as `OPENAI_API_KEY`

## Running
1. Install dependencies (if any) and ensure the API key is set in `.env`.
2. Start the application:
   ```bash
   python astra_app.py
   ```
3. Interact with Astra in the console. Type `выход` to quit.

The directory `astra_data/` stores persistent files such as `astra_core_prompt.txt`
and emotional memories. Commands like `сохрани в core_prompt` allow updating the
core prompt, while Astra can autonomously append lines if `allow_core_update` is
enabled in `AstraMemory`.

## Maintenance
Run `scripts/cleanup_duplicates.py` to merge duplicate emotion records after updates.

## Token handling
`AstraChat.generate_response` uses `tiktoken` to approximate how many tokens will be sent to the API. If the existing context plus the `max_tokens` setting would exceed about 9500 tokens, the oldest messages in the relevant context are dropped until the request fits this limit. This prevents hitting the GPT-4o hard cap while still returning up to 2000 new tokens.
