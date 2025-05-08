## 🐶 dogbot-agent
DogBot gives your dog a voice.

It’s an empathetic AI agent that helps you understand your dog’s behavior — powered by GPT-4 and a semantic database (Weaviate).  
Together, they translate symptoms into insights and support you with clear, kind guidance.

This repo contains the backend: a FastAPI app that connects OpenAI's language intelligence with structured dog behavior knowledge.

---

## 🔧 Local Setup
Clone the repo and install dependencies in a virtual environment:
```bash
git clone https://github.com/kemperfekt/dogbot-agent.git
cd dogbot-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🧪 Start the Agent
```bash
uvicorn main:app --reload
```
➡️ Available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔑 Required Environment Variables
Make sure to set these system-wide:
- `OPENAI_APIKEY` – your OpenAI key
- `WEAVIATE_API_KEY` – API key for your Weaviate Cloud instance
- `WEAVIATE_URL` – the REST endpoint of your Weaviate Cloud

---

## 📦 Tech Stack
- FastAPI – modern Python web framework
- OpenAI Python SDK – connects to GPT
- Weaviate Python Client – queries the semantic knowledge base
- Plus: pydantic, uvicorn, python-dotenv (optional for local dev)

---

## 🔄 How It Works
A user describes a behavioral symptom (e.g., “Why is my dog barking at other dogs?”)
1. GPT analyzes the input and suggests which instincts are likely involved
2. The dog responds from its own perspective (instinctive, emotional, sensory)
3. GPT asks gentle follow-up questions to clarify uncertainty
4. A **Mentor Agent** explains the relevant background knowledge to the human
5. A **Diagnosis Coach** synthesizes the input and identifies the leading instinct
6. A **Relationship Companion** reflects on the bond between human and dog and encourages learning and mutual understanding

## Agents
🐾 Hund (Behavious)
🛠 Coach (Knowledge & Education)
💛 Companion (Relationship)


---

## 📚 Related Repositories
- 🔵 Frontend (React): [github.com/kemperfekt/dogbot-ui](https://github.com/kemperfekt/dogbot-ui)
- 🟡 Data & Weaviate content: [github.com/kemperfekt/dogbot-ops](https://github.com/kemperfekt/dogbot-ops)
- 🐶 Project meta-repo with vision and coordination: [github.com/kemperfekt/dogbot](https://github.com/kemperfekt/dogbot)
