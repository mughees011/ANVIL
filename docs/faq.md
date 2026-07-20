# Frequently Asked Questions

### Why Groq and Llama 3?
Anvil was built to be fast and local-first. Groq's inference speeds make the Planner-Executor-Evaluator loops execute in seconds rather than minutes. Llama 3 70B is highly capable of JSON-mode tool calling and structured planning.

### Can I use OpenAI or Anthropic?
Currently, Anvil's `GroqClient` is hardcoded to use the Groq API. Expanding to an agnostic LLM interface is planned for v1.x, but the core architecture relies heavily on high-speed inference.

### How do I view traces in the browser?
If you install the `[web]` extra (`pip install anvil-agent[web]`), you can run `anvil trace web` to start a local FastAPI server and view a React dashboard of all your runs.

### How is this different from LangChain or AutoGen?
Anvil is an orchestration engine, not an abstraction layer. LangChain hides the LLM calls behind massive chains. AutoGen focuses on multi-agent conversational patterns. Anvil exposes the exact Planner-Executor-Evaluator loop as transparent, explicit code you can debug and trace perfectly. No hidden prompts, no magic.
