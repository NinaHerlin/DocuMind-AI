# DocuMind AI

DocuMind AI adalah aplikasi Streamlit untuk mengobrol dengan dokumen PDF. Unggah dokumen, lalu minta ringkasan, kesimpulan, atau jawaban atas pertanyaan spesifik berdasarkan isinya.

## Fitur

- Mengunggah dan membaca dokumen PDF.
- Membuat indeks pencarian semantik dari teks dokumen.
- Menjawab pertanyaan menggunakan konteks yang ditemukan dalam PDF.
- Menyediakan pertanyaan cepat untuk ringkasan, kesimpulan, dan poin penting.
- Menggunakan antarmuka berbahasa Indonesia dengan tema terang.

## Teknologi

- Streamlit untuk antarmuka aplikasi.
- LangChain dan PyPDF untuk membaca serta memecah dokumen.
- Sentence Transformers (`all-MiniLM-L6-v2`) untuk embedding teks.
- Chroma untuk pencarian vektor.
- Groq API dengan model `openai/gpt-oss-120b` untuk menyusun jawaban.

## Persiapan

Pastikan Python dan koneksi internet tersedia. Dari PowerShell, jalankan perintah berikut di direktori proyek:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install streamlit python-dotenv langchain-community langchain-text-splitters langchain-groq sentence-transformers chromadb pypdf
```

Buat file `.env` di direktori yang sama dengan `app.py`, lalu masukkan API key Groq:

```dotenv
GROQ_API_KEY=masukkan_api_key_groq_di_sini
```

Jangan membagikan atau mengunggah API key ke repositori publik.

## Menjalankan Aplikasi

Pastikan virtual environment aktif dan terminal berada di direktori proyek. Jalankan:

```powershell
python -m streamlit run app.py
```

Buka alamat lokal yang ditampilkan Streamlit, biasanya <http://localhost:8501>. Terminal harus tetap terbuka selama aplikasi digunakan; tekan `Ctrl+C` untuk menghentikan server.

## Cara Kerja

1. Aplikasi membaca PDF yang diunggah.
2. Teks dipecah menjadi bagian berukuran 1.000 karakter dengan tumpang tindih 200 karakter.
3. Embedding dibuat dengan `all-MiniLM-L6-v2` dan disimpan dalam indeks Chroma untuk sesi aplikasi.
4. Untuk setiap pertanyaan, tiga bagian dokumen yang paling relevan dikirim sebagai konteks ke model Groq.
5. Jawaban ditampilkan di ruang obrolan. Jika informasinya tidak ditemukan dalam konteks, asisten diarahkan untuk menyatakannya.

Model embedding dapat diunduh saat pertama kali digunakan, sehingga proses awal mungkin memerlukan waktu dan koneksi internet.

## Privasi Dokumen

Pembacaan PDF, pembuatan embedding, dan pencarian vektor dilakukan oleh aplikasi. Namun, teks dari bagian dokumen yang relevan dikirim ke Groq API untuk menghasilkan jawaban. Jangan gunakan dokumen sensitif kecuali pengiriman data tersebut sesuai dengan kebijakan privasi dan kebutuhanmu. Aplikasi juga menulis salinan pemrosesan ke `temp.pdf` di direktori proyek.

## Struktur Proyek

```text
.
├── app.py                 # Logika aplikasi dan antarmuka Streamlit
├── style.css              # Styling antarmuka
├── .streamlit/
│   └── config.toml        # Tema Streamlit
└── .env                   # API key Groq; dibuat secara lokal
```
