# SpongeBob CLI Chatbot (ai.sooners.us · gemma3:4b)

A tiny command-line chatbot that **talks like SpongeBob** and **keeps multi-turn history**.  
Uses the OpenAI-compatible **Chat Completions API** at `https://ai.sooners.us` with model `gemma3:4b`. Please reg an account first!

## Learning outcomes
- Call an OpenAI-compatible `/api/chat/completions` endpoint
- Keep and send multi-turn chat history (system + prior turns)
- Load secrets via a `.env` file (`~/.soonerai.env`)
- Package in a reproducible Git repo with clear docs

---

## 1) Account & API key (ai.sooners.us)
1. Go to `https://ai.sooners.us`
2. Sign up with your OU email
3. After login: **Settings → Account → API Keys**
4. Create a new API key and copy it

---

## 2) Create local env file

Create `~/.soonerai.env` with:

SOONERAI_API_KEY=your_key_here
SOONERAI_BASE_URL=https://ai.sooners.us
SOONERAI_MODEL=gemma3:4b


> **Do NOT commit this file.** `.gitignore` already excludes env files.

---

## 3) If you are using Anaconda like me

```bash
# Create and activate a clean env (Python 3.11+ recommended)
conda create -n spongebob-bot python=3.11 -y
conda activate spongebob-bot

# Get the code (either git clone your repo or copy files in)
# Example:
# git clone https://github.com/<you>/spongebob-cli.git
# cd spongebob-cli

# Install deps via pip (inside the conda env)
pip install -r requirements.txt