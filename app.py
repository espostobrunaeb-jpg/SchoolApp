```python
import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64
from PIL import Image

# =========================================================
# CONFIGURAZIONE PAGINA
# =========================================================

st.set_page_config(
    page_title="OmniScience 3D Studio Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "chat_history": [],
    "tema_scelto": "Modalità Scura (Consigliata)",

    # OUTPUT AI
    "spiegazione": "",
    "uda": "",
    "compito_realta": "",
    "inclusione": "",
    "quiz": "",

    # INFOGRAFICA
    "didascalie": {}
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

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
    1. Vai su https://aistudio.google.com/
    2. Accedi con Google
    3. Clicca "Get API key"
    4. Crea una nuova API key
    """)

# =========================================================
# CONTESTO ISTITUZIONALE
# =========================================================

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
    "Profilo Normativo:",
    [
        "Standard",
        "DSA",
        "BES",
        "Sostegno"
    ]
)

# =========================================================
# CSS
# =========================================================

if "Scura" in st.session_state.tema_scelto:

    st.markdown("""
    <style>

    .stApp {
        background-color: #0f0f0f;
        color: white;
    }

    h1,h2,h3 {
        color: #00d4aa !important;
    }

    .stButton button {
        background-color: #1f1f1f !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid #333 !important;
    }

    .stButton button:hover {
        background-color: #00d4aa !important;
        color: black !important;
    }

    textarea, input {
        color: white !important;
    }

    </style>
    """, unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.title("🧪 OmniScience 3D Studio Pro")

st.caption(
    "🔬 Laboratorio e Progettazione Didattica"
)

# =========================================================
# LAYOUT
# =========================================================

col_regia, col_main = st.columns([0.28, 0.72])

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

    st.markdown("### 📦 MODELLO 3D")

    file_3d = st.file_uploader(
        "Carica file .glb",
        type=["glb"]
    )

    img_copertina = st.file_uploader(
        "Copertina offline",
        type=["jpg", "png", "jpeg"]
    )

    st.markdown("---")

    st.markdown("### 🖼️ GALLERIA")

    immagini_lezione = st.file_uploader(
        "Carica immagini",
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

    st.markdown(f"## 🌐 {argomento.upper()}")

    data_url_online = (
        "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
    )

    if file_3d:

        file_3d.seek(0)

        data_url_online = (
            "data:model/gltf-binary;base64,"
            + base64.b64encode(file_3d.read()).decode()
        )

    html_3d = f"""
    <script type="module"
    src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>

    <model-viewer
        src="{data_url_online}"
        camera-controls
        auto-rotate
        style="width:100%;height:450px;background:#111;border-radius:12px;">
    </model-viewer>
    """

    components.html(html_3d, height=460)

    # =====================================================
    # CHAT
    # =====================================================

    with st.expander("💬 Chat Interattiva"):

        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt_chat := st.chat_input("Fai una domanda..."):

            st.session_state.chat_history.append({
                "role": "user",
                "content": prompt_chat
            })

            if api_key:

                client = genai.Client(api_key=api_key)

                response = client.models.generate_content(
                    model=modello_gemini,
                    contents=f"""
                    Rispondi come se fossi:
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
                    "content": response.text
                })

                st.rerun()

    st.markdown("---")

    # =====================================================
    # FUNZIONE AI
    # =====================================================

    prompt_normativo = f"""
    Agisci come docente esperto di Scienze.
    Target: {scuola_tipo}
    Profilo: {profilo}
    """

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
    # TABS
    # =====================================================

    tabs = st.tabs([
        "✨ Spiegazione",
        "🎯 UDA",
        "🌍 Compito di Realtà",
        "🌈 Inclusione",
        "📝 Quiz",
        "🖼️ Infografica",
        "💾 Esporta"
    ])

    # =====================================================
    # TAB 1
    # =====================================================

    with tabs[0]:

        if st.button(
            "🚀 Genera Spiegazione",
            key="btn_spiegazione"
        ):

            st.session_state.spiegazione = run_ai(
                f"""
                {prompt_normativo}

                Scrivi una spiegazione completa di:
                {argomento}
                """
            )

        if st.session_state.spiegazione:
            st.markdown(st.session_state.spiegazione)

    # =====================================================
    # TAB 2
    # =====================================================

    with tabs[1]:

        if st.button(
            "🎯 Genera UDA",
            key="btn_uda"
        ):

            st.session_state.uda = run_ai(
                f"""
                {prompt_normativo}

                Crea una UDA completa su:
                {argomento}
                """
            )

        if st.session_state.uda:
            st.markdown(st.session_state.uda)

    # =====================================================
    # TAB 3
    # =====================================================

    with tabs[2]:

        if st.button(
            "🌍 Genera Compito",
            key="btn_compito"
        ):

            st.session_state.compito_realta = run_ai(
                f"""
                {prompt_normativo}

                Crea un compito di realtà su:
                {argomento}
                """
            )

        if st.session_state.compito_realta:
            st.markdown(st.session_state.compito_realta)

    # =====================================================
    # TAB 4
    # =====================================================

    with tabs[3]:

        if st.button(
            "🌈 Genera Inclusione",
            key="btn_inclusione"
        ):

            st.session_state.inclusione = run_ai(
                f"""
                {prompt_normativo}

                Crea strumenti inclusivi per:
                {argomento}
                """
            )

        if st.session_state.inclusione:
            st.markdown(st.session_state.inclusione)

    # =====================================================
    # TAB 5
    # =====================================================

    with tabs[4]:

        if st.button(
            "📝 Genera Quiz",
            key="btn_quiz"
        ):

            st.session_state.quiz = run_ai(
                f"""
                {prompt_normativo}

                Genera 10 domande quiz su:
                {argomento}
                """
            )

        if st.session_state.quiz:
            st.markdown(st.session_state.quiz)

    # =====================================================
    # TAB 6 INFOGRAFICA
    # =====================================================

    with tabs[5]:

        st.markdown("### 🖼️ Infografica")

        if immagini_lezione:

            for idx, img_file in enumerate(immagini_lezione):

                img = Image.open(img_file)

                col_img, col_text = st.columns([1, 2])

                with col_img:

                    st.image(
                        img,
                        use_container_width=True
                    )

                with col_text:

                    key_desc = f"desc_{img_file.name}"

                    valore = st.session_state.didascalie.get(
                        img_file.name,
                        ""
                    )

                    nuova_desc = st.text_area(
                        f"Didascalia immagine {idx+1}",
                        value=valore,
                        key=key_desc,
                        height=150
                    )

                    st.session_state.didascalie[
                        img_file.name
                    ] = nuova_desc

                st.markdown("---")

        else:

            st.info(
                "Carica immagini dalla sidebar."
            )

    # =====================================================
    # TAB 7 EXPORT
    # =====================================================

    with tabs[6]:

        st.markdown("### 💾 Esporta Lezione")

        if st.button(
            "📦 Genera HTML",
            key="btn_export"
        ):

            fallback_html = """
            <div style='padding:40px;
                        background:#e9ecef;
                        border-radius:12px;
                        text-align:center;'>

                ⚠️ Offline: collega internet per il 3D.

            </div>
            """

            # =================================================
            # COPERTINA OFFLINE
            # =================================================

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

            # =================================================
            # GALLERIA
            # =================================================

            html_images = ""

            if immagini_lezione:

                for img_file in immagini_lezione:

                    img_file.seek(0)

                    b64 = base64.b64encode(
                        img_file.read()
                    ).decode()

                    desc = st.session_state.didascalie.get(
                        img_file.name,
                        ""
                    )

                    html_images += f"""
                    <div style='margin-bottom:40px;'>

                        <img
                            src='data:image/png;base64,{b64}'
                            style='width:100%;
                                   border-radius:12px;'>

                        <div style='padding:15px;
                                    background:#f5f5f5;
                                    border-left:5px solid #00d4aa;
                                    margin-top:10px;'>

                            {desc}

                        </div>

                    </div>
                    """

            # =================================================
            # HTML FINALE
            # =================================================

            html_finale = f"""
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
                html_finale,
                file_name=f"{argomento}.html",
                mime="text/html"
            )
```
