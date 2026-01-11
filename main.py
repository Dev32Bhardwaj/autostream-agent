from agent.graph import build_graph

graph = build_graph()

state = {
    "user_messages": [],
    "agent_messages": [],
    "intent": None,
    "high_intent_stage": None,
    "name": None,
    "email": None,
    "platform": None
}

print("AutoStream Agent is live! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    state["user_messages"].append(user_input)
    state = graph.invoke(state)

    print("Agent:", state["agent_messages"][-1])
