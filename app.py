import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64
from PIL import Image
import io
import time

# 1. CONFIGURAZIONE INTERFACCIA
st.set_page_config(page_title="OmniScience 3D Studio Pro", layout="wide", initial_sidebar_state="expanded")

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "tema_scelto" not in st.session_state: st.session_state.tema_scelto = "Modalità Scura (Consigliata)"
if "spiegazione" not in st.session_state: st.session_state.spiegazione = ""
if "uda" not in st.session_state: st.session_state.uda = ""
if "realta" not in st.session_state: st.session_state.realta = ""
if "inclusione" not in st.session_state: st.session_state.inclusione = ""
if "quiz" not in st.session_state: st.session_state.quiz = ""

# --- BARRA LATERALE: REGIA DOCENTE ---
st.sidebar.markdown("## ⚙️ REGIA DOCENTE")
tema = st.sidebar.selectbox("🎨 Tema Visivo:", ["Modalità Scura (Consigliata)", "Modalità Chiara"], key="tema_selector")
st.session_state.tema_scelto = tema
api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# SCELTA DEL MODELLO
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
    "Standard (Nessun PDP/PEI)", 
    "DSA (Legge 170/2010 - PDP)", 
    "BES (Dir. Min. 2012 - PDP)", 
    "Sostegno (Legge 104/92 - PEI)"
])

# --- INIEZIONE CSS BLINDATA (CON NUOVO FIX RADICALE PER L'ICONA INFO) ---
if st.session_state.tema_scelto == "Modalità Scura (Consigliata)":
    st.markdown("""
        <style>
        .stApp, header[data-testid="stHeader"] { background-color: #0f0f0f !important; color: #ffffff !important; }
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background-color: #161616 !important; border-right: 1px solid #2d2d2d !important; }
        section[data-testid="stSidebar"] * { color: #ffffff !important; }
        
        /* FIX PULSANTE APRI/CHIUDI BARRA LATERALE */
        [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] { background-color: #1f1f1f !important; border-radius: 8px !important; border: 1px solid #333333 !important; }
        [data-testid="collapsedControl"] svg, [data-testid="stSidebarCollapseButton"] svg { fill: #00d4aa !important; stroke: #00d4aa !important; color: #00d4aa !important; }
        
        div[data-testid="stColumn"] { background-color: #161616 !important; border-radius: 12px; padding: 20px; border: 1px solid #2d2d2d !important; }
        div[data-testid="stColumn"] p, div[data-testid="stColumn"] span, div[data-testid="stColumn"] label { color: #ffffff !important; }
        h1, h2, h3 { color: #00d4aa !important; font-weight: 600; }
        
        /* FIX INPUT E OCCHIELLO PASSWORD */
        div[data-baseweb="input"], div[data-baseweb="input"] > div, div[data-baseweb="input"] > div > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div { background-color: #1f1f1f !important; border-color: #333333 !important; color: #ffffff !important; }
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
        
        /* FIX PULSANTE DOWNLOAD E PULSANTI GENERALI */
        .stButton>button, .stDownloadButton>button, div[data-testid="stDownloadButton"] button, .st-key-download_btn button { 
             background-color: #1f1f1f !important; 
             color: #ffffff !important; 
             border: 1px solid #333 !important; 
             border-radius: 8px; 
             font-weight: 600; 
             width: 100%; 
         }
        .stButton>button *, .stDownloadButton>button *, div[data-testid="stDownloadButton"] button *, .st-key-download_btn button * { color: #ffffff !important; }
        .stButton>button:hover, .stDownloadButton>button:hover, div[data-testid="stDownloadButton"] button:hover, .st-key-download_btn button:hover { 
             background-color: #00d4aa !important; 
             color: #0f0f0f !important; 
             border-color: #00d4aa !important; 
         }
        .stButton>button:hover *, .stDownloadButton>button:hover *, div[data-testid="stDownloadButton"] button:hover *, .st-key-download_btn button:hover * { color: #0f0f0f !important; }
        
        button[data-baseweb="tab"] { color: #8a94a6 !important; font-weight: 600 !important; font-size: 14px !important; background-color: transparent !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #00d4aa !important; border-bottom: 3px solid #00d4aa !important; }
        div[data-testid="stTooltipContent"] { background-color: #1f1f1f !important; color: #ffffff !important; border: 1px solid #333 !important; }
        
        /* FIX DEFINITIVO E RADICALE PER IL BOTTONE "i" IN DARK MODE */
        div[data-testid="stPopover"] { background-color: transparent !important; display: flex !important; justify-content: flex-end !important; }
        div[data-testid="stPopover"] > button {
            background-color: #1f1f1f !important;
            border: 1px solid #333333 !important;
            color: #00d4aa !important;
            font-size: 1.4rem !important;
            border-radius: 50% !important; /* Forza la forma circolare perfetta */
            width: 45px !important;
            height: 45px !important;
            min-width: 45px !important;
            min-height: 45px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        }
        div[data-testid="stPopover"] > button:hover { 
            background-color: #00d4aa !important; 
            color: #0f0f0f !important; 
            border-color: #00d4aa !important;
        }
        /* Rimuove freccette o svg integrati da Streamlit che generano glitch visivi */
        div[data-testid="stPopover"] > button svg { display: none !important; }
        div[data-testid="stPopover"] > button p { color: inherit !important; font-size: 1.4rem !important; margin: 0 !important; padding: 0 !important; font-weight: bold !important; line-height: 1 !important; }

        /* PULSANTE DI CHIUSURA "X" INTERNO (DARK) */
        .close-popover-btn button {
            background-color: transparent !important;
            border: 1px solid #444444 !important;
            color: #ff5555 !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            float: right !important;
            width: 35px !important;
            height: 35px !important;
            padding: 0 !important;
            margin-top: -10px;
        }
        .close-popover-btn button:hover {
            background-color: #ff5555 !important;
            color: #ffffff !important;
            border-color: #ff5555 !important;
        }

        /* Tabelle Markdown Dark */
        table { width: 100%; border-collapse: collapse; margin: 15px 0; color: #ffffff; }
        th { background-color: #1f1f1f; color: #00d4aa; font-weight: bold; padding: 10px; border: 1px solid #333333; }
        td { padding: 10px; border: 1px solid #333333; background-color: #161616; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp, header[data-testid="stHeader"] { background-color: #f8f9fa !important; color: #212529 !important; }
        section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background-color: #e9ecef !important; border-right: 1px solid #dee2e6 !important; }
        section[data-testid="stSidebar"] * { color: #212529 !important; }
        
        /* FIX PULSANTE APRI/CHIUDI BARRA LATERALE */
        [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] { background-color: #ffffff !important; border-radius: 8px !important; border: 1px solid #ced4da !important; }
        [data-testid="collapsedControl"] svg, [data-testid="stSidebarCollapseButton"] svg { fill: #007a60 !important; stroke: #007a60 !important; color: #007a60 !important; }
        
        div[data-testid="stColumn"] { background-color: #ffffff !important; border-radius: 12px; padding: 20px; border: 1px solid #dee2e6 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        div[data-testid="stColumn"] p, div[data-testid="stColumn"] span, div[data-testid="stColumn"] label { color: #212529 !important; }
        h1, h2, h3 { color: #007a60 !important; font-weight: 600; }
        
        /* FIX INPUT E OCCHIELLO PASSWORD */
        div[data-baseweb="input"], div[data-baseweb="input"] > div, div[data-baseweb="input"] > div > div, div[data-baseweb="select"] > div, div[data-baseweb="textarea"] > div { background-color: #ffffff !important; border-color: #ced4da !important; color: #212529 !important; }
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
        
        /* FIX PULSANTE DOWNLOAD E PULSANTI GENERALI */
        .stButton>button, .stDownloadButton>button, div[data-testid="stDownloadButton"] button, .st-key-download_btn button { 
             background-color: #ffffff !important; 
             color: #212529 !important; 
             border: 1px solid #ced4da !important; 
             border-radius: 8px; 
             font-weight: 600; 
             width: 100%; 
         }
        .stButton>button *, .stDownloadButton>button *, div[data-testid="stDownloadButton"] button *, .st-key-download_btn button * { color: #212529 !important; }
        .stButton>button:hover, .stDownloadButton>button:hover, div[data-testid="stDownloadButton"] button:hover, .st-key-download_btn button:hover { 
             background-color: #007a60 !important; 
             color: #ffffff !important; 
             border-color: #007a60 !important; 
         }
        .stButton>button:hover *, .stDownloadButton>button:hover *, div[data-testid="stDownloadButton"] button:hover *, .st-key-download_btn button:hover * { color: #ffffff !important; }
        
        /* FIX BOTTONE "i" IN MODALITÀ CHIARA */
        div[data-testid="stPopover"] { display: flex !important; justify-content: flex-end !important; }
        div[data-testid="stPopover"] > button {
            background-color: #ffffff !important;
            border: 1px solid #ced4da !important;
            color: #007a60 !important;
            font-size: 1.4rem !important;
            border-radius: 50% !important;
            width: 45px !important;
            height: 45px !important;
            min-width: 45px !important;
            min-height: 45px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        }
        div[data-testid="stPopover"] > button:hover { 
            background-color: #007a60 !important; 
            color: #ffffff !important; 
            border-color: #007a60 !important;
        }
        div[data-testid="stPopover"] > button svg { display: none !important; }
        div[data-testid="stPopover"] > button p { color: inherit !important; font-size: 1.4rem !important; margin: 0 !important; padding: 0 !important; font-weight: bold !important; line-height: 1 !important; }

        /* PULSANTE DI CHIUSURA "X" INTERNO (LIGHT) */
        .close-popover-btn button {
            background-color: transparent !important;
            border: 1px solid #ced4da !important;
            color: #dc3545 !important;
            border-radius: 6px !important;
            font-weight: bold !important;
            float: right !important;
            width: 35px !important;
            height: 35px !important;
            padding: 0 !important;
            margin-top: -10px;
        }
        .close-popover-btn button:hover {
            background-color: #dc3545 !important;
            color: #ffffff !important;
            border-color: #dc3545 !important;
        }

        /* Tabelle Markdown Light */
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th { background-color: #e9ecef; color: #007a60; font-weight: bold; padding: 10px; border: 1px solid #dee2e6; }
        td { padding: 10px; border: 1px solid #dee2e6; background-color: #ffffff; }
        </style>
    """, unsafe_allow_html=True)

# --- HEADER CON ICONA INFORMATIVA POP-UP CIRCOLARE PERFECT ---
col_titolo, col_info = st.columns([0.88, 0.12], vertical_alignment="center")
with col_titolo:
    st.title("🧪 OmniScience 3D Studio Pro")
with col_info:
    # Il popover usa la stringa "ⓘ", trasformata in etichetta centrale pulita via CSS priva di artefatti nativi
    with st.popover("ⓘ", help="Clicca per scoprire come funziona l'applicazione"):
        col_pop_title, col_pop_close = st.columns([0.85, 0.15])
        with col_pop_title:
            st.markdown("### 🏛️ Guia Rapida")
        with col_pop_close:
            st.markdown('<div class="close-popover-btn">', unsafe_allow_html=True)
            if st.button("✕", key="close_popover_trigger"):
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown("""
        **OmniScience 3D Studio Pro** è un assistente didattico avanzato basato su AI pensato per i docenti di Scienze Naturali (A050).
        
        * **1. Configurazione:** Inserisci la tua *Gemini API Key* e imposta l'indirizzo scolastico e il profilo dello studente (es. BES, DSA, Standard) nella barra laterale.
        * **2. Laboratorio 3D:** Carica un file `.glb` per mostrare strutture biologiche o chimiche tridimensionali direttamente nel visualizzatore integrato. Gli studenti possono dialogare direttamente con l'oggetto scientifico tramite la chat.
        * **3. Progettazione Automatica:** Naviga tra le schede per generare Spiegazioni adattive, Unità di Apprendimento (UDA), Compiti di realtà completi e Piani didattici inclusivi.
        * **4. Verifiche Flawless:** La tab *SuperQuiz* genera 10 domande con soluzioni e compila una griglia di valutazione MIUR a 4 livelli senza errori di formattazione.
        * **5. Esportazione Unificata:** Nella scheda *Esporta*, seleziona i moduli generati e scarica una lezione interattiva HTML standalone, funzionante anche offline.
        """)

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
                resp = client.models.generate_content(model=modello_gemini, contents=f"Rispondi in prima persona come '{argomento}' parlando a un alunno di {scuola_tipo} (Profilo {profilo}). Domanda: {prompt_chat}")
                st.session_state.chat_history.append({"role": "assistant", "content": resp.text})
                st.rerun()

    st.markdown("---")
    
    # 3. DASHBOARD DIDATTICA
    st.markdown(f"## 📚 PROGETTAZIONE E METODOLOGIA")
    tabs = st.tabs(["✨ Spiegazione", "🎯 Progettazione UDA", "🌍 Compito di Realtà", "🌈 Inclusione (PDP/PEI)", "📝 SuperQuiz 10", "🖼️ Infografica", "💾 Esporta"])
    
    prompt_normativo = f"Agisci come un Esperto Docente di Scienze (A050) italiano. Target: {scuola_tipo}. Profilo: {profilo}. Usa terminologia MIUR (UDA, rubriche, competenze chiave)."
    
    def run_ai_with_progress(prompt_text, success_msg):
        if not api_key:
            st.error("⚠️ Inserisci API Key nella barra laterale.")
            return None
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            with st.spinner(f"🤖 L'intelligenza Artificiale sta elaborando..."):
                for percent_complete in range(1, 35):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete)
                    status_text.text(f"Analisi del contesto normativo... {percent_complete}%")
                
                client = genai.Client(api_key=api_key)
                
                for percent_complete in range(35, 70):
                    time.sleep(0.005)
                    progress_bar.progress(percent_complete)
                    status_text.text(f"Generazione dei contenuti didattici... {percent_complete}%")
                
                response = client.models.generate_content(model=modello_gemini, contents=prompt_text).text
                
                for percent_complete in range(70, 101):
                    time.sleep(0.005)
                    progress_bar.progress(percent_complete)
                    status_text.text(f"Finalizzazione e formattazione... {percent_complete}%")
                
                progress_bar.empty()
                status_text.empty()
                st.success(success_msg)
                return response
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Errore tecnico durante la generazione: {e}")
            return None

    with tabs[0]:
        if st.button("🚀 Genera Spiegazione Adattiva"): 
             res = run_ai_with_progress(
                 f"{prompt_normativo} Scrivi la spiegazione di '{argomento}'. Inizia con una metafora potente. Adatta rigorosamente linguaggio e formattazione al profilo {profilo}.",
                 "✨ Spiegazione creata con successo!"
             )
             if res: st.session_state.spiegazione = res
        if st.session_state.spiegazione:
            st.markdown(st.session_state.spiegazione)

    with tabs[1]:
        if st.button("🎯 Genera Progettazione UDA"):
            res = run_ai_with_progress(
                f"{prompt_normativo} Struttura l'UDA per '{argomento}': 1. Prerequisiti, 2. Obiettivi (Conoscenze/Abilità), 3. Competenze chiave europee.",
                "🎯 Unità di Apprendimento strutturata!"
            )
            if res: st.session_state.uda = res
        if st.session_state.uda:
            st.markdown(st.session_state.uda)

    with tabs[2]:
        if st.button("🌍 Progetta Compito di Realtà"):
            res = run_ai_with_progress(
                f"{prompt_normativo} Crea un Compito di Realtà su '{argomento}'. Includi: Scenario reale, Ruolo studenti, Prodotto finale, Fasi e Criteri di valutazione.",
                "🌍 Compito di realtà generato!"
            )
            if res: st.session_state.realta = res
        if st.session_state.realta:
            st.markdown(st.session_state.realta)

    with tabs[3]:
        if st.button("🌈 Genera Piano Inclusivo"):
            res = run_ai_with_progress(
                f"{prompt_normativo} Definisci per '{argomento}': Obiettivi minimi, Strumenti compensativi, Misure dispensative e uno schema testuale semplificato.",
                "🌈 Piano personalizzato completato!"
            )
            if res: st.session_state.inclusione = res
        if st.session_state.inclusione:
            st.markdown(st.session_state.inclusione)

    with tabs[4]:
        if st.button("📝 Genera Quiz (10 Domande) e Griglia"):
            prompt_quiz_ottimizzato = f"""
            {prompt_normativo} 
            Crea un test di 10 domande a risposta multipla su '{argomento}' con relative soluzioni.
            
            Alla fine del quiz, inserisci tassativamente una **Griglia di Valutazione MIUR a 4 livelli** formattata come una vera tabella Markdown standard.
            Usa esattamente questa struttura per l'intestazione e i separatori della tabella, compilando opportunamente i contenuti senza saltare righe o aggiungere trattini infiniti:
            
            | Livello | Punteggio (Risposte Corrette) | Descrittori Specifici per la Valutazione delle Competenze (MIUR) | Valutazione |
            | :--- | :--- | :--- | :--- |
            | **Avanzato** | 10 risposte corrette | L'alunno manifesta un'elevata padronanza concettuale... | Eccellente / Ottimo (9-10) |
            | **Intermedio** | 8-9 risposte corrette | L'alunno dimostra una buona e solida comprensione... | Buono / Distinto (8) |
            | **Base** | 6-7 risposte corrette | L'alunno applica le conoscenze in contesti noti o esecutivi... | Sufficiente (6-7) |
            | **In Via di Prima Acquisizione** | 0-5 risposte corrette | L'alunno si orienta nel modulo didattico solo se supportato... | Non Sufficiente (4-5) |
            
            Assicurati che non ci siano interruzioni orizzontali anomale o stringhe di soli trattini slegate dai pipe '|'.
            """
            res = run_ai_with_progress(prompt_quiz_ottimizzato, "📝 Quiz e tabella di valutazione pronti!")
            if res: st.session_state.quiz = res
        if st.session_state.quiz:
            st.markdown(st.session_state.quiz)

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

    # TAB ESPORTAZIONE
    with tabs[6]:
        st.markdown("### 💾 Esporta Lezione Interattiva (Smart Offline)")
        st.markdown("##### ⚙️ Seleziona i moduli da includere nell'esportazione:")
        
        label_spiegazione = "✨ Spiegazione" if st.session_state.spiegazione else "✨ Spiegazione (Non ancora generata)"
        label_uda = "🎯 Progettazione UDA" if st.session_state.uda else "🎯 Progettazione UDA (Non ancora generata)"
        label_realta = "🌍 Compito di Realtà" if st.session_state.realta else "🌍 Compito di Realtà (Non ancora generato)"
        label_inclusione = "🌈 Inclusione (PDP/PEI)" if st.session_state.inclusione else "🌈 Inclusione (PDP/PEI) (Non ancora generata)"
        label_quiz = "📝 SuperQuiz 10" if st.session_state.quiz else "📝 SuperQuiz 10 (Non ancora generato)"
        label_images = "🖼️ Galleria Scientifica (Infografica)" if immagini_lezione else "🖼️ Galleria Scientifica (Nessuna immagine caricata)"

        col_chk1, col_chk2 = st.columns(2)
        with col_chk1:
            sel_spiegazione = st.checkbox(label_spiegazione, value=bool(st.session_state.spiegazione), disabled=not st.session_state.spiegazione)
            sel_uda = st.checkbox(label_uda, value=bool(st.session_state.uda), disabled=not st.session_state.uda)
            sel_realta = st.checkbox(label_realta, value=bool(st.session_state.realta), disabled=not st.session_state.realta)
        with col_chk2:
            sel_inclusione = st.checkbox(label_inclusione, value=bool(st.session_state.inclusione), disabled=not st.session_state.inclusione)
            sel_quiz = st.checkbox(label_quiz, value=bool(st.session_state.quiz), disabled=not st.session_state.quiz)
            sel_images = st.checkbox(label_images, value=bool(immagini_lezione), disabled=not immagini_lezione)

        st.markdown("---")

        fallback_html = "<div style='padding: 50px; background: #e9ecef; color: #666; text-align: center; border-radius: 12px; border: 2px dashed #ccc; font-size: 1.2em;'>⚠️ Sei offline. Collegati a Internet per visualizzare il modello 3D interattivo.</div>"
        if img_copertina:
            img_copertina.seek(0)
            b64_cover = base64.b64encode(img_copertina.read()).decode()
            fallback_html = f"<img src='data:image/png;base64,{b64_cover}' style='width: 100%; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>"

        html_tab_buttons = ""
        html_tab_contents = ""
        active_class_added = False
        
        if sel_spiegazione and st.session_state.spiegazione:
            active_class = " active" if not active_class_added else ""
            active_class_added = True
            html_tab_buttons += f'<button class="tab-button{active_class}" onclick="openTab(event, \'tab-spiegazione\')">✨ Spiegazione</button>\n'
            html_tab_contents += f"""
            <div id="tab-spiegazione" class="tab-content{active_class}">
                <h2>✨ Spiegazione: {argomento}</h2>
                <div class="markdown-content">{st.session_state.spiegazione}</div>
            </div>
            """
        
        if sel_uda and st.session_state.uda:
            active_class = " active" if not active_class_added else ""
            active_class_added = True
            html_tab_buttons += f'<button class="tab-button{active_class}" onclick="openTab(event, \'tab-uda\')">🎯 Progettazione UDA</button>\n'
            html_tab_contents += f"""
            <div id="tab-uda" class="tab-content{active_class}">
                <h2>🎯 Progettazione UDA</h2>
                <div class="markdown-content">{st.session_state.uda}</div>
            </div>
            """
            
        if sel_realta and st.session_state.realta:
            active_class = " active" if not active_class_added else ""
            active_class_added = True
            html_tab_buttons += f'<button class="tab-button{active_class}" onclick="openTab(event, \'tab-realta\')">🌍 Compito di Realtà</button>\n'
            html_tab_contents += f"""
            <div id="tab-realta" class="tab-content{active_class}">
                <h2>🌍 Compito di Realtà</h2>
                <div class="markdown-content">{st.session_state.realta}</div>
            </div>
            """
            
        if sel_inclusione and st.session_state.inclusione:
            active_class = " active" if not active_class_added else ""
            active_class_added = True
            html_tab_buttons += f'<button class="tab-button{active_class}" onclick="openTab(event, \'tab-inclusione\')">🌈 Inclusione (PDP/PEI)</button>\n'
            html_tab_contents += f"""
            <div id="tab-inclusione" class="tab-content{active_class}">
                <h2>🌈 Inclusione (PDP/PEI)</h2>
                <div class="markdown-content">{st.session_state.inclusione}</div>
            </div>
            """
            
        if sel_quiz and st.session_state.quiz:
            active_class = " active" if not active_class_added else ""
            active_class_added = True
            html_tab_buttons += f'<button class="tab-button{active_class}" onclick="openTab(event, \'tab-quiz\')">📝 SuperQuiz 10</button>\n'
            html_tab_contents += f"""
            <div id="tab-quiz" class="tab-content{active_class}">
                <h2>📝 SuperQuiz 10</h2>
                <div class="markdown-content">{st.session_state.quiz}</div>
            </div>
            """

        if sel_images and immagini_lezione:
            active_class = " active" if not active_class_added else ""
            active_class_added = True
            html_tab_buttons += f'<button class="tab-button{active_class}" onclick="openTab(event, \'tab-galleria\')">🖼️ Galleria Scientifica</button>\n'
            
            html_images_list = ""
            for img_file in immagini_lezione:
                img_file.seek(0)
                b64 = base64.b64encode(img_file.read()).decode()
                desc = didascalie.get(img_file.name, "").replace("\n", "<br>")
                html_images_list += f"""
                <div style='margin-bottom: 40px; padding: 20px; border: 1px solid #ddd; border-radius: 12px; background: #fafafa; text-align: center;'>
                    <img src='data:image/png;base64,{b64}' style='max-width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                    <div style='margin-top: 15px; font-size: 18px; color: #444; text-align: left; line-height: 1.6; padding: 15px; background: #fff; border-left: 5px solid #00d4aa; border-radius: 4px;'>
                        {desc if desc else '<i>Nessuna didascalia fornita.</i>'}
                    </div>
                </div>
                """
            html_tab_contents += f"""
            <div id="tab-galleria" class="tab-content{active_class}">
                <h2>🖼️ Galleria Scientifica</h2>
                {html_images_list}
            </div>
            """

        html_sections = f"""
        <div class="tabs-container">
            <div class="tab-buttons">
                {html_tab_buttons}
            </div>
            <div class="tab-contents">
                {html_tab_contents}
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
                #viewer-container { width: 100%; height: 500px; margin-bottom: 30px; display: flex; justify-content: center; align-items: center; background-color: #111; border-radius: 12px; }
                model-viewer { width: 100%; height: 100%; background-color: #111; border-radius: 12px; }
                .markdown-content { line-height: 1.7; font-size: 1.1em; color: #444; }
                .markdown-content p { margin-bottom: 1em; }
                .markdown-content ul, .markdown-content ol { padding-left: 20px; margin-bottom: 1em; }
                .markdown-content li { margin-bottom: 0.5em; }
                .markdown-content strong { color: #111; }
                .markdown-content code { background-color: #f1f3f5; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.9em; }
                .markdown-content pre { background-color: #f1f3f5; padding: 15px; border-radius: 8px; overflow-x: auto; }
                
                .markdown-content table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 1em; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
                .markdown-content th { background-color: #007a60; color: white; padding: 12px 15px; text-align: left; border: 1px solid #dee2e6; }
                .markdown-content td { padding: 12px 15px; border: 1px solid #dee2e6; background-color: #fafafa; }
                .markdown-content tr:nth-child(even) td { background-color: #f1f5f4; }
                                
                .tabs-container { margin-top: 30px; }
                .tab-buttons { display: flex; flex-wrap: wrap; border-bottom: 2px solid #dee2e6; margin-bottom: 25px; gap: 5px; }
                .tab-button { background-color: transparent; border: none; border-bottom: 3px solid transparent; padding: 12px 20px; font-size: 1.1em; font-weight: 600; color: #6c757d; cursor: pointer; transition: all 0.2s ease; }
                .tab-button:hover { color: #007a60; border-bottom: 3px solid #b2dfdb; }
                .tab-button.active { color: #007a60; border-bottom: 3px solid #007a60; }
                .tab-content { display: none; animation: fadeIn 0.4s ease; background: #fdfdfd; border: 1px solid #e0e0e0; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
                .tab-content h2 { color: #007a60; border-bottom: 2px solid #eef2f5; padding-bottom: 10px; margin-top: 0; }
                .tab-content.active { display: block; }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
            </style>
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        </head>
        <body>
            <div class="container">
                <h1>__ARGOMENTO__</h1>
                <div class="info-box">
                    <strong>Target:</strong> __SCUOLA_TIPO__ | <strong>Profilo:</strong> __PROFILO__
                </div>
                
                <div id="viewer-container">
                    <div id="offline-fallback" style="width: 100%; height: 100%;">
                        __FALLBACK_HTML__
                    </div>
                    <div id="online-3d" style="display: none; width: 100%; height: 100%;">
                        <model-viewer src="__DATA_URL_ONLINE__" camera-controls auto-rotate></model-viewer>
                    </div>
                </div>
                
                <div id="lesson-content">
                    __HTML_SECTIONS__
                </div>
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
                checkConnection();

                function openTab(evt, tabId) {
                    var tabContents = document.getElementsByClassName("tab-content");
                    for (var i = 0; i < tabContents.length; i++) { tabContents[i].classList.remove("active"); }
                    var tabButtons = document.getElementsByClassName("tab-button");
                    for (var i = 0; i < tabButtons.length; i++) { tabButtons[i].classList.remove("active"); }
                    document.getElementById(tabId).classList.add("active");
                    evt.currentTarget.classList.add("active");
                }

                if (typeof marked !== 'undefined') {
                    marked.setOptions({ gfm: true, breaks: true });
                    document.querySelectorAll('.markdown-content').forEach(el => { el.innerHTML = marked.parse(el.textContent); });
                } else {
                    document.querySelectorAll('.markdown-content').forEach(el => { el.style.whiteSpace = 'pre-wrap'; });
                }
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
        lezione_html = lezione_html.replace("__HTML_SECTIONS__", html_sections)
        
        abilitato_export = (sel_spiegazione or sel_uda or sel_realta or sel_inclusione or sel_quiz or sel_images)
        if habilitato_export:
            st.download_button(
                "📦 Scarica Lezione Smart (HTML)", 
                lezione_html, 
                file_name=f"Lezione_{argomento.replace(' ', '_')}.html", 
                mime="text/html",
                key="download_btn"
            )
        else:
            st.warning("⚠️ Seleziona almeno un contenuto generato o un'immagine per procedere con l'esportazione.")
