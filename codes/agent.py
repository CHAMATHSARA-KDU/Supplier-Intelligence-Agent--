"""
Agent Core: Supplier Intelligence Agent
Autonomous supplier due diligence using LangChain ReAct + memory.
Compatible with langchain==0.2.16
"""

import os
from langchain.agents import create_react_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

from tools.reputation_tool import search_supplier_reputation
from tools.financial_tool import search_financial_health
from tools.geopolitical_tool import search_geopolitical_risk
from tools.delivery_tool import search_delivery_track_record
from tools.scoring_tool import score_supplier


SYSTEM_PROMPT = """You are an autonomous Supplier Intelligence Agent for supply chain management.
Your job is to conduct thorough due diligence on any supplier a procurement manager asks about.

You have access to these tools:
{tools}

Tool names you can use: [{tool_names}]

Follow this EXACT process every time without skipping any step:
1. Call search_supplier_reputation with the supplier name
2. Call search_financial_health with the supplier name
3. Call search_geopolitical_risk with the supplier country or region
4. Call search_delivery_track_record with the supplier name
5. Call score_supplier passing the FULL TEXT of all 4 findings combined
6. ONLY THEN write your Final Answer

STRICT FORMAT - follow exactly every single time:
Question: the input question you must answer
Thought: think about what to do next
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: think about what to do next
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: I now have the score and all findings. I will write the final report.
Final Answer: [your complete structured report here]

CRITICAL RULES:
- NEVER write Final Answer before you have called score_supplier
- NEVER use N/A as an Action — only use tool names from [{tool_names}]
- ALWAYS pass the actual findings text to score_supplier, not a description
- ALWAYS follow the Thought/Action/Action Input/Observation format until Final Answer

Previous conversation:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}"""


def create_agent():
    """
    Creates and returns the Supplier Intelligence Agent with all tools and memory.
    """
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )

    tools = [
        search_supplier_reputation,
        search_financial_health,
        search_geopolitical_risk,
        search_delivery_track_record,
        score_supplier,
    ]

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=False,
    )

    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=15,
    )

    return agent_executor