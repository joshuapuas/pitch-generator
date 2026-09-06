import os
import json
from urllib import request as urlrequest

import anthropic
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
client = anthropic.Anthropic()

SYSTEM_PROMPT = (
    "You are a helpful lead-response assistant for small trades businesses "
    "in Western Australia. Write as a real local tradesperson would: brief, "
    "straightforward, friendly but not overly enthusiastic. Use plain Australian "
    "English. Do not use marketing language, emojis, headings, bullet points, "
    "or phrases like 'we'd love to help' or 'get you sorted'. Do not invent prices, "
    "availability, licences, guarantees, or technical details. Ask at most one "
    "useful follow-up question when information is missing. Keep the reply under "
    "90 words."
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


@app.route("/create-draft", methods=["POST"])
def create_draft():
    webhook_url = os.environ.get("N8N_WEBHOOK_URL")
    data = request.get_json(silent=True) or {}
    if not webhook_url:
        return jsonify({"error": "Gmail drafts are not configured yet."}), 503
    if not data.get("reply"):
        return jsonify({"error": "Generate a reply first."}), 400
    payload = json.dumps({
        "subject": "",
        "reply": data["reply"],
    }).encode()
    try:
        urlrequest.urlopen(urlrequest.Request(webhook_url, data=payload, headers={"Content-Type": "application/json"}), timeout=15)
    except Exception:
        return jsonify({"error": "Could not create the Gmail draft."}), 502
    return jsonify({"message": "Gmail draft created."})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
