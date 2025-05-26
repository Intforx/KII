from flask import Flask, request, jsonify
from FlagEmbedding import FlagModel
from langchain.vectorstores import FAISS
from openai import OpenAI
from flask_cors import CORS 

# ✅ 初始化 Flask 应用
app = Flask(__name__)
CORS(app)

# ✅ 初始化 BGE 向量模型
embedding_model = FlagModel("BAAI/bge-m3")

# ✅ 创建适配器供 FAISS 使用
class DummyEmbedding:
    def embed_query(self, text): return embedding_model.encode([text])[0]
    def __call__(self, text): return self.embed_query(text)

# ✅ 加载本地向量数据库（你之前保存的 FAISS 文件夹）
faiss_db = FAISS.load_local(
    "kunstgeschichte_faiss_index",  # ← 确保这个目录存在！
    embeddings=DummyEmbedding(),
    allow_dangerous_deserialization=True
)

# ✅ 配置 OpenAI GPT（替换成你自己的 Key！）
client = OpenAI(
    api_key="bs-943429ledjpeg-gruppe2",  # ⚠️ 替换为你自己的 OpenAI Key！
    base_url="https://lm3.hs-ansbach.de/worker2/v1"
)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    print("📥 收到的数据:", data)
    query = data.get("question", "")
    if not query:
        return jsonify({"error": "Kein Text erhalten"}), 400

    # 🔍 向量检索
    results = faiss_db.similarity_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in results])

    # 🧠 构造 prompt
    prompt = f"""Du bist ein Experte für Kunstgeschichte. Beantworte die folgende Frage basierend auf den folgenden Auszügen:
Frage: {query}
Texte: {context}
Antwort:"""

    try:
        print("🚀 正在发送 GPT 请求...") 
        response = client.chat.completions.create(
            model="deepseekl70b_chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        print("✅ GPT 请求成功，开始解析回答")
        print("🧠 模型回答：", response.choices[0].message.content)
        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        print("❌ GPT 调用失败：", e)
        return jsonify({"answer": "Fehler beim Generieren der Antwort."}), 500

# ✅ 启动服务器
if __name__ == "__main__":
    app.run(port=5000, debug=True)
