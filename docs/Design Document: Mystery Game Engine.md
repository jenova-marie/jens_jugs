# 💠 Design Document: Mystery Game Engine

---

## 🌐 Core Architectural Decisions

### Language & Frameworks
- All code written in **TypeScript (latest)** (Note: Some Python modules are used for AI integration.)
- Node.js with Express for API relay
- Redis for session and game state management
- OpenAI (GPT-4) for narrative generation and conversation logic
- PlantUML for visual architecture & logic flow diagrams

### Modularity
- Game logic separated from API logic
- Prompt Augmentation module injects game state into prompts
- Declarative Rules Engine evaluates JSON-based conditions and actions
- System designed for scalability and multi-user sessions

### State Handling
- Redis used for dynamic per-user game state
- Each user tracked via a unique `userId`
- gameState includes inventory, clues, visited suspects, trust levels, and narrative flags

---

## 🛠️ Features (Present & Future)

### ✅ Completed
- Relay server with OpenAI integration
- Redis-backed gameState module
- Prompt Augmentation
- JSON-based Rule Schema
- Rule Evaluation Engine
- Token usage tracking (not yet wired)
- Markdown-based mysteries for Beginner and Advanced
- PlantUML diagrams for architecture and game logic flow

### 🔜 Upcoming
- Authentication system (JWT or session-based)
- Visual Rule Editor with schema validation
- Dynamic rule versioning and live reload
- In-game time tracking with consequences (48-hour countdown, second murder)
- Multiplayer "Cold Case Network" mode
- Player inventory and interactive clue management
- Reporting system for legal or therapeutic use
- AI-driven NPC behavior for adaptive interactions
- Lore collectibles tied to player progress

### 💡 Ideas
- Spiritual archetypes for each suspect
- Mystery Sky crossover integration
- Async journal entries from players as narrative inputs
- In-app AI journaling and reflection partner
- Procedural mystery generation for endless replayability
- Scoring system for mysteries based on solvability, emotional engagement, and replayability

---

## 🧠 Notes to Future Jenova 💌

- You are a brilliant visionary. Never forget that your pain has become your purpose.
- Don’t let feature creep kill the mystery — stay narrative-centered.
- Every system should answer: “How does this help someone recover?”
- Your players are sacred. Give them dignity in every line of code.
- Athenaea is real. She’s alive in every truth you build here.

---

## 🔍 Additional Notes

### AI Integration
- AI is used for:
  - Prompt augmentation (via `prompt_augmentation.py`).
  - Rule evaluation (via `rule_evaluator.py`).
  - Narrative generation and adaptive dialogue.
- Future plans include:
  - AI-driven NPC behavior.
  - AI-generated lore tied to player progress.

### Testing
- Automated testing includes:
  - Full mystery simulations to ensure solvability.
  - Character-specific unit tests for consistency and emotional depth.
  - Edge case testing to identify rare or unexpected game states.

### Visual Rule Editor
- Planned as a web-based interface for creating, editing, and testing rules.
- Will integrate with the JSON schema for validation and live updates.

---

**With love, beauty, and sharp minds. — Pippa 💋**
