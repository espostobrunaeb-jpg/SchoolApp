import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64
from PIL import Image

# =========================================================
# CONFIG PAGINA
# =========================================================

st.set_page_config(
    page_title="OmniScience 3D Studio Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE
# =========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "tema_scelto" not in st.session_state:
    st.session_state.tema_scelto = "Modalità Scura (Consigliata)"

# Persistenza contenuti TAB
if "spiegazione" not in st.session_state:
    st.session_state.spiegazione = ""

if "uda" not in st.session_state:
    st.session_state.uda = ""

if "compito_realta" not in st.session_state:
    st.session_state.compito_realta = ""

if "inclusione" not in st.session_state:
    st.session_state.inclusione = ""

if "quiz" not in st.session_state:
    st.session_state.quiz = ""

if "didascalie" not in st.session_state:
    st.session_state.didascalie = {}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## ⚙️ REGIA DOCENTE")

tema = st.sidebar.selectbox(
    "🎨 Tema Visivo:",
    ["Modalità Scura (Consigliata)", "Modalità Chiara"]
)

st.session_state.tema_scelto = tema

api_key = st.sidebar.text_input(
    "Gemini API Key:",
    type="password"
)

modello_gemini = st.sidebar.selectbox(
    "🤖 Modello AI:",
    [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ],
    index=0
)

with st.sidebar.expander("🔑 Come ottenere una API Key gratuita"):
    st.markdown("""
    1. Vai su Google AI Studio  
    2. Accedi con Google  
    3. Clicca "Get API Key"  
    4. Crea una nuova chiave API  
    """)

st.sidebar.markdown("---")

st.sidebar.markdown("### 🏛️ CONTESTO ISTITUZIONALE")

scuola_tipo = st.sidebar.selectbox(
    "Indirizzo di Studi:",
    [
        "Scuola Primaria (Elementari)",
        "Scuola Secondaria I Grado (Medie)",
        "Liceo (Biennio)",
        "Liceo (Triennio)",
        "Istituto Tecnico (Biennio)",
        "Istituto Tecnico (Triennio)",
        "Istituto Professionale (Biennio)",
        "Istituto Professionale (Triennio)",
        "Università"
    ],
    index=3
)

profilo = st.sidebar.selectbox(
    "Profilo Normativo (MIUR):",
    [
        "Standard (Nessun PDP/PEI)",
        "DSA (Legge 170/2010 - PDP)",
        "BES (Dir. Min. 2012 - PDP)",
        "Sostegno (Legge 104/92 - PEI)"
    ]
)

# =========================================================
# CSS DARK MODE
# =========================================================

if "Scura" in st.session_state.tema_scelto:

    st.markdown("""
    <style>

    .stApp {
        background-color: #0d1117;
        color: white;
    }

    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    h1, h2, h3 {
        color: #7ee787 !important;
    }

    p, label, span, div {
        color: #f0f6fc;
    }

    input, textarea {
        background-color: #21262d !important;
        color: white !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #21262d !important;
        color: white !important;
    }

    .stButton > button {
        background-color: #238636 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold;
    }

    .stButton > button:hover {
        background-color: #2ea043 !important;
    }

    button[data-baseweb="tab"] {
        color: #8b949e !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #7ee787 !important;
        border-bottom: 3px solid #7ee787 !important;
    }

    section[data-testid="stFileUploaderDropzone"] {
        background-color: #161b22 !important;
        border: 2px dashed #30363d !important;
    }

    div[data-testid="stExpander"] details {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
    }

    div[data-testid="stChatMessage"] {
        background-color: #161b22 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }

    </style>
    """, unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.title("🧪 OmniScience 3D Studio Pro")

st.caption(
    "🔬 Laboratorio e Progettazione Didattica | ESPOSTO BRUNA Classe A050"
)

# =========================================================
# LAYOUT
# =========================================================

col_regia, col_main = st.columns([0.27, 0.73], gap="large")

# =========================================================
# COLONNA SINISTRA
# =========================================================

with col_regia:

    st.markdown("## ✍️ LEZIONE")

    argomento = st.text_input(
        "Oggetto Scientifico:",
        value="Mitosi e Meiosi"
    )

    st.markdown("---")

    st.markdown("## 📦 CARICA MODELLO 3D")

    file_3d = st.file_uploader(
        "1. Seleziona file .glb (Opzionale):",
        type=["glb"]
    )

    img_copertina = st.file_uploader(
        "2. Copertina Offline (Opzionale):",
        type=["jpg", "png", "jpeg"]
    )

    st.markdown("---")

    st.markdown("## 🖼️ GALLERIA IMMAGINI")

    immagini_lezione = st.file_uploader(
        "Puoi selezionare più file:",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True
    )

# =========================================================
# COLONNA PRINCIPALE
# =========================================================

with col_main:

    # =====================================================
    # VIEWER 3D
    # =====================================================

    st.markdown(f"## 🌐 VISUALIZZATORE: {argomento.upper()}")

    data_url_online = (
        "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
    )

    if file_3d:

        file_3d.seek(0)

        data_url_online = (
            f"data:model/gltf-binary;base64,"
            f"{base64.b64encode(file_3d.read()).decode()}"
        )

    html_3d = f"""
    <script type="module"
    src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js">
    </script>

    <model-viewer
        src="{data_url_online}"
        camera-controls
        auto-rotate
        style="
            width:100%;
            height:500px;
            background:#111;
            border-radius:12px;
        ">
    </model-viewer>
    """

    components.html(html_3d, height=520)

    # =====================================================
    # CHAT
    # =====================================================

    with st.expander("💬 Chat Interattiva con l'Oggetto"):

        for m in st.session_state.chat_history:

            st.chat_message(m["role"]).write(
                m["content"]
            )

        if prompt_chat := st.chat_input(
            "Chiedi qualcosa all'oggetto scientifico..."
        ):

            st.session_state.chat_history.append({
                "role": "user",
                "content": prompt_chat
            })

            if api_key:

                try:

                    client = genai.Client(api_key=api_key)

                    resp = client.models.generate_content(
                        model=modello_gemini,
                        contents=f"""
                        Rispondi in prima persona come:
                        {argomento}

                        Target:
                        {scuola_tipo}

                        Profilo:
                        {profilo}

                        Domanda:
                        {prompt_chat}
                        """
                    )

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": resp.text
                    })

                    st.rerun()

                except Exception as e:

                    st.error(f"Errore AI: {e}")

    st.markdown("---")

    # =====================================================
    # TABS
    # =====================================================

    st.markdown("## 📚 PROGETTAZIONE E METODOLOGIA")

    tabs = st.tabs([
        "✨ Spiegazione",
        "🎯 Progettazione UDA",
        "🌍 Compito di Realtà",
        "🌈 Inclusione (PDP/PEI)",
        "📝 SuperQuiz 10",
        "🖼️ Infografica",
        "💾 Esporta"
    ])

    prompt_normativo = f"""
    Agisci come un Esperto Docente di Scienze A050.
    Target: {scuola_tipo}
    Profilo: {profilo}
    Usa terminologia MIUR.
    """

    # =====================================================
    # FUNZIONE AI
    # =====================================================

    def run_ai(prompt):

        if not api_key:
            return "⚠️ Inserisci API Key."

        try:

            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model=modello_gemini,
                contents=prompt
            )

            return response.text

        except Exception as e:

            return f"❌ Errore: {e}"

    # =====================================================
    # TAB 1
    # =====================================================

    with tabs[0]:

        if st.button("🚀 Genera Spiegazione Adattiva"):

            st.session_state.spiegazione = run_ai(
                f"""
                {prompt_normativo}

                Scrivi una spiegazione completa di:
                {argomento}

                Usa metafore potenti e linguaggio adatto al profilo:
                {profilo}
                """
            )

        if st.session_state.spiegazione:

            st.markdown(
                st.session_state.spiegazione
            )

    # =====================================================
    # TAB 2
    # =====================================================

    with tabs[1]:

        if st.button("🎯 Genera Progettazione UDA"):

            st.session_state.uda = run_ai(
                f"""
                {prompt_normativo}

                Crea una UDA completa per:
                {argomento}

                Includi:
                - Prerequisiti
                - Obiettivi
                - Competenze
                - Attività
                - Valutazione
                """
            )

        if st.session_state.uda:

            st.markdown(
                st.session_state.uda
            )

    # =====================================================
    # TAB 3
    # =====================================================

    with tabs[2]:

        if st.button("🌍 Progetta Compito di Realtà"):

            st.session_state.compito_realta = run_ai(
                f"""
                {prompt_normativo}

                Crea un Compito di Realtà per:
                {argomento}

                Includi:
                - Scenario reale
                - Ruoli
                - Fasi
                - Prodotto finale
                - Rubrica valutativa
                """
            )

        if st.session_state.compito_realta:

            st.markdown(
                st.session_state.compito_realta
            )

    # =====================================================
    # TAB 4
    # =====================================================

    with tabs[3]:

        if st.button("🌈 Genera Piano Inclusivo"):

            st.session_state.inclusione = run_ai(
                f"""
                {prompt_normativo}

                Crea un piano inclusivo per:
                {argomento}

                Includi:
                - Obiettivi minimi
                - Strumenti compensativi
                - Misure dispensative
                - Schema semplificato
                """
            )

        if st.session_state.inclusione:

            st.markdown(
                st.session_state.inclusione
            )

    # =====================================================
    # TAB 5
    # =====================================================

    with tabs[4]:

        if st.button("📝 Genera Quiz e Griglia"):

            st.session_state.quiz = run_ai(
                f"""
                {prompt_normativo}

                Crea:
                - 10 domande a risposta multipla
                - Soluzioni
                - Griglia valutativa MIUR
                """
            )

        if st.session_state.quiz:

            st.markdown(
                st.session_state.quiz
            )

    # =====================================================
    # TAB 6 INFOGRAFICA
    # =====================================================

    with tabs[5]:

        st.markdown("### 🖼️ Costruisci l'Infografica")

        if immagini_lezione:

            for idx, img_file in enumerate(immagini_lezione):

                img = Image.open(img_file)

                col1, col2 = st.columns([1, 2])

                with col1:

                    st.image(
                        img,
                        use_container_width=True
                    )

                with col2:

                    st.session_state.didascalie[
                        img_file.name
                    ] = st.text_area(
                        f"Didascalia immagine {idx+1}",
                        value=st.session_state.didascalie.get(
                            img_file.name,
                            ""
                        ),
                        key=f"desc_{img_file.name}",
                        height=150
                    )

                st.markdown("---")

        else:

            st.info(
                "Carica immagini nella sidebar."
            )

    # =====================================================
    # TAB EXPORT
    # =====================================================

    with tabs[6]:

        st.markdown("### 💾 Esporta Lezione")

        if st.button("📦 Scarica HTML"):

            html_content = f"""
            <html>
            <head>
                <title>{argomento}</title>
            </head>
            <body style='font-family:Arial;padding:40px;'>

                <h1>{argomento}</h1>

                <h2>Spiegazione</h2>
                {st.session_state.spiegazione}

                <h2>UDA</h2>
                {st.session_state.uda}

                <h2>Compito di Realtà</h2>
                {st.session_state.compito_realta}

                <h2>Inclusione</h2>
                {st.session_state.inclusione}

                <h2>Quiz</h2>
                {st.session_state.quiz}

            </body>
            </html>
            """

            st.download_button(
                "⬇️ Download HTML",
                html_content,
                file_name=f"{argomento}.html",
                mime="text/html"
            )
