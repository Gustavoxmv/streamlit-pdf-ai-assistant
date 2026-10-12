# Smart PDF Insights — Chat with your PDFs

![Status](https://img.shields.io/badge/status-active-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Framework](https://img.shields.io/badge/framework-Streamlit-red)

Turn any PDF into an instant Q&A assistant powered by OpenAI. **Smart PDF Insights** lets business teams and freelancers upload a document and immediately chat with it — extracting answers, key figures and insights without reading every page.

## Why Smart PDF Insights?

E-commerce operators, analysts and consultants waste hours manually searching through contracts, reports, invoices and product specifications. Smart PDF Insights eliminates that friction: upload a file, ask a question in plain English, and get a precise, context-aware answer in seconds.

- **Save time** — no more scanning long documents by hand.
- **Better decisions** — surface the exact facts, terms and numbers you need.
- **Zero setup** — bring your own OpenAI API key and start immediately.

## Features

- Modern, clean Streamlit interface with a wide layout.
- Upload PDFs and extract full text automatically (via PyPDF2).
- Instant document metrics: page count and approximate word count.
- Interactive chat (`st.chat_input` / `st.chat_message`) with streaming responses.
- Context-aware answers grounded only in your document (RAG-lite).
- Model selection: `gpt-4o-mini` (fast) or `gpt-4o` (most capable).
- Secure API key handling via sidebar, `.env`, or Streamlit secrets (show/hide toggle).
- Elegant error handling for invalid API keys and encrypted or empty PDFs.

## Tech stack

| Layer      | Technology                                  |
| ---------- | ------------------------------------------- |
| Frontend   | [Streamlit](https://streamlit.io)           |
| AI         | [OpenAI API](https://openai.com) (v1.0+)    |
| PDF parsing| [PyPDF2](https://pypi.org/project/PyPDF2/)  |
| Config     | [python-dotenv](https://pypi.org/project/python-dotenv/) |

## Installation (local)

1. **Clone the repository**

   ```bash
   git clone https://github.com/Gustavoxmv/streamlit-pdf-ai-assistant.git
   cd streamlit-pdf-ai-assistant
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set your API key**

   Copy the example file and add your key:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env`:

   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```

5. **Run the app**

   ```bash
   streamlit run app.py
   ```

   Open http://localhost:8501 in your browser.

## Deployment on Streamlit Cloud

1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in.
3. Click **New app**, select the repository and set the main file to `app.py`.
4. Under **Advanced settings → Secrets**, add:

   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```

5. Click **Deploy**. Your app will be live in minutes.

> Your API key is never stored in the repository — it is injected at runtime via `.env` or Streamlit secrets.

## Project structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Ignored files and secrets
└── README.md
```

## License

[MIT](LICENSE)

---

Developed by [Gustavoxmv](https://github.com/Gustavoxmv).
