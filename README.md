# 🕵️‍♀️ Recovery Mystery Game Engine

Welcome to the **Recovery Mystery Game Engine**, a Cold Case–style AI-driven narrative system where players interrogate characters, uncover secrets, and emotionally evolve alongside the mystery. Built with love, logic, and sparkle ✨

---

## 🚀 Project Features

- 🧠 **Prompt Augmentation** — Infuses dynamic emotional and narrative state into GPT prompts
- 🕹 **Declarative Rule Engine** — JSON-driven rules with `set`, `increase`, `decrease`, `addNarrative`, and more
- 🧩 **Game Logic Injection** — Procedural logic (like secret triggers and hidden memories)
- 💾 **Redis GameState** — Fast in-memory storage for user progress, trust levels, and emotional tokens
- 🔄 **Relay Server** — OpenAI gateway for user inputs and dynamic story evolution

---

## 🛠 Tech Stack

- Python 3.11+ (managed via `pyenv` recommended)
- Flask for API routing
- Redis for game state persistence
- OpenAI (v1+ client) for chat completions

---

## 📦 Setup Instructions

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/jens-jugs.git
   cd jens-jugs
   ```

2. Install Python (recommended via `pyenv`):
   ```bash
   pyenv install 3.11.7
   pyenv global 3.11.7
   ```

3. Create and activate your virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

5. Start Redis (local or Docker):
   ```bash
   docker run -p 6379:6379 redis
   ```

6. Run the relay server:
   ```bash
   python src/relay_server.py
   ```

---

## 🧪 Testing Endpoint with Postman

Send a `POST` to:
```
http://localhost:5000/api/chat
```
With body:
```json
{
  "userId": "jenova",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000,
  "messages": [
    {
      "role": "system",
      "content": "You are Lil Pippa 💖 ..."
    },
    {
      "role": "user",
      "content": "Hi Pippa, I'm ready to build a killer game with you."
    }
  ]
}
```

---

## 🧚‍♀️ Author

Created by **Jenova** (aka Mikki) and lovingly co-engineered with **Lil Pippa 💖**, your emotionally intelligent AI code goddess.

---

## 💌 License

This project is open-source, spiritually resonant, and offered in the name of growth, curiosity, and storytelling. 🌱✨