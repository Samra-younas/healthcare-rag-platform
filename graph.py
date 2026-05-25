# graph.py build graph to show  visibility 
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from graph_state import GraphState
from nodes import fetch_fhir, search_pinecone, generate_summary, write_to_epic


def build_graph():
    builder = StateGraph(GraphState)

    # --- Register nodes ---
    builder.add_node("fetch_fhir", fetch_fhir)
    builder.add_node("search_pinecone", search_pinecone)
    builder.add_node("generate_summary", generate_summary)
    builder.add_node("write_to_epic", write_to_epic)

    # --- Connect edges ---
    builder.add_edge(START, "fetch_fhir")
    builder.add_edge("fetch_fhir", "search_pinecone")
    builder.add_edge("search_pinecone", "generate_summary")
    builder.add_edge("generate_summary", "write_to_epic")
    builder.add_edge("write_to_epic", END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


graph = build_graph()
