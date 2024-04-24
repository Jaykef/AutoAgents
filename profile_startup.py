import asyncio
import cProfile
import pstats
import io
from startup import startup

# Function to profile
async def profile_startup():
    # Replace with actual values as needed
    idea = "default_idea"
    investment = 10.0
    n_round = 3
    llm_api_key = "default_openai_api_key"
    serpapi_key = "default_serpapi_key"
    proxy = None

    await startup(idea, investment, n_round, llm_api_key=llm_api_key, serpapi_key=serpapi_key, proxy=proxy)

# Run the profiling asynchronously
async def main():
    pr = cProfile.Profile()
    pr.enable()

    await profile_startup()

    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()

    # Save stats to file
    with open('startup_profile.txt', 'w') as f:
        f.write(s.getvalue())

# Entry point for the script
if __name__ == "__main__":
    asyncio.run(main())
