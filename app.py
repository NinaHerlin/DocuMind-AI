import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# 1. Load API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 2. Config Halaman & Embed CSS
st.set_page_config(
    page_title="DocuMind AI - Autumn Edition",
    page_icon="🍁",
    layout="wide"
)

css_path = Path(__file__).with_name("style.css")
st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.title("🍁 DocuMind AI")
    st.caption("Asisten Dokumen Cerdas & Hangat")
    st.divider()

    st.subheader("Status Layanan")
    if GROQ_API_KEY:
        st.success("Sistem AI Siap", icon="✅")
    else:
        st.error("API Key Belum Ada", icon="🚨")

    st.divider()
    st.markdown("**Mesin AI Utama**")
    st.code("openai/gpt-oss-120b", language="text")

# 4. Hero Banner
st.markdown(
    '<div class="hero">'
    '<div class="hero-kicker">✦ Workspace Dokumen AI</div>'
    '<h1 class="main-title">Pahami isi dokumen dengan nyaman.</h1>'
    '<p class="sub-title">Unggah berkas PDF kamu, dapatkan rangkuman otomatis, dan tanyakan detail poin penting di dalamnya secara instan.</p>'
    '</div>',
    unsafe_allow_html=True,
)

if not GROQ_API_KEY:
    st.error("⚠️ File `.env` belum dikonfigurasi dengan `GROQ_API_KEY`. Silakan atur terlebih dahulu.")
    st.stop()

# 5. File Uploader
st.markdown("### 📄 Pilih Dokumen")
uploaded_file = st.file_uploader(
    "Unggah file PDF kamu di sini",
    type="pdf",
    help="Pilih file PDF. AI akan memproses teks di dalamnya secara lokal.",
)

if not uploaded_file:
    st.markdown(
        '<div class="workflow">'
        '<div><span class="step-number">01</span><br><strong>Unggah PDF</strong>'
        '<p>Pilih atau tarik dokumen yang ingin kamu pelajari ke area atas.</p></div>'
        '<div><span class="step-number">02</span><br><strong>Indeks Otomatis</strong>'
        '<p>Sistem membaca dan mengekstrak informasi penting secara otomatis.</p></div>'
        '<div><span class="step-number">03</span><br><strong>Tanya Jawab</strong>'
        '<p>Minta ringkasan, penjelasan bab, atau cari data spesifik.</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )

if uploaded_file:
    with st.sidebar:
        st.divider()
        st.subheader("📋 Dokumen Aktif")
        st.write(f"**Nama:** {uploaded_file.name}")
        st.write(f"**Ukuran:** {round(uploaded_file.size / 1024, 2)} KB")

    st.success(f"Dokumen **{uploaded_file.name}** berhasil dipahami oleh sistem!")

    # Processing PDF
    @st.cache_resource(show_spinner="⚙️ Membaca dan menganalisis struktur dokumen...")
    def process_pdf(file_bytes):
        with open("temp.pdf", "wb") as f:
            f.write(file_bytes)

        loader = PyPDFLoader("temp.pdf")
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        return vectorstore.as_retriever(search_kwargs={"k": 3})

    retriever = process_pdf(uploaded_file.getvalue())

    # 6. Interactive Chat Interface
    st.divider()
    st.markdown("### 💬 Obrolan Dokumen")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Halo! Dokumen kamu sudah siap dibahas. Ingin saya buatkan ringkasan utamanya?"}
        ]

    # Render Messages
    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Quick Prompts / Tombol Bantuan Interaktif
    st.markdown("**💡 Contoh pertanyaan cepat:**")
    col1, col2, col3 = st.columns(3)
    quick_input = None
    if col1.button("Rangkum isi dokumen"):
        quick_input = "Tolong buatkan ringkasan poin-poin utama dari dokumen ini."
    if col2.button("Apa kesimpulannya?"):
        quick_input = "Apa kesimpulan utama yang disampaikan dalam dokumen ini?"
    if col3.button("Apa poin pentingnya?"):
        quick_input = "Sebutkan 3-5 poin paling penting yang ada di dokumen ini."

    user_query = st.chat_input("Tulis pertanyaan kamu di sini...") or quick_input

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Menyusun jawaban dari dokumen..."):
                try:
                    relevant_docs = retriever.invoke(user_query)
                    context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

                    llm = ChatGroq(
                        groq_api_key=GROQ_API_KEY, 
                        model_name="openai/gpt-oss-120b"
                    )
                    
                    system_prompt = (
                        "Kamu adalah asisten profesional yang ramah dan cerdas. Jawab pertanyaan pengguna berdasarkan konteks dokumen berikut.\n"
                        "Gunakan format Markdown yang rapi (seperti poin-poin atau cetak tebal) agar mudah dibaca.\n"
                        "Jika jawaban tidak ada dalam dokumen, katakan secara jujur bahwa informasi tersebut tidak ditemukan.\n\n"
                        "Konteks Dokumen:\n{context}"
                    )
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", system_prompt),
                        ("human", "{input}"),
                    ])

                    formatted_prompt = prompt.format_messages(context=context_text, input=user_query)
                    response = llm.invoke(formatted_prompt)
                    answer = response.content

                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")