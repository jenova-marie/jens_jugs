# AI Wiki: Jens Jugs Mystery Game Engine 💡

This document outlines how AI is integrated into the Jens Jugs Mystery Game Engine, focusing on its role in enhancing gameplay, narrative, and system functionality.

---

## **1. Role of AI in the Game Engine**
AI is used to provide dynamic and immersive gameplay by:
- **Prompt Augmentation**: Enhancing player interactions by dynamically generating responses based on the game state and narrative context.
- **Rule Evaluation**: Assisting in evaluating complex game rules and conditions to drive the story forward.
- **Narrative Generation**: Generating adaptive storylines and dialogue based on player actions and decisions.
- **Testing Automation**: Simulating gameplay scenarios to test game logic and rule interactions.

---

## **2. AI Integration Points**
### **a. Prompt Augmentation**
- The `prompt_augmentation.py` module uses OpenAI's API to:
  - Generate responses for player queries.
  - Incorporate game state elements (e.g., inventory, trust levels) into the prompts.
  - Provide contextually relevant hints or narrative progressions.

### **b. Rule Evaluation**
- The `rule_evaluator.py` module leverages AI to:
  - Evaluate complex conditions in game rules.
  - Suggest rule optimizations or highlight potential conflicts.
  - Dynamically adjust rules based on player behavior.

### **c. Narrative Adaptation**
- AI is used to:
  - Generate dialogue for NPCs (non-player characters).
  - Adapt the storyline based on player decisions and game state.
  - Create unique narrative paths for replayability.

---

## **3. Token Usage Tracking**
- OpenAI API usage is tracked to monitor token consumption.
- Planned features include:
  - Logging token usage per session.
  - Displaying token usage statistics for debugging and cost management.

---

## **4. Planned Enhancements**
### **a. Advanced AI Testing**
- Automate testing of game scenarios using AI to simulate player actions.
- Use AI to identify edge cases and potential bugs in game logic.

### **b. AI-Driven NPC Behavior**
- Implement AI-driven decision-making for NPCs to create more lifelike interactions.
- Allow NPCs to adapt their behavior based on player trust levels and narrative flags.

### **c. AI-Generated Lore**
- Use AI to generate collectible lore items based on the game’s narrative and player progress.

---

## **5. Limitations and Considerations**
- **Cost**: OpenAI API usage can be expensive; token tracking is essential for managing costs.
- **Latency**: API calls may introduce delays; caching frequently used responses is recommended.
- **Ethical Concerns**: Ensure AI-generated content aligns with the game’s tone and avoids harmful or inappropriate outputs.

---

## **6. Configuration**
- The OpenAI API is configured in the `.env` file:
  ```env
  OPENAI_API_KEY=your-api-key-here