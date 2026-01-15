from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from src.agents.chat_agent.nodes.chat_node import chat
from src.agents.chat_agent.states.chat_agent_state import ChatAgentState
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()


def create_chat_agent_graph() -> CompiledStateGraph:
    """Create a chat agent graph"""
    graph_builder = StateGraph(ChatAgentState)
    graph_builder.add_node("chat_node", chat)
    graph_builder.add_edge(START, "chat_node")
    graph_builder.add_edge("chat_node", END)
    return graph_builder.compile(checkpointer=checkpointer)
