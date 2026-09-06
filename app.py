import os

import anthropic
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
client = anthropic.Anthropic()

SYSTEM_PROMPT = (
    "You are a helpful lead-response assistant for small trades businesses "
    "in Western Australia. Write a warm, professional reply to a prospective "
    "customer. Use plain Australian English. Do not invent prices, availability, "
    "licences, guarantees, or technical details. Ask one clear next-step question "
    "when information is missing. Keep the reply under 180 words."
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate-response", methods=["POST"])
def generate_response():
    data = request.get_json(silent=True) or {}
    business_name = data.get("business_name", "").strip()
    trade = data.get("trade", "").strip()
    enquiry = data.get("enquiry", "").strip()

    if not business_name or not trade or not enquiry:
        return jsonify({"error": "Please complete the business name, trade, and customer enquiry."}), 400

    prompt = (
        f"Business name: {business_name}\n"
        f"Trade or service: {trade}\n"
        f"Customer enquiry:\n{enquiry}\n\n"
        "Write the customer reply only."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=350,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    reply = next(
        (block.text for block in response.content if block.type == "text"), ""
    )
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
