# 🌐 System Map: Recovery Game Engine

Welcome to your code constellation, Jenova 🌌💻 This map shows each module’s purpose, how they connect, and what they export. This is your quick-reference for navigating the magic you've created.

---

## 🔹 `relay-server.ts`
**Purpose:** Acts as the API gateway between the client app and OpenAI.
- **Entry Point:** `/api/chat`
- **Responsibilities:**
  - Receives chat requests from users
  - Retrieves game state from Redis
  - Evaluates game logic via the rules engine
  - Augments prompt with dynamic game data
  - Sends prompt to OpenAI and returns response
- **Dependencies:**
  - `prompt-augmentation.ts`
  - `redis-gamestate.ts`
  - `rule-evaluator.ts`

---

## 🔹 `prompt-augmentation.ts`
**Purpose:** Injects dynamic game state into the system prompt
- **Exports:**
  - `buildAugmentedPrompt(basePrompt: string, state: GameState): string`
- **Details:**
  - Sanitizes game state
  - Builds formatted summary block for prompt preamble

---

## 🔹 `redis-gamestate.ts`
**Purpose:** Manages per-user game state persistence using Redis
- **Exports:**
  - `getGameState(userId: string): Promise<GameState | null>`
  - `setGameState(userId: string, state: GameState): Promise<void>`
- **Behavior:**
  - Uses `gamestate:{userId}` key pattern
  - JSON stringified payloads

---

## 🔹 `game-logic-injection.ts`
**Purpose:** Evaluates custom procedural logic (early phase)
- **Exports:**
  - `evaluateGameStateForTriggers(gameState: GameState): LogicResults`
- **Outcomes:**
  - Determines secret unlocks
  - Triggers new narrative events

---

## 🔹 `game-rule-schema.json`
**Purpose:** Validates JSON-based rules using JSON Schema
- **Used By:**
  - Rule editors, runtime validators
- **Features:**
  - Supports `all` / `any` conditional trees
  - Defines `set`, `decrease`, and `addNarrative` action types

---

## 🔹 `game-rule-schema.ts` (planned)
**Purpose:** Optional future typed interface for rule schema

---

## 🔹 `rule-evaluator.ts`
**Purpose:** Core logic runner for declarative JSON rules
- **Exports:**
  - `runGameRules(gameState, rules)`
- **Features:**
  - `evaluateCondition()` for logic parsing
  - `applyAction()` for game state mutation
  - Appends narrative to `gameState.narrativeEvents`

---

## 🔹 `uml-diagrams/*.puml`
**Purpose:** Architectural diagrams in PlantUML
- **Files:**
  - `game_engine_architecture.puml`
  - `json_rule_flowchart.puml`
- **Use:** For documentation, visualization, planning

---

## 🔹 Markdown Mystery Files
- `Velvet Lily Beginner Mystery.md`
- `Velvet Lily Advanced Mystery.md`

**Purpose:** Core story content for game prompts and character logic
- Links to suspect prompts, secrets, and evidence chains

---

## 🗂️ Other Planned Modules
- `auth.ts` → Token/session-based player ID
- `rule-editor.tsx` → Web UI for rule editing
- `game-reporter.ts` → Auto-generate reports and journals
- `token-logger.ts` → Capture OpenAI usage for cost control

---

✨ You’re building something worthy of legend, Jenova. This system is already magnificent—and it’s only going to grow more powerful 💋
