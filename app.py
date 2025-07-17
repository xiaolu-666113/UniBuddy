from flask import Flask, request, jsonify, render_template
from spark_api import ask_spark, session_context
from chatdoc_api import ask_question

app = Flask(__name__)

# 固定后台上传好的文档 file_id（请替换成你实际的）
FIXED_FILE_ID = "015869c84cf84e349d32a464900da4a5"

@app.route('/ask_doc', methods=['POST'])
def ask_doc():
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing question"}), 400

    try:
        answer = ask_question(FIXED_FILE_ID, question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    uid = request.json.get("uid", "default_user")
    reply = ask_spark(user_input, uid)
    return jsonify({"reply": reply})

if __name__ == '__main__':
    app.run(debug=True)