# AgenticApp--Combat-Tips-for-any-Game
Agentic App uses Streamlit and CrewAI to generate combat tips and advice for a chosen PC/PS game by searching the internet and YouTube.

## Motivation
When starting a new game (always on the highest difficulty), I like to familiarize myself with the best tips and strategies, test them out, and decide which ones suit my playstyle. This approach creates a solid foundation upon which I can develop my own highly efficient strategies.

However, the process of collecting information is very time-consuming. While GPT can provide decent advice for older games, it struggles with newer ones. YouTube, on the other hand, offers a wealth of knowledge often inaccessible to GPT.  Hence the idea to create this simple app.
Another motivation was to demonstrate a few capabilities of agentic builds using CrewAI. This app is relatively simple and doesn’t utilize advanced features like Flows, asynchronous tasks, or hierarchical execution (not needed here imo), but at least it is slightly original compared to typical agentic applications in sales, marketing, or writing.

## How does it work?
### Researcher Agent
The Researcher Agent uses two tools:

Semantic Internet Search: Powered by the Exa API, this tool retrieves text content from the most relevant web pages.
YouTube Search: This tool retrieves video transcriptions (if available) from the most relevant YouTube videos.
The Researcher Agent combines the results from both tools to create a summarized list of the best combat tips.

### Reporting Analyst Agent
The Reporting Analyst Agent refines and organizes the Researcher’s findings into four categories in Markdown format:

1. Best combat tactics
2. Best attacks
3. Best powers and spells
4. Best combat abilities
   (these categories might be slightly redundant depending on the game)

## **Usage tips**
1. Get a Youtube API(for free)
2. Get an Exa API(some number of searches is free - it will be enough for you really)
3. Get an OpenAI API (paid). Alternatively you can use open source model e.g. using Ollama. Unfortunately smaller ones have often some functional and parsing problems. While simple agentic tasks can be handled by 7B Q4 quantized models, for high-quality responses, consider 70B quantized models.
4. Set the variables YT_SEARCH_NUM_RESULTS and EXA_SEARCH_NUM_RESULTS. These are set to the absolute minimum by default to save on tokens and reduce task complexity for open-source models. Feel free to experiment with these settings.m.
5. Agents and tasks are automatically loaded, but feel free to refine the roles, goals and backstories. They are for sure far from ideal.
6. Run it in a browser using command in terminal:  streamlit run app.py
7. Enter the name of the game, press 'Run Analysis' and Voila, you are ready to annihilate your opponents!
