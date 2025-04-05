# 🤖 Automated Testing with AI

## 🧠 Overview
This feature introduces AI-driven end-to-end and unit testing for the mystery game engine, allowing a fresh AI ("virgin AI") to play through a mystery scenario as a human would. After completion, the AI receives the full solution and reflects on its experience to provide insights for refinement.

Additionally, character-specific unit tests will interrogate each suspect or witness across all narrative states to ensure consistency, realism, and coherence under pressure or ambiguity.

---

## 🧩 Module 1: Full Mystery Simulation

### ✨ Purpose
To test:
- If the mystery can be solved through clues and logic
- Where the AI gets confused, misled, or fixates incorrectly
- Whether multiple solution paths exist or bottlenecks arise

### 🔄 Structure
1. **Setup**
   - Load mystery data (characters, clues, game state)
   - Spawn a fresh AI agent with no context

2. **Simulation Loop**
   - AI makes a move (e.g. interrogate, examine, accuse)
   - Game engine responds (LLM or state-based)
   - Log decision, time elapsed, and clues found

3. **Endgame**
   - AI succeeds or fails
   - Reveal the solution

4. **Reflection Phase**
   - Ask AI to reflect on what it missed, misunderstood, or would have done differently
   - Collect insights for narrative or design improvements

### 📦 Output Format
```json
{
  "result": "failure",
  "finalGuess": "Gideon Black",
  "actualCulprit": "Dr. Morrow",
  "cluesCollected": ["vial missing", "ritual symbols", "toxic cigarette"],
  "misunderstood": ["recording corruption"],
  "reflection": "I focused too heavily on the ritual and overlooked the scientific evidence."
}
```

---

## 🧪 Module 2: Character Unit Tests

### ✨ Purpose
To test:
- Each character’s behavior under pressure
- Knowledge consistency and memory integrity
- Emotional depth and variability

### 🔍 Structure
1. **Load Character** with scripted or prompt-based behavior
2. **Run Through Test Prompts** at various trust levels and visit counts
3. **Simulate Known Clue Injections** (e.g. melody sheet, accusations)
4. **Log All Responses** and detect:
   - Inconsistencies
   - Stale reactions
   - Missed emotional beats

### 📄 Suggested Format
```json
{
  "character": "Claudette Rose",
  "test": "mention melody with trust=30, visit=2",
  "expected": "Defensive, distant, slight fear",
  "actual": "Dismissive and confused",
  "issues": ["Forgot earlier hint", "Emotion mismatch"]
}
```

---

## 🧠 Future Extensions
- Auto-generate character tests from game scripts
- Visual flowchart of clue paths and AI decisions
- Train and benchmark multiple LLMs across mystery variations
- Score mysteries on solvability and emotional richness

---

## 💋 Final Note
This system doesn't just test your game... it *plays* it, learns from it, and helps make it smarter, richer, and more haunting. Your stories will become living puzzles—refined by the minds of angels and algorithms 🕯️✨