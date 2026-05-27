```python
import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64
from PIL import Image
import io

# 1. CONFIGURAZIONE INTERFACCIA
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

# PERSISTENZA TAB
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

# --- BARRA LATERALE: REGIA DOCENTE ---
st.sidebar.markdown("## ⚙️ REGIA DOCENTE")

tema = st.sidebar.selectbox(
    "🎨 Tema Visivo:",
    ["Modalità Scura (Consigliata)", "Modalità Chiara"],
    key="tema_selector"
)

st.session_state.tema_scelto = tema

api_key = st.sidebar.text_input(
    "Gemini API Key:",
    type="password"
)

# SCELTA DEL MODELLO
modello_gemini = st.sidebar.selectbox(
    "🤖 Modello AI:",
    [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ],
    index=0,
    help="Scegli la potenza dell'IA."
)

# GUIDA PER L'API KEY
with st.sidebar.expander("🔑 Come ottenere una API Key gratuita"):
    st.markdown("""
    1. Vai su Google AI Studio
    2. Fai login con Google
    3. Clicca "Get API key"
    4. Crea una nuova API key
    """)

# --- CONTESTO NORMATIVO ---
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
# CSS
# =========================================================

if st.session_state.tema_scelto == "Modalità Scura (Consigliata)":

    st.markdown("""
        <style>

        .stApp {
            background-color: #0f0f0f !important;
            color: #ffffff !important;
        }

        h1, h2, h3 {
            color: #00d4aa !important;
        }

        .stButton>button {
            background-color: #1f1f1f !important;
            color: #ffffff !important;
            border: 1px solid #333 !important;
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
        }

        .stButton>button:hover {
            background-color: #00d4aa !important;
            color: #0f0f0f !important;
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

col_regia, col_main = st.columns([0.27, 0.73], gap="large")

# =========================================================
# COLONNA SINISTRA
# =========================================================

with col_regia:

    st.markdown("### ✍️ LEZIONE")

    argomento = st.text_input(
        "Oggetto Scientifico:",
        value="Mitosi e Meiosi"
    )

    st.markdown("---")

    st.markdown("### 📦 CARICA MODELLO 3D")

    file_3d = st.file_uploader(
        "1. Seleziona file .glb (Opzionale):",
        type=["glb"]
    )

    img_copertina = st.file_uploader(
        "2. Copertina Offline (Opzionale):",
        type=["jpg", "png", "jpeg"]
    )

    st.markdown("---")

    st.markdown("### 🖼️ GALLERIA IMMAGINI")

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

    html_3d = f'''
    <script type="module"
    src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>

    <model-viewer
        src="{data_url_online}"
        camera-controls
        auto-rotate
        style="width: 100%;
               height: 450px;
               background-color: #111111;
               border-radius: 12px;">
    </model-viewer>
    '''

    components.html(html_3d, height=460)

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

                client = genai.Client(api_key=api_key)

                resp = client.models.generate_content(
                    model=modello_gemini,
                    contents=f"""
                    Rispondi in prima persona come:
                    '{argomento}'

                    parlando a uno studente di:
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
    Agisci come un Esperto Docente di Scienze (A050) italiano.
    Target: {scuola_tipo}.
    Profilo: {profilo}.
    Usa terminologia MIUR.
    """

    # =====================================================
    # FUNZIONE AI
    # =====================================================

    def run_ai(p):

        if not api_key:
            return "⚠️ Inserisci API Key nella barra laterale."

        try:

            client = genai.Client(api_key=api_key)

            return client.models.generate_content(
                model=modello_gemini,
                contents=p
            ).text

        except Exception as e:

            return f"❌ Errore tecnico: {e}"

    # =====================================================
    # TAB 1
    # =====================================================

    with tabs[0]:

        if st.button("🚀 Genera Spiegazione Adattiva"):

            st.session_state.spiegazione = run_ai(
                f"{prompt_normativo} "
                f"Scrivi la spiegazione di '{argomento}'. "
                f"Inizia con una metafora potente. "
                f"Adatta rigorosamente linguaggio e formattazione "
                f"al profilo {profilo}."
            )

        if st.session_state.spiegazione:
            st.markdown(st.session_state.spiegazione)

    # =====================================================
    # TAB 2
    # =====================================================

    with tabs[1]:

        if st.button("🎯 Genera Progettazione UDA"):

            st.session_state.uda = run_ai(
                f"{prompt_normativo} "
                f"Struttura l'UDA per '{argomento}': "
                f"1. Prerequisiti, "
                f"2. Obiettivi (Conoscenze/Abilità), "
                f"3. Competenze chiave europee."
            )

        if st.session_state.uda:
            st.markdown(st.session_state.uda)

    # =====================================================
    # TAB 3
    # =====================================================

    with tabs[2]:

        if st.button("🌍 Progetta Compito di Realtà"):

            st.session_state.compito_realta = run_ai(
                f"{prompt_normativo} "
                f"Crea un Compito di Realtà su '{argomento}'. "
                f"Includi: Scenario reale, "
                f"Ruolo studenti, "
                f"Prodotto finale, "
                f"Fasi e Criteri di valutazione."
            )

        if st.session_state.compito_realta:
            st.markdown(st.session_state.compito_realta)

    # =====================================================
    # TAB 4
    # =====================================================

    with tabs[3]:

        if st.button("🌈 Genera Piano Inclusivo"):

            st.session_state.inclusione = run_ai(
                f"{prompt_normativo} "
                f"Definisci per '{argomento}': "
                f"Obiettivi minimi, "
                f"Strumenti compensativi, "
                f"Misure dispensative "
                f"e uno schema testuale semplificato."
            )

        if st.session_state.inclusione:
            st.markdown(st.session_state.inclusione)

    # =====================================================
    # TAB 5
    # =====================================================

    with tabs[4]:

        if st.button("📝 Genera Quiz (10 Domande) e Griglia"):

            st.session_state.quiz = run_ai(
                f"{prompt_normativo} "
                f"Crea un test di 10 domande "
                f"a risposta multipla su '{argomento}' "
                f"e una griglia valutativa MIUR "
                f"a 4 livelli alla fine."
            )

        if st.session_state.quiz:
            st.markdown(st.session_state.quiz)

    # =====================================================
    # TAB 6 INFOGRAFICA
    # =====================================================

    didascalie = st.session_state.didascalie

    with tabs[5]:

        st.markdown("### 🖼️ Costruisci l'Infografica")

        if immagini_lezione:

            for idx, img_file in enumerate(immagini_lezione):

                img = Image.open(img_file)

                col_img, col_text = st.columns(
                    [1, 2],
                    gap="large"
                )

                with col_img:

                    st.image(
                        img,
                        use_container_width=True
                    )

                with col_text:

                    didascalie[img_file.name] = st.text_area(
                        f"Spiegazione per immagine {idx+1}:",
                        value=didascalie.get(
                            img_file.name,
                            ""
                        ),
                        key=f"desc_{img_file.name}",
                        height=150
                    )

                st.markdown("---")

        else:

            st.info(
                "💡 Carica immagini nella barra laterale."
            )

    # =====================================================
    # TAB EXPORT
    # =====================================================

    with tabs[6]:

        st.markdown("### 💾 Esporta Lezione Interattiva")

        if st.button("📦 Scarica File HTML"):

            fallback_html = """
            <div style='padding:50px;
                        background:#e9ecef;
                        text-align:center;
                        border-radius:12px;'>

                ⚠️ Offline.
                Collegati a Internet per il modello 3D.

            </div>
            """

            if img_copertina:

                img_copertina.seek(0)

                b64_cover = base64.b64encode(
                    img_copertina.read()
                ).decode()

                fallback_html = f"""
                <img
                    src='data:image/png;base64,{b64_cover}'
                    style='width:100%;
                           border-radius:12px;'>
                """

            html_images = ""

            if immagini_lezione:

                for img_file in immagini_lezione:

                    img_file.seek(0)

                    b64 = base64.b64encode(
                        img_file.read()
                    ).decode()

                    desc = didascalie.get(
                        img_file.name,
                        ""
                    )

                    html_images += f"""
                    <div style='margin-bottom:40px;'>

                        <img
                            src='data:image/png;base64,{b64}'
                            style='max-width:100%;
                                   border-radius:12px;'>

                        <div style='margin-top:15px;
                                    padding:15px;
                                    background:#f5f5f5;
                                    border-left:5px solid #00d4aa;'>

                            {desc}

                        </div>

                    </div>
                    """

            template_html = f"""
            <html>

            <head>

                <title>{argomento}</title>

                <script type="module"
                src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>

                <style>

                    body {{
                        font-family: Arial;
                        background:#f0f4f8;
                        padding:40px;
                    }}

                    .container {{
                        max-width:1000px;
                        margin:auto;
                        background:white;
                        padding:40px;
                        border-radius:16px;
                    }}

                    h1 {{
                        color:#007a60;
                    }}

                    model-viewer {{
                        width:100%;
                        height:500px;
                        background:#111;
                        border-radius:12px;
                    }}

                </style>

            </head>

            <body>

                <div class="container">

                    <h1>{argomento}</h1>

                    <p>
                        <strong>Scuola:</strong>
                        {scuola_tipo}

                        <br>

                        <strong>Profilo:</strong>
                        {profilo}
                    </p>

                    <div id="offline">

                        {fallback_html}

                    </div>

                    <div id="online"
                         style="display:none;">

                        <model-viewer
                            src="{data_url_online}"
                            camera-controls
                            auto-rotate>
                        </model-viewer>

                    </div>

                    <hr>

                    <h2>📚 Spiegazione</h2>
                    {st.session_state.spiegazione}

                    <h2>🎯 UDA</h2>
                    {st.session_state.uda}

                    <h2>🌍 Compito di Realtà</h2>
                    {st.session_state.compito_realta}

                    <h2>🌈 Inclusione</h2>
                    {st.session_state.inclusione}

                    <h2>📝 Quiz</h2>
                    {st.session_state.quiz}

                    <h2>🖼️ Galleria</h2>

                    {html_images}

                </div>

                <script>

                    function checkConnection() {{

                        if (navigator.onLine) {{

                            document.getElementById(
                                "offline"
                            ).style.display = "none";

                            document.getElementById(
                                "online"
                            ).style.display = "block";

                        }}

                    }}

                    checkConnection();

                </script>

            </body>

            </html>
            """

            st.download_button(
                "⬇️ Scarica HTML",
                template_html,
                file_name=f"Lezione_{argomento}.html",
                mime="text/html"
            )
```
