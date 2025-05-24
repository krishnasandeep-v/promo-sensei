import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from rag_query import generate_answer

# Slack bot tokens (set these as environment variables or add to .env)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

@app.command("/promosensei")
def handle_promosensei(ack, respond, command):
    ack()
    text = command.get('text', '').strip()

    if text.startswith("search"):
        query = text[len("search"):].strip()
        if not query:
            respond("Please provide a query after `search`.")
            return
        answer = generate_answer(query)
        respond(answer)
    elif text.startswith("summary"):
        answer = generate_answer("Give me a summary of the top current deals.")
        respond(answer)
    elif text.startswith("brand"):
        brand_name = text[len("brand"):].strip()
        if not brand_name:
            respond("Please specify a brand name after `brand`.")
            return
        answer = generate_answer(f"List current offers by brand {brand_name}.")
        respond(answer)
    elif text.startswith("refresh"):
        respond("Refreshing offers is not yet implemented.")
    else:
        respond("Unknown command. Use `search`, `summary`, `brand`, or `refresh`.")

if __name__ == "__main__":
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        print("Error: Slack tokens missing. Set SLACK_BOT_TOKEN and SLACK_APP_TOKEN in your environment.")
        exit(1)

    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
