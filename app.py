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
st.sidebar.markdown("## ⚙️ REGIA DOCENTE (A050)")
tema = st.sidebar.selectbox("🎨 Tema Visivo:", ["Modalità Scura (Consigliata)", "Modalità Chiara"], key="tema_selector")
st.session_state.tema_scelto = tema

api_key = st.sidebar.text_input("Gemini API Key:", type="password")

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
    "Liceo (Scientifico/Classico/Scienze Umane)", 
    "Istituto Tecnico (Settore Tecnologico)", 
    "Istituto Professionale",
    "Scuola Secondaria di I Grado"
])
profilo = st.sidebar.selectbox("Profilo Normativo (MIUR):", [
    "Classe Standard (Nessun PDP/PEI)", 
    "DSA (Legge 170/2010 - PDP)", 
    "BES (Dir. Min. 2012 - PDP)", 
    "Sostegno (Legge 104/92 - PEI)"
])

# --- INIEZIONE CSS COMPLETO E CORRETTO ---
if st.session_state.tema_scelto == "Modalità Scura (Consigliata)":
    st.markdown("""
        <style>
        /* Sfondo generale */
        .stApp, .stApp > header { background-color: #0f0f0f !important; color: #ffffff !important; }
        
        /* Barra laterale */
        section[data-testid="stSidebar"] { background-color: #161616 !important; border-right: 1px solid #2d2d2d !important; }
        section[data-testid="stSidebar"] * { color: #ffffff !important; }
        
        /* Colonne centrali */
        div[data-testid="stColumn"] { background-color: #161616 !important; border-radius: 12px; padding: 20px; border: 1px solid #2d2d2d !important; }
        h1, h2, h3 { color: #00d4aa !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        p, li, span, label { color: #e0e0e0 !important; }
        
        /* Pulsanti */
        .stButton>button { background-color: #1f1f1f !important; color: #ffffff !important; border-radius: 8px; border: 1px solid #333333 !important; width: 100%; padding: 10px; font-weight: 600; }
        .stButton>button:hover { background-color: #00d4aa !important; color: #0f0f0f !important; border-color: #00d4aa !important; }
        
        /* Input, Select e File Uploader */
        input, div[data-baseweb="select"] > div { background-color: #1f1f1f !important; color: #ffffff !important; border-color: #333333 !important; }
        div[data-testid="stFileUploader"] section { background-color: #1f1f1f !important; border: 1px dashed #444444 !important; color: #ffffff !important; }
        
        /* Tab Didattici (Correzione scritte scure) */
        button[data-baseweb="tab"] { color: #8a94a6 !important; font-weight: 600 !important; font-size: 15px !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #00d4aa !important; border-bottom: 3px solid #00d4aa !important; }
        
        /* Tendine (Popover) */
        div[data-baseweb="popover"] > div, ul[role="listbox"], li[role="option"] { background-color: #1f1f1f !important; color: #ffffff !important; }
        li[role="option"]:hover, li[role="option"]:focus, li[aria-selected="true"] { background-color: #00d4aa !important; color: #0f0f0f !important; }
        
        /* Tooltip (Punto interrogativo) */
        div[data-testid="stTooltipContent"], div[data-baseweb="tooltip"] > div { background-color: #1f1f1f !important; color: #ffffff !important; border: 1px solid #333333 !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp, .stApp > header { background-color: #f8f9fa !important; color: #212529 !important; }
        section[data-testid="stSidebar"] { background-color: #e9ecef !important; border-right: 1px solid #dee2e6 !important; }
        section[data-testid="stSidebar"] * { color: #212529 !important; }
        
        div[data-testid="stColumn"] { background-color: #ffffff !important; border-radius: 12px; padding: 20px; border: 1px solid #dee2e6 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        h1, h2, h3 { color: #007a60 !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        p, li, span, label { color: #212529 !important; }
        
        .stButton>button { background-color: #f1f3f5 !important; color: #212529 !important; border-radius: 8px; border: 1px solid #ced4da !important; width: 100%; padding: 10px; font-weight: 600; }
        .stButton>button:hover { background-color: #007a60 !important; color: #ffffff !important; border-color: #007a60 !important; }
        
        input, div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #212529 !important; border-color: #ced4da !important; }
        div[data-testid="stFileUploader"] section { background-color: #ffffff !important; border: 1px dashed #ced4da !important; color: #212529 !important; }
        
        button[data-baseweb="tab"] { color: #64748b !important; font-weight: 600 !important; font-size: 15px !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #007a60 !important; border-bottom: 3px solid #007a60 !important; }
        
        div[data-baseweb="popover"] > div, ul[role="listbox"], li[role="option"] { background-color: #ffffff !important; color: #212529 !important; }
        li[role="option"]:hover, li[role="option"]:focus, li[aria-selected="true"] { background-color: #007a60 !important; color: #ffffff !important; }
        div[data-testid="stTooltipContent"], div[data-baseweb="tooltip"] > div { background-color: #ffffff !important; color: #212529 !important; border: 1px solid #ced4da !important; }
        </style>
    """, unsafe_allow_html=True)


# --- HEADER ---
st.title("🧪 OmniScience 3D Studio Pro")
st.caption(f"🔬 *Laboratorio e Progettazione Didattica MIUR | Classe A050*")

col_regia, col_main = st.columns([0.27, 0.73], gap="large")

with col_regia:
    st.markdown("### ✍️ LEZIONE")
    argomento = st.text_input("Oggetto Scientifico:", value="Mitosi e Meiosi")
    
    st.markdown("---")
    st.markdown("### 📦 CARICA MODELLO 3D")
    file_3d = st.file_uploader("Seleziona file .glb (Opzionale):", type=["glb"])
    
    with st.expander("🔍 Guida ai file .glb e Risorse Gratuite"):
        st.write("""
        I file **.glb** (chiamati anche gLTF binari) sono il formato standard per il 3D sul web: leggeri, con colori e texture inclusi.
        
        **1. Portali 3D Gratuiti**
        * **Sketchfab (sketchfab.com):** Cerca in inglese (es. *plant cell*). **Attiva il filtro "Downloadable"**.
        * **NASA 3D (gdc.nasa.gov):** Modelli astronomici e geologici.
        * **Smithsonian (3d.si.edu):** Fossili e reperti.

        **2. Generare 3D con l'I.A.**
        Usa **Tripo3D (tripo3d.ai)**: Registrati gratis, vai su *Text-to-3D*, scrivi cosa ti serve in inglese (es. *3D model of methane molecule CH4*) e scarica il file GLB.
        """)
    
    st.markdown("---")
    st.markdown("### 👁️ LABORATORIO VISIONE")
    img_alunno = st.file_uploader("Carica schema/disegno alunno:", type=["jpg", "png", "jpeg"])

with col_main:
    # 1. VIEWPORT 3D
    st.markdown(f"## 🌐 VISUALIZZATORE: {argomento.upper()}")
    data_url = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
    if file_3d:
        data_url = f"data:model/gltf-binary;base64,{base64.b64encode(file_3d.getvalue()).decode()}"
    
    bg_v = "#111111" if "Scura" in st.session_state.tema_scelto else "#ffffff"
    border_v = "#333333" if "Scura" in st.session_state.tema_scelto else "#ced4da"
    html_3d = f'<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script><model-viewer src="{data_url}" camera-controls auto-rotate style="width: 100%; height: 450px; background-color: {bg_v}; border: 1px solid {border_v}; border-radius: 12px;"></model-viewer>'
    components.html(html_3d, height=460)

    # 2. CHAT INTERATTIVA
    with st.expander("💬 Chat Interattiva con l'Oggetto (Simulazione Alunni)"):
        for m in st.session_state.chat_history: st.chat_message(m["role"]).write(m["content"])
        if prompt_chat := st.chat_input("Chiedi qualcosa all'oggetto scientifico..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt_chat})
            if api_key:
                client = genai.Client(api_key=api_key)
                resp = client.models.generate_content(model='gemini-2.5-flash', contents=f"Rispondi come se fossi in prima persona '{argomento}' parlando a un alunno di {scuola_tipo} (Profilo {profilo}). Sii chiaro, empatico e scientificamente preciso. Domanda: {prompt_chat}")
                st.session_state.chat_history.append({"role": "assistant", "content": resp.text})
                st.rerun()

    st.markdown("---")
    
    # 3. DASHBOARD DIDATTICA
    st.markdown(f"## 📚 PROGETTAZIONE E METODOLOGIA")
    tabs = st.tabs(["✨ Spiegazione", "🎯 Progettazione UDA", "🌍 Compito di Realtà", "🌈 Inclusione (PDP/PEI)", "📝 SuperQuiz 10", "📊 Valutazione", "📸 Visione AI", "💾 Esporta"])
    
    prompt_normativo = f"Agisci come un Esperto Docente di Scienze (A050) italiano. Target: {scuola_tipo}. Profilo: {profilo}. Usa terminologia MIUR (UDA, rubriche, competenze chiave)."
    
    def run_ai(p):
        if not api_key: return "⚠️ Inserisci API Key nella barra laterale."
        try:
            client = genai.Client(api_key=api_key)
            return client.models.generate_content(model='gemini-2.5-flash', contents=p).text
        except Exception as e: 
            if "503" in str(e): return "⏳ Server occupati. Riprova tra pochi secondi!"
            return f"❌ Errore tecnico: {e}"

    with tabs[0]:
        if st.button("🚀 Genera Spiegazione Adattiva"): 
            st.markdown(run_ai(f"{prompt_normativo} Scrivi la spiegazione di '{argomento}'. Inizia con una metafora potente. Adatta linguaggio e formattazione al profilo {profilo}."))

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
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Genera Quiz (10 Domande)"):
                st.markdown(run_ai(f"{prompt_normativo} Crea un test di 10 domande a risposta multipla su '{argomento}'. Soluzioni commentate alla fine."))
        with col2:
            if st.button("📊 Genera Griglia Valutativa"):
                st.markdown(run_ai(f"{prompt_normativo} Crea una rubrica valutativa MIUR a 4 livelli per '{argomento}'. Focus su: Conoscenza, Lessico e Rielaborazione."))

    with tabs[5]:
        if img_alunno:
            if st.button("📸 Analizza Elaborato"):
                client = genai.Client(api_key=api_key)
                img = Image.open(img_alunno)
                resp = client.models.generate_content(model='gemini-2.5-flash', contents=[f"{prompt_normativo} Analizza questo disegno/schema di un alunno su '{argomento}'. Dai feedback formativo incoraggiante.", img])
                st.image(img, width=400)
                st.markdown(resp.text)
        else: st.info("💡 Carica un'immagine a sinistra per attivare l'analisi.")

    with tabs[6]:
        if st.button("📦 Prepara Lezione per Download"):
            lezione_html = f"<html><head><title>Lezione: {argomento}</title><style>body{{font-family:sans-serif; padding:40px;}} .box{{border:2px solid #00d4aa; padding:20px; border-radius:10px;}}</style></head><body><h1>{argomento}</h1><div class='box'><strong>Scuola:</strong> {scuola_tipo}<br><strong>Profilo:</strong> {profilo}</div></body></html>"
            st.download_button("Scarica File Offline (HTML)", lezione_html, file_name=f"Lezione_{argomento}.html", mime="text/html")
