from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import BaseTool
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import os
import yaml
from crewai_tools import tool
from exa_py import Exa
import streamlit as st


# ----------------------------------------------------------------------------------------------------------------------
# 0. Setting Keys, variables and loading .yaml files.
# ----------------------------------------------------------------------------------------------------------------------

YT_API_KEY = "..."
youtube = build('youtube', 'v3', developerKey=YT_API_KEY)

exa_api_key = "..."

openai_api_key = "..."
os.environ["OPENAI_API_KEY"] = openai_api_key
os.environ["OPENAI_MODEL_NAME"] = 'gpt-4o-mini'

# Optionally disable openai model by commenting 3 lines above and uncomment open source model from Ollama (below),
# and then uncomment lines in agents with parameter 'llm'

# ollama_llm = LLM(
#     model='ollama/llama3.1',
#     base_url='http://localhost:11434',
# )

YT_SEARCH_NUM_RESULTS = 5
EXA_SEARCH_NUM_RESULTS = 2


files = {
    'agents': 'config/agents.yaml',
    'tasks': 'config/tasks.yaml'
}

configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

agents_config = configs['agents']
tasks_config = configs['tasks']

# ----------------------------------------------------------------------------------------------------------------------
# 1. Creating tools, agents and tasks.
# ----------------------------------------------------------------------------------------------------------------------


# Tool creation (by class)     -   first method
class YouTubeAnalysisTool(BaseTool):
    name: str = "YouTube Analysis Tool"
    description: str = "Search YouTube and analyze top videos transcripts for a given query."

    def _run(self, query: str) -> str:
        videos = self.search_videos(query)
        results = []
        for video in videos:
            title = video['title']
            transcript = self.get_transcription(video['id'])
            print(f"Title: {title}\nTranscript (excerpt): {transcript}")
            if transcript != '':
                results.append(f"Tips and advices: {transcript}")
        return "\n".join(results)

    def search_videos(self, query):
        request = youtube.search().list(
            q=query,
            part='id,snippet',
            type='video',
            maxResults=YT_SEARCH_NUM_RESULTS
        )
        response = request.execute()
        return [
            {
                'id': item['id']['videoId'],
                'title': item['snippet']['title']
            }
            for item in response['items']
        ]

    def get_transcription(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([t['text'] for t in transcript])
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            return ''


# Tool creation (by decorator)     -   second method

@tool("Exa search and get contents")
def search_and_get_contents_tool(query: str):
    """Tool using Exa's Python SDK to run semantic search and return result highlights."""

    exa = Exa(exa_api_key)
    response = exa.search_and_contents(
        query,
        type="neural",
        use_autoprompt=True,
        num_results=EXA_SEARCH_NUM_RESULTS,
        text=True,
        highlights=False
    )

    parsedResult = ''.join([
        f'Tips and advices: {"".join(eachResult.text)}'
        for idx, eachResult in enumerate(response.results)
    ])

    return parsedResult


researcher = Agent(
    config=agents_config['researcher'],
    tools=[
        search_and_get_contents_tool,
        YouTubeAnalysisTool()
    ],
    verbose=True,
    # llm=ollama_llm
)

reporting_analyst = Agent(
    config=agents_config['reporting_analyst'],
    verbose=True,
    # llm=ollama_llm
)

research_task = Task(
    config=tasks_config['research_task'],
    agent=researcher
)

reporting_task = Task(
    config=tasks_config['reporting_task'],
    agent=reporting_analyst
)

# ----------------------------------------------------------------------------------------------------------------------
# 2. Creating the crew.
# ----------------------------------------------------------------------------------------------------------------------

combat_tips_crew = Crew(
    agents=[researcher, reporting_analyst],
    tasks=[research_task, reporting_task],
    process=Process.sequential,
    verbose=True,
)

# ----------------------------------------------------------------------------------------------------------------------
# 3. Creating Streamlit UI
# ----------------------------------------------------------------------------------------------------------------------
st.title("Combat Tips for a chosen game")

query = st.text_input("Enter a name of your game:")

if st.button("Run Analysis"):
    st.subheader("Analysis Results")
    if query:
        inputs = {'topic': query}
        result = combat_tips_crew.kickoff(inputs=inputs)
        st.text(result)
    else:
        st.error("Please enter a correct name of the game.")