# test_graph.py
from graph import graph


def test_full_flow():
    # --- Input state ---
    initial_state = {
        "patient_id": "e3MBXCOmcoLKl7ayLD51AWA3",
        "question": "What medication adjustments should be considered?",
        "patient_context": "",
        "literature_context": "",
        "summary": None
    }

    # --- Config required by MemorySaver ---
    config = {"configurable": {"thread_id": "test-thread-001"}}

    print("🚀 Running graph...\n")

    # --- Run the graph ---
    result = graph.invoke(initial_state, config=config)

    # --- Print each stage ---
    print("✅ FHIR Patient Context:")
    print(result["patient_context"])

    print("\n✅ Pinecone Literature Context:")
    print(result["literature_context"])

    print("\n✅ Claude Summary:")
    import json
    print(json.dumps(result["summary"], indent=2))


test_full_flow()