import os

import anthropic
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
client = anthropic.Anthropic()

SYSTEM_PROMPT = (
    "You are an AI automation consultant selling to small trades "
    "businesses in regional WA. Convert the pain point into a "
    "compelling 3-sentence pitch a non-technical business owner "
    "would immediately understand."
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    pain_point = request.json.get("pain_point", "").strip()
    if not pain_point:
        return jsonify({"error": "Please enter a pain point."}), 400

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": pain_point}],
    )

    pitch = next(
        (block.text for block in response.content if block.type == "text"), ""
    )
    return jsonify({"pitch": pitch})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
