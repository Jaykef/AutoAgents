import json

# Mock AsyncAzureOpenAI client
class MockAsyncAzureOpenAI:
    def __init__(self, *args, **kwargs):
        pass

    async def chat_completions_create(self, **kwargs):
        # Return a mock response with the expected fields in the correct format
        return {
            "Roles List": '''```
{
    "name": "Language Expert",
    "descriptions": "Expert in summarizing information",
    "prompt": "You are a Language Expert. Your task is to summarize information.",
    "tools": [],
    "steps": ["Understand the task", "Extract information", "Construct response"]
},
{
    "name": "Data Analyst",
    "descriptions": "Expert in data analysis",
    "prompt": "You are a Data Analyst. Your task is to analyze data.",
    "tools": ["Data Analysis Tool"],
    "steps": ["Collect data", "Analyze data", "Present findings"]
}
```''',
            "Execution Plan": "1. Language Expert: Summarize the information\n2. Data Analyst: Analyze the data and present findings",
            "Anything UNCLEAR": "The specific data sources to be used by the Data Analyst are not clear."
        }

# Replace the actual AsyncAzureOpenAI client with the mock
aclient = MockAsyncAzureOpenAI()
