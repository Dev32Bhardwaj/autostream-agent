def detect_intent(user_message: str) -> str:
    msg = user_message.lower()

    # 1️⃣ High intent
    if any(word in msg for word in [
        "sign up", "signup", "buy", "subscribe", "try",
        "pro plan", "start pro", "want pro"
    ]):
        return "high_intent"

    # 2️⃣ Product inquiry
    if any(word in msg for word in [
        "price", "pricing", "cost", "plan", "features"
    ]):
        return "product_inquiry"

    # 3️⃣ Greeting
    if any(word in msg for word in ["hi", "hello", "hey"]):
        return "greeting"

    return "product_inquiry"
