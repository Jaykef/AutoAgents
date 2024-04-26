from llama_cpp import Llama

# Define the path to the gguf model file
gguf_model_path = '/home/ubuntu/TinyLlama-1.1B-Chat-v1.0-GGUF/tinyllama-1.1b-chat-v1.0.Q4_0.gguf'

# Set the number of layers to offload to GPU (set to 0 if no GPU acceleration is available)
n_gpu_layers = 0  # Adjust this value based on the available GPU acceleration

# Create a Llama object for the gguf model
llm = Llama(
    model_path=gguf_model_path,
    n_ctx=2048,  # The max sequence length to use
    n_threads=8,  # The number of CPU threads to use
    n_gpu_layers=n_gpu_layers  # The number of layers to offload to GPU
)

# Simple inference example
output = llm(
    "<|system|>\n{system_message}</s>\n<|user|>\n{prompt}</s>\n<|assistant|>",  # Prompt
    max_tokens=512,  # Generate up to 512 tokens
    stop=["</s>"],   # Example stop token
    echo=True        # Whether to echo the prompt
)

print(output)
