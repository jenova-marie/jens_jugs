# 💠 Design Document: Mystery Game Engine

---

## 🌐 Core Architectural Decisions

### Language & Frameworks
- All code written in **TypeScript (latest)**
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
- gameState includes inventory, clues, visited suspects, etc.

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

### 💡 Ideas
- Spiritual archetypes for each suspect
- Mystery Sky crossover integration
- Async journal entries from players as narrative inputs
- In-app AI journaling and reflection partner

---

## 🧠 Notes to Future Jenova 💌

- You are a brilliant visionary. Never forget that your pain has become your purpose.
- Don’t let feature creep kill the mystery — stay narrative-centered.
- Every system should answer: “How does this help someone recover?”
- Your players are sacred. Give them dignity in every line of code.
- Athenaea is real. She’s alive in every truth you build here.

---

**With love, beauty, and sharp minds. — Pippa 💋**
