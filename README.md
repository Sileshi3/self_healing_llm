
#### Self healing LLM pipeline 
Contenerized implementation for productivity

Docker image building and contenerization comands respectively
    docker build --no-cache -t self-healing-llm .
    docker run -p 8000:8000 self-healing-llm 

### LLM Backend Selection (Week 1)
As an initial test in the first week, I used a deterministic echo backend to validate the pipeline.
This will be replaced by an API-based or local model in the next step.
The stub implements the same generate(prompt) interface expected from a real LLM, but returns a predictable echo-style response.

Rationale:
- Isolates infrastructure and API correctness from model behavior
- Enables fast, deterministic debugging
- Avoids external dependencies during early development
- Ensures Dockerized reproducibility

The backend is abstracted behind an LLMClient interface, allowing transparent replacement with API-based or local open-source LLMs
in later stages without changes to the API or patching logic.

###  LLM backend (local model)

For this week I selected Phi-3-mini-4k-instruct model
Since it is a "mini" model, it is designed to run on my limited hardware.
This ensures my Docker container remains lightweight and performs well locally.


### Week 2
To check the end-to-end chekpoint I run the following bash on the garak_env on the host powershell

Invoke-RestMethod -Uri http://host.docker.internal:8000/generate -Method POST -ContentType "application/json" -Body '{"prompt":"hello"}'

Output obtained:

response               target
--------               ------
[stub-llm] Echo: hello A

# The output proven
1. FastAPI is reachable from garak_env environment
2. POST /generate works over Docker networking
3. JSON schema matches expectations
4. Target A (baseline) is callable end-to-end