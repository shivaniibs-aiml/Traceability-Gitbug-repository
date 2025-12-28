from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def health():
    return jsonify({"status": "API running"})

if __name__ == "__main__":
    app.run()

