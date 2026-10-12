import io
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader

load_dotenv()

st.set_page_config(
    page_title="Smart PDF Insights",
    page_icon=":material/article:",
    layout="wide",
)

MODEL_OPTIONS = {
    "gpt-4o-mini": "Fast and affordable — best for everyday document Q&A",
    "gpt-4o": "Most capable — ideal for complex reasoning over long documents",
}

MAX_CONTEXT_CHARS = 40_000

st.session_state.setdefault("messages", [])
st.session_state.setdefault("current_file", None)


@st.cache_data(show_spinner=False, max_entries=5)
def extract_pdf_text(file_bytes: bytes) -> tuple[str, int]:
    """Extract raw text and page count from an uploaded PDF."""
    reader = PdfReader(io.BytesIO(file_bytes))

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise ValueError(
                "This PDF is password-protected. Remove the password and upload it again."
            ) from exc
        if reader.is_encrypted:
            raise ValueError(
                "This PDF is password-protected. Remove the password and upload it again."
            )

    page_texts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(page_texts), len(reader.pages)


def resolve_api_key() -> str:
    """Prefer the sidebar input; fall back to st.secrets, then the .env file."""
    try:
        secret = st.secrets["OPENAI_API_KEY"]
        if secret:
            return secret
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY", "")


def build_system_prompt(context: str) -> str:
    return (
        "You are Smart PDF Insights, an AI assistant that answers business "
        "questions about an uploaded PDF document.\n"
        "Rules:\n"
        "- Answer using ONLY the information in the document context below.\n"
        "- If the answer is not in the context, say so clearly.\n"
        "- Be concise, professional and business-oriented.\n"
        "- Use bullet points when listing facts or figures.\n\n"
        f"Document context:\n'''\n{context}\n'''"
    )


def stream_response(client: OpenAI, model: str, messages: list[dict]):
    """Yield response text from the OpenAI chat completions streaming API."""
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        temperature=0.2,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.title("Smart PDF Insights", icon=":material/article:")
    st.caption("Turn any PDF into an instant Q&A assistant.")

    st.header("Configuration", icon=":material/settings:")

    default_key = resolve_api_key()
    show_key = st.toggle("Show API key", value=False)

    api_key = st.text_input(
        "OpenAI API key",
        type="default" if show_key else "password",
        value=default_key,
        placeholder="sk-...",
        help="Stored only in memory for this session. You can also set it in a "
        ".env file or Streamlit secrets.",
    )

    model_label = st.selectbox("Model", list(MODEL_OPTIONS.keys()))
    st.caption(MODEL_OPTIONS[model_label])

    if st.button("Clear conversation", icon=":material/delete:"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    with st.expander("How to use", icon=":material/help:"):
        st.markdown(
            "1. Enter your OpenAI API key.\n"
            "2. Upload a PDF document.\n"
            "3. Ask questions about its content in the chat below."
        )

    st.divider()
    st.caption("Built with Streamlit + OpenAI")
    st.caption("Developed by **Gustavoxmv**")

# --------------------------------------------------------------------------- #
# Main area
# --------------------------------------------------------------------------- #
st.title("Smart PDF Insights", icon=":material/article:")
st.subheader(
    "Chat with your PDFs. Extract answers, insights and key figures from any "
    "document in seconds — no more manual reading.",
)

uploaded_file = st.file_uploader(
    "Upload a PDF document",
    type=["pdf"],
    accept_multiple_files=False,
    help="The file is processed locally and never stored.",
)

if uploaded_file is None:
    st.info(
        "Upload a PDF to get started. Contracts, reports, invoices and product "
        "specs all work great.",
        icon=":material/upload_file:",
    )
    st.stop()

file_bytes = uploaded_file.getvalue()
file_id = (uploaded_file.name, uploaded_file.size)

if st.session_state.current_file != file_id:
    st.session_state.messages = []
    st.session_state.current_file = file_id

try:
    pdf_text, page_count = extract_pdf_text(file_bytes)
except ValueError as exc:
    st.error(str(exc), icon=":material/lock:")
    st.stop()
except Exception:
    st.error(
        "Could not read this PDF. The file may be corrupt or encrypted.",
        icon=":material/error:",
    )
    st.stop()

if not pdf_text.strip():
    st.warning(
        "No selectable text was found in this PDF. It is likely a scanned "
        "document or contains only images.",
        icon=":material/warning:",
    )
    st.stop()

word_count = len(pdf_text.split())
context = pdf_text[:MAX_CONTEXT_CHARS]
truncated = len(pdf_text) > MAX_CONTEXT_CHARS

col_name, col_pages, col_words = st.columns(3)
col_name.metric("Document", uploaded_file.name)
col_pages.metric("Pages", page_count)
col_words.metric("Words (approx.)", f"{word_count:,}")

if truncated:
    st.caption(
        "This document is large, so only the first part is used as context. "
        "Ask specific questions for the best results."
    )

st.divider()

# --------------------------------------------------------------------------- #
# Chat
# --------------------------------------------------------------------------- #
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(
    "Ask a question about your document...",
    submit_mode="disable",
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not api_key.strip():
        with st.chat_message("assistant"):
            st.error(
                "Please enter your OpenAI API key in the sidebar to continue.",
                icon=":material/key:",
            )
    else:
        with st.chat_message("assistant"):
            messages = (
                [{"role": "system", "content": build_system_prompt(context)}]
                + st.session_state.messages
            )
            try:
                client = OpenAI(api_key=api_key)
                response = st.write_stream(
                    stream_response(client, model_label, messages)
                )
            except Exception as exc:
                response = None
                if getattr(exc, "status_code", None) == 401:
                    st.error(
                        "Invalid OpenAI API key. Check the key in the sidebar "
                        "and try again.",
                        icon=":material/key_off:",
                    )
                else:
                    st.error(
                        f"Something went wrong while contacting OpenAI: {exc}",
                        icon=":material/error:",
                    )

        if response:
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
