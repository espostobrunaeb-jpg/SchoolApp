import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64
from PIL import Image
import io

# 1. CONFIGURAZIONE INTERFACCIA
st.set_page_config(page_title="OmniScience 3D Studio Pro", layout="wide", initial_sidebar_state="expanded")

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "tema_scelto" not in st.session_state: st.session_state.tema_scelto = "Modalità Scura (Consigliata)"

# --- BARRA LATERALE: REGIA DOCENTE ---
st.sidebar.markdown("## ⚙️ REGIA DOCENTE")
tema = st.sidebar.selectbox("🎨 Tema Visivo:", ["Modalità Scura (Consigliata)", "Modalità Chiara"], key="tema_selector")
st.session_state.tema_scelto = tema

api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# NUOVA SCELTA DEL MODELLO
modello_gemini = st.sidebar.selectbox("🤖 Modello AI:", [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
], index=0, help="Scegli la potenza dell'IA. 'Flash' è velocissimo, 'Pro' è più profondo nei ragionamenti complessi.")

# GUIDA PER L'API KEY
with st.sidebar.expander("🔑 Come ottenere una API Key gratuita"):
    st.markdown("""
    1. Vai su [Google AI Studio](https://aistudio.google.com/).
    2. Fai l'accesso con il tuo **account Google**.
    3. Clicca su **"Get API key"** -> **"Create API key"**.
    4. Copia la chiave e incollala qui sopra.
    """)

# --- CONTESTO NORMATIVO E ISTITUZIONALE ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏛️ CONTESTO ISTITUZIONALE")

scuola_tipo = st.sidebar.selectbox("Indirizzo di Studi:", [
    "Scuola Primaria (Elementari)", 
    "Scuola Secondaria I Grado (Medie)", 
    "Liceo (Biennio)",
    "Liceo (Triennio)",
    "Istituto Tecnico (Biennio)", 
    "Istituto Tecnico (Triennio)",
    "Istituto Professionale (Biennio)",
    "Istituto Professionale (Triennio)",
    "Università"
], index=3)

profilo = st.sidebar.selectbox("Profilo Normativo (MIUR):", [
    "Classe Standard (Nessun PDP/PEI)", 
    "DSA (Legge 170/2010 - PDP)", 
    "BES (Dir. Min. 2012 - PDP)", 
    "Sostegno (Legge 104/92 - PEI)"
])

# --- INIEZIONE CSS BLINDATA ---
if st.session_state.tema_scelto == "Modalità Scura (Consigliata)":
    st.markdown("""
        <style>
        .stApp, header[data-testid="stHeader"] { background-color: #0f0f0f !important; color: #ffffff !important; }
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background-color: #161616 !important; border-right: 1px solid #2d2d2d !important; }
        section[data-testid="stSidebar"] * { color: #ffffff !important; }
        div[data-testid="stColumn"] { background-color: #161616 !important; border-radius: 12px; padding: 20px; border: 1px solid #2d2d2d !important; }
        div[data-testid="stColumn"] p, div[data-testid="stColumn"] span, div[data-testid="stColumn"] label { color: #ffffff !important; }
        h1, h2, h3 { color: #00d4aa !important; font-weight: 600; }
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div { background-color: #1f1f1f !important; border-color: #333333 !important; color: #ffffff !important; }
        input, textarea { color: #ffffff !important; background-color: transparent !important; }
        div[data-baseweb="popover"] > div, ul[role="listbox"], li[role="option"] { background-color: #1f1f1f !important; color: #ffffff !important; }
        li[role="option"]:hover, li[role="option"]:focus, li[aria-selected="true"] { background-color: #00d4aa !important; color: #0f0f0f !important; }
        div[data-testid="stFileUploader"] section, div[data-testid="stFileUploaderDropzone"] { background-color: #1f1f1f !important; color: #ffffff !important; border: 1px dashed #444 !important; }
        div[data-testid="stFileUploader"] span, div[data-testid="stFileUploader"] small, div[data-testid="stFileUploader"] label { color: #ffffff !important; }
        div[data-testid="stFileUploader"] button { background-color: #333333 !important; color: #ffffff !important; border: 1px solid #444444 !important; border-radius: 6px; font-weight: 500; }
        div[data-testid="stFileUploader"] button:hover { background-color: #00d4aa !important; color: #0f0f0f !important; border-color: #00d4aa !important; }
        div[data-testid="stExpander"] details { background-color: #1f1f1f !important; border: 1px solid #333 !important; border-radius: 8px; }
        div[data-testid="stExpander"] summary { background-color: #1f1f1f !important; color: #00d4aa !important; }
        div[data-testid="stExpander"] summary:hover { color: #ffffff !important; }
        div[data-testid="stExpander"] div { color: #e0e0e0 !important; }
        div[data-testid="stChatInput"] { background-color: transparent !important; }
        div[data-testid="stChatInput"] > div { background-color: #1f1f1f !important; border: 1px solid #333 !important; }
        div[data-testid="stChatInput"] textarea, div[data-testid="stChatInput"] input { color: #ffffff !important; background-color: transparent !important; }
        div[data-testid="stChatMessage"] { background-color: transparent !important; color: #ffffff !important; }
        div[data-testid="stChatMessage"] * { color: #ffffff !important; }
        .stButton>button { background-color: #1f1f1f !important; color: #ffffff !important; border: 1px solid #333 !important; border-radius: 8px; font-weight: 600; width: 100%; }
        .stButton>button:hover { background-color: #00d4aa !important; color: #0f0f0f !important; border-color: #00d4aa !important; }
        button[data-baseweb="tab"] { color: #8a94a6 !important; font-weight: 600 !important; font-size: 14px !important; background-color: transparent !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #00d4aa !important; border-bottom: 3px solid #00d4aa !important; }
        div[data-testid="stTooltipContent"] { background-color: #1f1f1f !important; color: #ffffff !important; border: 1px solid #333 !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp, header[data-testid="stHeader"] { background-color: #f8f9fa !important; color: #212529 !important; }
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background-color: #e9ecef !important; border-right: 1px solid #dee2e6 !important; }
        section[data-testid="stSidebar"] * { color: #212529 !important; }
        div[data-testid="stColumn"] { background-color: #ffffff !important; border-radius: 12px; padding: 20px; border: 1px solid #dee2e6 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        div[data-testid="stColumn"] p, div[data-testid="stColumn"] span, div[data-testid="stColumn"] label { color: #212529 !important; }
        h1, h2, h3 { color: #007a60 !important; font-weight: 600; }
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div { background-color: #ffffff !important; border-color: #ced4da !important; color: #212529 !important; }
        input, textarea { color: #212529 !important; background-color: transparent !important; }
        div[data-baseweb="popover"] > div, ul[role="listbox"], li[role="option"] { background-color: #ffffff !important; color: #212529 !important; }
        li[role="option"]:hover, li[role="option"]:focus, li[aria-selected="true"] { background-color: #007a60 !important; color: #ffffff !important; }
        div[data-testid="stFileUploader"] section, div[data-testid="stFileUploaderDropzone"] { background-color: #ffffff !important; color: #212529 !important; border: 1px dashed #ced4da !important; }
        div[data-testid="stFileUploader"] span, div[data-testid="stFileUploader"] small, div[data-testid="stFileUploader"] label { color: #212529 !important; }
        div[data-testid="stFileUploader"] button { background-color: #e9ecef !important; color: #212529 !important; border: 1px solid #ced4da !important; border-radius: 6px; font-weight: 500; }
        div[data-testid="stFileUploader"] button:hover { background-color: #007a60 !important; color: #ffffff !important; border-color: #007a60 !important; }
        div[data-testid="stExpander"] details { background-color: #ffffff !important; border: 1px solid #ced4da !important; border-radius: 8px; }
        div[data-testid="stExpander"] summary { background-color: #ffffff !important; color: #007a60 !important; }
        div[data-testid="stExpander"] summary:hover { color: #212529 !important; }
        div[data-testid="stExpander"] div { color: #212529 !important; }
        div[data-testid="stChatInput"] { background-color: transparent !important; }
        div[data-testid="stChatInput"] > div { background-color: #ffffff !important; border: 1px solid #ced4da !important; }
        div[data-testid="stChatInput"] textarea, div[data-testid="stChatInput"] input { color: #212529 !important; background-color: transparent !important; }
        div[data-testid="stChatMessage"] { background-color: transparent !important; color: #212529 !important; }
        div[data-testid="stChatMessage"] * { color: #212529 !important; }
        .stButton>button { background-color: #ffffff !important; color: #212529 !important; border: 1px solid #ced4da !important; border-radius: 8px; font-weight: 600; width: 100%; }
        .stButton>button:hover { background-color: #007a60 !important; color: #ffffff !important; border-color: #007a60 !important; }
        button[data-baseweb="tab"] { color: #64748b !important; font-weight: 600 !important; font-size: 14px !important; background-color: transparent !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #007a60 !important; border-bottom: 3px solid #007a60 !important; }
        div[data-testid="stTooltipContent"] { background-color: #ffffff !important; color: #212529 !important; border: 1px solid #ced4da !important; }
        </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🧪 OmniScience 3D Studio Pro")
st.caption(f"🔬 *Laboratorio e Progettazione Didattica | ESPOSTO BRUNA Classe A050*")

col_regia, col_main = st.columns([0.27, 0.73], gap="large")

with col_regia:
    st.markdown("### ✍️ LEZIONE")
    argomento = st.text_input("Oggetto Scientifico:", value="Mitosi e Meiosi")
    
    st.markdown("---")
    st.markdown("### 📦 CARICA MODELLO 3D")
    file_3d = st.file_uploader("1. Seleziona file .glb (Opzionale):", type=["glb"])
    
    img_copertina = st.file_uploader("2. Copertina Offline (Opzionale):", type=["jpg", "png", "jpeg"], help="Immagine che verrà mostrata nell'esportazione se apri il file senza connessione internet.")
    
    with st.expander("🔍 Guida ai file .glb e Risorse Gratuite"):
        st.write("""
        I file **.glb** (chiamati anche gLTF binari) sono il formato standard per il 3D sul web.
        * 🪐 **Sketchfab:** Cerca in inglese. Filtro **"Downloadable"**.
        * 🏛️ **NASA 3D & Smithsonian:** (3d.si.edu).
        * 🤖 **Tripo3D (tripo3d.ai):** Genera modelli 3D con intelligenza artificiale.
        """)
    
    st.markdown("---")
    st.markdown("### 🖼️ GALLERIA IMMAGINI")
    st.caption("Carica immagini per l'infografica finale.")
    immagini_lezione = st.file_uploader("Puoi selezionare più file:", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

with col_main:
    # 1. VIEWPORT 3D
    st.markdown(f"## 🌐 VISUALIZZATORE: {argomento.upper()}")
    data_url_online = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
    if file_3d:
        file_3d.seek(0)
        data_url_online = f"data:model/gltf-binary;base64,{base64.b64encode(file_3d.read()).decode()}"
    
    bg_v = "#111111" if "Scura" in st.session_state.tema_scelto else "#ffffff"
    border_v = "#333333" if "Scura" in st.session_state.tema_scelto else "#ced4da"
    html_3d = f'<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script><model-viewer src="{data_url_online}" camera-controls auto-rotate style="width: 100%; height: 450px; background-color: {bg_v}; border: 1px solid {border_v}; border-radius: 12px;"></model-viewer>'
    components.html(html_3d, height=460)

    # 2. CHAT INTERATTIVA
    with st.expander("💬 Chat Interattiva con l'Oggetto (Simulazione Alunni)"):
        for m in st.session_state.chat_history: st.chat_message(m["role"]).write(m["content"])
        if prompt_chat := st.chat_input("Chiedi qualcosa all'oggetto scientifico..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt_chat})
            if api_key:
                client = genai.Client(api_key=api_key)
                # Qui usiamo il modello scelto dall'utente!
                resp = client.models.generate_content(model=modello_gemini, contents=f"Rispondi in prima persona come '{argomento}' parlando a un alunno di {scuola_tipo} (Profilo {profilo}). Domanda: {prompt_chat}")
                st.session_state.chat_history.append({"role": "assistant", "content": resp.text})
                st.rerun()

    st.markdown("---")
    
    # 3. DASHBOARD DIDATTICA
    st.markdown(f"## 📚 PROGETTAZIONE E METODOLOGIA")
    tabs = st.tabs(["✨ Spiegazione", "🎯 Progettazione UDA", "🌍 Compito di Realtà", "🌈 Inclusione (PDP/PEI)", "📝 SuperQuiz 10", "🖼️ Infografica", "💾 Esporta"])
    
    prompt_normativo = f"Agisci come un Esperto Docente di Scienze (A050) italiano. Target: {scuola_tipo}. Profilo: {profilo}. Usa terminologia MIUR (UDA, rubriche, competenze chiave)."
    
    def run_ai(p):
        if not api_key: return "⚠️ Inserisci API Key nella barra laterale."
        try:
            client = genai.Client(api_key=api_key)
            # Qui usiamo il modello scelto dall'utente!
            return client.models.generate_content(model=modello_gemini, contents=p).text
        except Exception as e: return f"❌ Errore tecnico: {e}"

    with tabs[0]:
        if st.button("🚀 Genera Spiegazione Adattiva"): 
            st.markdown(run_ai(f"{prompt_normativo} Scrivi la spiegazione di '{argomento}'. Inizia con una metafora potente. Adatta rigorosamente linguaggio e formattazione al profilo {profilo}."))

    with tabs[1]:
        if st.button("🎯 Genera Progettazione UDA"):
            st.markdown(run_ai(f"{prompt_normativo} Struttura l'UDA per '{argomento}': 1. Prerequisiti, 2. Obiettivi (Conoscenze/Abilità), 3. Competenze chiave europee."))

    with tabs[2]:
        if st.button("🌍 Progetta Compito di Realtà"):
            st.markdown(run_ai(f"{prompt_normativo} Crea un Compito di Realtà su '{argomento}'. Includi: Scenario reale, Ruolo studenti, Prodotto finale, Fasi e Criteri di valutazione."))

    with tabs[3]:
        if st.button("🌈 Genera Piano Inclusivo"):
            st.markdown(run_ai(f"{prompt_normativo} Definisci per '{argomento}': Obiettivi minimi, Strumenti compensativi, Misure dispensative e uno schema testuale semplificato."))

    with tabs[4]:
        if st.button("📝 Genera Quiz (10 Domande) e Griglia"):
            st.markdown(run_ai(f"{prompt_normativo} Crea un test di 10 domande a risposta multipla su '{argomento}' e una griglia valutativa MIUR a 4 livelli alla fine."))

    didascalie = {}
    with tabs[5]:
        st.markdown("### 🖼️ Costruisci l'Infografica della Lezione")
        if immagini_lezione:
            for idx, img_file in enumerate(immagini_lezione):
                img = Image.open(img_file)
                col_img, col_text = st.columns([1, 2], gap="large")
                with col_img: st.image(img, use_column_width=True)
                with col_text: didascalie[img_file.name] = st.text_area(f"Spiegazione per l'immagine {idx+1}:", key=f"desc_{img_file.name}", height=150)
                st.markdown("---")
        else:
            st.info("💡 Carica le immagini nella barra laterale per costruire l'infografica.")

    # TAB ESPORTAZIONE: LOGICA SMART ONLINE/OFFLINE
    with tabs[6]:
        st.markdown("### 💾 Esporta Lezione Interattiva (Smart Offline)")
        if st.button("📦 Scarica File HTML"):
            
            fallback_html = "<div style='padding: 50px; background: #e9ecef; color: #666; text-align: center; border-radius: 12px; border: 2px dashed #ccc; font-size: 1.2em;'>⚠️ Sei offline. Collegati a Internet per visualizzare il modello 3D interattivo.</div>"
            if img_copertina:
                img_copertina.seek(0)
                b64_cover = base64.b64encode(img_copertina.read()).decode()
                fallback_html = f"<img src='data:image/png;base64,{b64_cover}' style='width: 100%; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>"

            html_images = ""
            if immagini_lezione:
                html_images += "<h2 style='color:#007a60; border-bottom:2px solid #00d4aa; padding-bottom:10px; margin-top: 50px;'>🖼️ Galleria Scientifica</h2>"
                for img_file in immagini_lezione:
                    img_file.seek(0)
                    b64 = base64.b64encode(img_file.read()).decode()
                    desc = didascalie.get(img_file.name, "").replace("\n", "<br>")
                    html_images += f"""
                    <div style='margin-bottom: 40px; padding: 20px; border: 1px solid #ddd; border-radius: 12px; background: #fafafa; text-align: center;'>
                        <img src='data:image/png;base64,{b64}' style='max-width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                        <div style='margin-top: 15px; font-size: 18px; color: #444; text-align: left; line-height: 1.6; padding: 15px; background: #fff; border-left: 5px solid #00d4aa; border-radius: 4px;'>
                            {desc if desc else '<i>Nessuna didascalia fornita.</i>'}
                        </div>
                    </div>
                    """
            
            template_html = """
            <html>
            <head>
                <title>Lezione: __ARGOMENTO__</title>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; padding: 40px; background-color: #f0f4f8; color: #333; }
                    .container { max-width: 900px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
                    h1 { color: #007a60; text-align: center; font-size: 3em; margin-bottom: 10px; }
                    .info-box { background: #e9ecef; padding: 20px; border-radius: 8px; margin-bottom: 40px; font-size: 1.2em; text-align: center; }
                    #viewer-container { width: 100%; height: 500px; margin-bottom: 30px; display: flex; justify-content: center; align-items: center; }
                    model-viewer { width: 100%; height: 100%; background-color: #111; border-radius: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>__ARGOMENTO__</h1>
                    <div class="info-box">
                        <strong>Target:</strong> __SCUOLA_TIPO__ | <strong>Profilo:</strong> __PROFILO__
                    </div>
                    
                    <div id="offline-fallback">
                        __FALLBACK_HTML__
                    </div>
                    <div id="online-3d" style="display: none;">
                        <model-viewer src="__DATA_URL_ONLINE__" camera-controls auto-rotate></model-viewer>
                    </div>
                    
                    __HTML_IMAGES__
                </div>

                <script>
                    function checkConnection() {
                        if (navigator.onLine) {
                            document.getElementById('offline-fallback').style.display = 'none';
                            document.getElementById('online-3d').style.display = 'block';
                        } else {
                            document.getElementById('offline-fallback').style.display = 'block';
                            document.getElementById('online-3d').style.display = 'none';
                        }
                    }
                    window.addEventListener('online', checkConnection);
                    window.addEventListener('offline', checkConnection);
                    checkConnection(); // Esegui subito all'avvio
                </script>
                <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
            </body>
            </html>
            """
            
            lezione_html = template_html.replace("__ARGOMENTO__", argomento)
            lezione_html = lezione_html.replace("__SCUOLA_TIPO__", scuola_tipo)
            lezione_html = lezione_html.replace("__PROFILO__", profilo)
            lezione_html = lezione_html.replace("__FALLBACK_HTML__", fallback_html)
            lezione_html = lezione_html.replace("__DATA_URL_ONLINE__", data_url_online)
            lezione_html = lezione_html.replace("__HTML_IMAGES__", html_images)
            
            st.download_button("Scarica Lezione Smart (HTML)", lezione_html, file_name=f"Lezione_{argomento.replace(' ', '_')}.html", mime="text/html")
