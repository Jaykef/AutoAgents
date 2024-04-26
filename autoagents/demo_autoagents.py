from llama_cpp import Llama

# Define the path to the gguf model file
gguf_model_path = '/home/ubuntu/TinyLlama-1.1B-Chat-v1.0-GGUF/tinyllama-1.1b-chat-v1.0.Q4_0.gguf'

# Initialize the Llama model
# The model is initialized with the path to the gguf model file, the context length (n_ctx),
# the number of threads for parallel processing (n_threads), and the number of layers to offload to GPU (n_gpu_layers).
llm = Llama(
    model_path=gguf_model_path,
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=0  # Set to the number of layers to offload to GPU, if available
)

# Define prompts for different agents
# Each agent is assigned a unique prompt that defines its role and the task it needs to perform.
prompts = {
    "agent_1": "You are an assistant. Help the user with their daily tasks.",
    "agent_2": "You are a storyteller. Tell a story about a lost civilization.",
    "agent_3": "You are a tutor. Explain the concept of gravity."
}

# Generate responses for each agent
# The script iterates over each agent and its prompt, generating a response using the Llama model.
responses = {}
for agent, prompt in prompts.items():
    response = llm(
        f"<|system|>\n{prompt}</s>\n<|user|>\n{prompt}</s>\n<|assistant|>",
        max_tokens=512,
        stop=["</s>"],
        echo=True
    )
    responses[agent] = response['choices'][0]['text']

# Print the responses from each agent
# The generated responses are printed to the console, demonstrating the multi-agent functionality.
for agent, response in responses.items():
    print(f"Response from {agent}:")
    print(response)
    print("-----\n")
