# LinkedIn Post Generator Agent

An AI agent built with [LangChain](https://www.langchain.com/) and Google Gemini that generates
professional, engaging LinkedIn posts from a **topic** and a **language**.

The agent uses an LLM chain (`prompt | llm | output_parser`) to produce a
structured 2–4 paragraph post with a strong hook, a clear takeaway, a call to
action, and relevant hashtags — all written in the language you choose
(English, Bengali, Spanish, and more).

## Features

- **Topic-driven** — give it any subject (e.g., "AI in Healthcare").
- **Multilingual** — writes the entire post in your selected language, including
  non-Latin scripts like Bengali or Arabic.
- **Structured output** — hook, 2–4 paragraphs, call to action, and hashtags.
- **Configurable** — optional tone and target audience; swap models or
  temperature via flags or environment variables.
- **Usable two ways** — interactive CLI prompts or one-shot command-line flags.

## Project structure

```
linkedin-post-generator-agent/
├── linkedin_agent/
│   ├── __init__.py      # exports LinkedInPostAgent, PostRequest
│   ├── agent.py         # the LangChain LCEL chain + agent class
│   └── prompts.py       # chat prompt templates
├── main.py              # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

1. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key**

   ```bash
   cp .env.example .env
   # then edit .env and set GOOGLE_API_KEY
   ```

   `.env` variables:

   | Variable          | Required | Default            | Description                     |
   | ----------------- | -------- | ------------------ | ------------------------------- |
   | `GOOGLE_API_KEY`  | yes      | —                  | Your Google Gemini API key      |
   | `GEMINI_MODEL`    | no       | `gemini-2.5-flash` | Chat model to use               |
   | `LLM_TEMPERATURE` | no       | `0.7`              | Sampling temperature (0.0–1.0)  |

## Usage

### Interactive

```bash
python main.py
```

You'll be prompted for the topic and language.

### One-shot with flags

```bash
python main.py --topic "AI in Healthcare" --language English
python main.py -t "Remote Work Productivity" -l Bengali --tone inspirational
python main.py -t "Cloud Cost Optimization" -l Spanish --audience "startup founders"
```

| Flag                 | Description                                      |
| -------------------- | ------------------------------------------------ |
| `-t`, `--topic`      | Topic of the post                                |
| `-l`, `--language`   | Language of the post (default: English)          |
| `--tone`             | Optional tone (e.g., inspirational, technical)   |
| `--audience`         | Optional target audience                         |
| `--model`            | Override the LLM model                           |
| `--temperature`      | Override the sampling temperature                |

## Use as a library

```python
from dotenv import load_dotenv
from linkedin_agent import LinkedInPostAgent

load_dotenv()

agent = LinkedInPostAgent()
post = agent.generate_post(
    topic="AI in Healthcare",
    language="English",
    tone="inspirational",
)
print(post)
```

## How it works

`linkedin_agent/agent.py` builds a LangChain Expression Language (LCEL) chain:

```
ChatPromptTemplate  →  ChatGoogleGenerativeAI (Gemini)  →  StrOutputParser
```

The system prompt instructs the model to act as a LinkedIn content strategist
and to write the full post in the requested language, while the human prompt
injects the topic, language, and optional tone/audience. The parsed string is
returned as the final post.

## Notes

- A Google Gemini API key is required; calls to the API may incur usage costs.
  Get one at https://aistudio.google.com/app/apikey.
- To use a different LLM provider, swap `ChatGoogleGenerativeAI` in `agent.py` for another
  LangChain chat model (e.g., `langchain-openai`, `langchain-anthropic`).
- Note: some models (e.g., `gemini-2.0-flash`) may have zero free-tier quota on a given
  key; `gemini-2.5-flash` is used by default. Override via `GEMINI_MODEL` or `--model`.
