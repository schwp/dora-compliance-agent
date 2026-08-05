import streamlit as st

from src.rag.embedding import VectorStore
from src.rag.generator import Generator
from src.rag.retriever import HybridRetriever

st.set_page_config(
    page_title="CSSF/DORA Compliance Assistant",
    page_icon="📋",
    layout="centered",
)

st.title("CSSF/DORA Compliance Assistant")
st.caption("Grounded answers with citations, from the CSSF circular corpus.")


@st.cache_resource(show_spinner="Connecting to the knowledge base…")
def load_pipeline():
    """
    Build the retriever and generator once.
    @st.cache_resource keeps them alive across Streamlit reruns.
    """
    store = VectorStore()
    retriever = HybridRetriever(store)
    generator = Generator()
    return retriever, generator


retriever, generator = load_pipeline()

with st.sidebar:
    st.header("About")
    st.markdown(
        "Ask questions about **CSSF circulars** implementing DORA "
        "(Digital Operational Resilience Act) for Luxembourg financial entities."
    )
    st.markdown("---")
    top_k = st.slider(
        "Sources to retrieve",
        min_value=2,
        max_value=8,
        value=4,
        help="How many circular chunks to ground the answer in.",
    )
    show_sources = st.toggle("Show retrieved sources", value=True)
    st.markdown("---")
    st.caption(
        "Answers are grounded only in the indexed circulars and cite their "
        "point numbers. This is a demo, not legal advice."
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for src in msg["sources"]:
                    st.markdown(f"**{src['citation']}**")
                    st.caption(
                        src["text"][:300] + ("…" if len(src["text"]) > 300 else "")
                    )

if question := st.chat_input("Ask about a CSSF circular…"):
    st.session_state.messages.append(
        {"role": "user", "content": question, "avatar": ":material/account_circle:"}
    )
    with st.chat_message("user", avatar=":material/account_circle:"):
        st.markdown(question)

    with st.chat_message("assistant", avatar=":material/cognition_2:"):
        with st.spinner("Thinking..."):
            chunks = retriever.search(question, top_k=top_k)

        if not chunks:
            answer_text = "I couldn't find anything relevant in the indexed circulars."
            st.markdown(answer_text)
            sources = []
        else:
            answer_text = st.write_stream(generator.stream(question, chunks))

            sources = [{"citation": c.citation, "text": c.text} for c in chunks]
            if show_sources:
                with st.expander("Sources"):
                    for c in chunks:
                        st.markdown(f"**{c.citation}**")
                        st.caption(c.text[:300] + ("…" if len(c.text) > 300 else ""))

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer_text,
            "sources": sources,
            "avatar": ":material/cognition_2:",
        }
    )
