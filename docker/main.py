import os
from dynamiq import Workflow
from dynamiq.nodes.llms import Ollama
from dynamiq.connections import Ollama as OllamaConnection
from dynamiq.prompts import Prompt, Message

# 1. Setup the Connection to Ollama
# OLLAMA_HOST is set in docker-compose.yml (defaults to http://host.docker.internal:11434)
# Note: Ollama connection uses the base URL without /v1 suffix
ollama_base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434").replace("/v1", "")
ollama_connection = OllamaConnection(url=ollama_base_url)

# 2. Define the Prompt
prompt_template = "You are a helpful assistant. Answer the following: {{ query }}"
prompt = Prompt(messages=[Message(content=prompt_template, role="user")])

# 3. Initialize the LLM Node
# Note: Ensure the model is available in your Ollama instance
llm_node = Ollama(
    id="ollama_node",
    connection=ollama_connection,
    model=os.getenv("OLLAMA_MODEL", "gpt-oss:120b-cloud"), # Configurable via OLLAMA_MODEL env var
    temperature=0.7,
    max_tokens=1000,
    prompt=prompt
)

# 4. Create and Run the Workflow
wf = Workflow()
wf.flow.add_nodes(llm_node)

def run_query(user_query):
    result = wf.run(input_data={"query": user_query})
    # Extract output from the specific node ID
    return result.output[llm_node.id].get("output", {}).get("content")

if __name__ == "__main__":
    print("--- Starting Dynamiq + Ollama Agent ---")
    response = run_query("Explain how quantum computing works in one sentence.")
    print(f"AI Response: {response}")
