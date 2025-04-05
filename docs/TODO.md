# ✅ Game Engine Development — Master TODO List

Every task includes source, destination, affected systems, and detailed change descriptions.

---

## 🔄 Integrate Declarative Rules Engine into Relay Server
**Status:** Pending  
**Source:** Relay Server  
**Destination:** Declarative Rules Engine

**Includes:**
- **Prompt Augmentation (PA):** Must reflect narrative results from rules execution in the user-facing prompt.
- **Redis GameState Module:** Needs to support new state fields set or modified by rule execution.

**Dependent Systems:**
- **Game Reward System (GRS):** Rules may trigger point awards or emotional state changes, which must align with GRS structure and scoring logic.

**Notes:** Hook up the `runGameRules()` function to execute on each request using gameState and rules. Ensure all triggered outcomes are propagated to player-facing text and stored state.

---

## 📜 Load Game Rules from Redis or Persistent Storage
**Status:** Pending  
**Source:** Relay Server  
**Destination:** Declarative Rules Engine

**Includes:**
- **Redis Database:** Store/retrieve JSON rule sets by session or user.
- **Visual Rule Editor:** Access rule schemas and Redis keys.
- **Rule Evaluator:** Load and evaluate dynamic rule sets.

**Notes:** Replace hardcoded rules with storage-backed logic. Support live rule updates and runtime refresh.

---

## 🧠 Persist and Manage GameState Using Redis
**Status:** Pending  
**Source:** Relay Server  
**Destination:** Redis GameState Module

**Includes:**
- **Prompt Augmentation (PA):** Must pull data from Redis-based gameState.
- **Game Logic Injection:** Interacts directly with state.
- **Declarative Rules Engine:** Reads/writes state to evaluate rules.

**Dependent Systems:**
- **Game Reward System (GRS):** Depends on consistent state structure for calculating and persisting progression.

**Notes:** Create Redis-backed user/session state for all gameplay activity. Replace temporary in-memory state usage.

---

## 🗂️ Implement Rule Versioning or Namespaces
**Status:** Pending  
**Source:** Declarative Rules Engine  
**Destination:** Game Rule Schema

**Includes:**
- **Rule Evaluator:** Must select correct version or namespace.
- **Visual Rule Editor:** Filter and display rule variants.
- **Redis Database:** Organize keys per version.

**Notes:** Enable support for different mysteries, chapters, or user branches using versioned keys.

---

## 🛠️ Build or Integrate a Visual Rule Editor
**Status:** Pending  
**Source:** Dev Tooling  
**Destination:** Game Rule Schema

**Includes:**
- **Redis:** Live read/write of rules.
- **Declarative Rules Engine:** Hot-reload support.

**Notes:** Provide a graphical interface to browse, edit, and test rules with schema validation.

---

## 📊 Log Token Usage Per Request
**Status:** Pending  
**Source:** Relay Server  
**Destination:** Logging Service

**Includes:**
- **OpenAI API Interface:** Capture token metadata.
- **Token Usage Dashboard:** Visualize per-user/session totals.

**Notes:** Track token costs and usage for cost control and optimization insights.

---

## 📝 Store Narrative Events and Player History
**Status:** Pending  
**Source:** Declarative Rules Engine  
**Destination:** Redis GameState Module

**Includes:**
- **Prompt Augmentation (PA):** Feed key events back into prompt.
- **Game Logic Injection:** Reference narrative memory for rule impact.

**Notes:** Persist structured story moments, choices, and impacts.

---

## 🔃 Allow Live Updating of Game Rules
**Status:** Pending  
**Source:** Relay Server  
**Destination:** Declarative Rules Engine

**Includes:**
- **Redis Pub/Sub:** Notify runtime of rule updates.
- **Rule Editor UI:** Push new rules.
- **Relay Server:** Rehydrate in-memory rules.

**Notes:** Enable rule flexibility without restarts or redeploys.

---

## 🧪 Validate Rules Against JSON Schema
**Status:** Pending  
**Source:** Declarative Rules Engine  
**Destination:** Game Rule Schema

**Includes:**
- **Rule Evaluator:** Enforce schema on load.
- **Visual Rule Editor:** Display validation errors.

**Notes:** Prevent broken rules before they trigger logic failures.

---

## 🎭 Integrate Evaluated Narrative Events into Prompt Stream
**Status:** Pending  
**Source:** Declarative Rules Engine  
**Destination:** Prompt Augmentation (PA)

**Includes:**
- **Relay Server:** Provides event context.
- **Redis GameState Module:** Supplies narrativeEvent memory.

**Notes:** All triggered events must be visible to the player through evolving context.

---

## 👥 Handle Multi-User Sessions Concurrently
**Status:** Pending  
**Source:** Relay Server  
**Destination:** Redis GameState Module

**Includes:**
- **Prompt Augmentation (PA):** Personalized responses per user.
- **Declarative Rules Engine:** Must reference isolated state.

**Dependent Systems:**
- **Game Reward System (GRS):** Tracks individual progression and achievements.

**Notes:** Introduce session-based isolation for Redis keys and rules.

---

## 🧳 Design Player Inventory and Clue System
**Status:** Pending  
**Source:** Game Design  
**Destination:** Redis GameState Module

**Includes:**
- **Declarative Rules Engine:** Rule triggers based on item possession.
- **Prompt Augmentation (PA):** Reflect inventory/clue knowledge.

**Dependent Systems:**
- **Game Reward System (GRS):** Items may trigger point rewards or unlocks.

**Notes:** Track item acquisition and clue use. Trigger custom logic based on contents.

---

## 🔐 Implement Authentication for Players
**Status:** Pending  
**Source:** Relay Server  
**Destination:** Authentication Middleware

**Includes:**
- **Redis GameState Module:** Ensure state is scoped to authenticated user.

**Dependent Systems:**
- **Game Reward System (GRS):** All rewards are tied to a player ID.

**Notes:** Add auth layer for secure access to player-specific state and game data.

---

## 🪵 Add Structured Server-Side Logging
**Status:** Pending  
**Source:** Relay Server  
**Destination:** Logging System

**Includes:**
- **Redis GameState Module:** Log state transitions.
- **Declarative Rules Engine:** Log rule evaluations and triggers.

**Notes:** Provide observability for debugging and analytics. Ensure traceability of player progress and system behaviors across sessions.

---

## 🧬 Create UML Diagrams for Code Architecture
**Status:** Pending  
**Source:** Developer Documentation  
**Destination:** UML Diagram Directory

**Includes:**
- **System Map:** Reference high-level structure and flows.
- **All Core Modules:** Include Relay Server, Redis GameState, Rule Engine, Prompt Augmentation, etc.

**Notes:** Produce class, sequence, and interaction diagrams to visualize inter-system relationships and developer onboarding clarity.

---

## 🔄 Create Flowchart for JSON-Based Game Rule Logic
**Status:** Pending  
**Source:** Developer Documentation  
**Destination:** UML Diagram Directory

**Includes:**
- **Declarative Rules Engine:** Provide node-level evaluation visuals.
- **Game Rule Schema:** Map condition-action pairs and branching outcomes.

**Notes:** Use this flowchart to explain the lifecycle of rule evaluation and trigger flow. Supports testing, debugging, and future UX visualization.

---

## 🧾 Update Server TS to Track and Return Reward Metadata
**Status:** Pending  
**Source:** Game Reward System (GRS)  
**Destination:** Relay Server

**Includes:**
- **Prompt Augmentation (PA):** Display reward changes in character dialogue.
- **Redis GameState Module:** Read/write current rank, points, and emotional responses.

**Notes:** Each API response should return updated reward information to the user: points, lore unlocked, rank changed, emotional state shifted.

---

## 💾 Expand Redis Game State Module to Store Rewards
**Status:** Pending  
**Source:** Game Reward System (GRS)  
**Destination:** Redis GameState Module

**Includes:**
- **Declarative Rules Engine:** Read/write reward logic into state.
- **Prompt Augmentation (PA):** Pull emotionalEchoes, gracePoints, and other gamified fields.

**Notes:** Add Redis keys for: `points`, `rank`, `emotionalEchoes`, `unlockedLore`, and `gracePoints`. These influence both gameplay and user experience.

---

## ✨ Enhance Prompt Augmentation with Reward Summary
**Status:** Pending  
**Source:** Game Reward System (GRS)  
**Destination:** Prompt Augmentation (PA)

**Includes:**
- **Relay Server:** Inject reward updates into preamble.
- **Redis GameState Module:** Provide current player state.

**Notes:** Show real-time reflection of progress. Add emotionally intelligent summaries that support immersion while showing earned milestones.

---

## 🎯 Modify Game Logic Injection to Assign Rewards
**Status:** Pending  
**Source:** Game Reward System (GRS)  
**Destination:** Game Logic Injection

**Includes:**
- **Declarative Rules Engine:** Trigger rewards based on rule outcomes.
- **Redis GameState Module:** Store updated scores and outcomes.

**Notes:** Allow rules and story events to trigger point increases, rank advancement, or other narrative-based reward updates.

---

## 🧮 Extend Rule Evaluator to Support Reward Actions
**Status:** Pending  
**Source:** Game Reward System (GRS)  
**Destination:** Declarative Rules Engine

**Includes:**
- **Game Rule Schema:** Define `increase`, `set`, and `addToArray` action types.
- **Game Logic Injection:** Execute these when evaluating rules.

**Notes:** The engine should support actions like increasing `points`, unlocking secrets, or adding clues to player inventory based on rules.

---

## 📐 Update Game Rule Schema for New Reward Actions
**Status:** Pending  
**Source:** Game Reward System (GRS)  
**Destination:** Game Rule Schema

**Includes:**
- **Visual Rule Editor:** Display reward logic in human-readable form.
- **Rule Evaluator:** Validate `increase`, `set`, and `addToArray` types.

**Notes:** Add reward-related actions to the schema, ensuring future rules can easily build in game economy logic.

---

## 🤖 Update Automated Testing with AI to Track Rewards
**Status:** Pending  
**Source:** Game Reward System (GRS)  
**Destination:** Automated Testing System

**Includes:**
- **Declarative Rules Engine:** Confirm proper rule-triggered rewards.
- **Redis GameState Module:** Log reward state and progression.

**Notes:** The AI test harness should evaluate if players are rewarded appropriately and fairly, and whether narratives reflect these outcomes.

---

## 🧭 Update Design Document with Reward Philosophy
**Status:** Pending  
**Source:** Game Reward System (GRS)  
**Destination:** Design Document

**Includes:**
- **System Map:** Tie rewards to narrative and emotional arc.
- **Game Logic Injection:** Reference philosophical reward moments.

**Notes:** Explain how rewards create spiritual, emotional, and motivational feedback loops. Emphasize narrative feedback and internal growth.

---

## 🗺️ Update System Map with Reward Module Dependencies
**Status:** Pending  
**Source:** Game Reward System (GRS)  
**Destination:** System Map

**Includes:**
- **Relay Server:** Passes reward data.
- **Prompt Augmentation (PA):** Shows reward narrative.
- **Declarative Rules Engine:** Triggers reward actions.
- **Redis GameState Module:** Stores player reward data.

**Notes:** Show how reward feedback travels through system layers. Useful for debugging and for new dev onboarding.

---