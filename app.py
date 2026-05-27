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
tema = st.sidebar.selectbox("🎨 Tema:", ["Modalità Scura (Consigliata)", "Modalità Chiara"], key="tema_selector")
st.session_state.tema_scelto = tema

api_key = st.sidebar.text_input("Gemini API Key:", type="password")

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

# MENU AGGIORNATO CON TUTTI I GRADI SCOLASTICI E BIENNIO/TRIENNIO
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

# --- INIEZIONE CSS (Fix Tendine, Tooltip e Layout) ---
css_style = """
<style>
    .stApp { background-color: """ + ("#0f0f0f" if "Scura" in st.session_state.tema_scelto else "#f8f9fa") + """ !important; color: """ + ("#ffffff" if "Scura" in st.session_state.tema_scelto else "#212529") + """ !important; }
    div[data-testid="stColumn"] { background-color: """ + ("#161616" if "Scura" in st.session_state.tema_scelto else "#ffffff") + """ !important; border-radius: 12px; padding: 20px; border: 1px solid #2d2d2d; }
    button[data-baseweb="tab"] { font-size: 14px !important; font-weight: 600 !important; }
    div[data-baseweb="popover"] > div, ul[role="listbox"], li[role="option"] { background-color: #1f1f1f !important; color: #ffffff !important; }
    li[role="option"]:hover { background-color: #00d4aa !important; color: #000 !important; }
    div[data-testid="stTooltipContent"], div[data-baseweb="tooltip"] > div { background-color: #1f1f1f !important; color: #ffffff !important; border: 1px solid #333; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; }
</style>
"""
st.markdown(css_style, unsafe_allow_html=True)

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
    
    # GUIDA AI FILE GLB
    with st.expander("🔍 Guida ai file .glb e Risorse Gratuite"):
        st.write("""
        I file **.glb** (chiamati anche gLTF binari) sono il formato standard per il 3D sul web: sono leggeri, includono già i colori e le texture.

        Ecco le migliori risorse online:
        * 🪐 **Sketchfab (sketchfab.com):** Cerca in inglese. **Trucco:** attiva il filtro **"Downloadable"**.
        * 🏛️ **NASA 3D & Smithsonian:** Modelli astronomici e fossili (3d.si.edu).
        * 🧬 **BioDigital:** Modelli anatomici.

        **Creare GLB con l'I.A.**
        Usa **Tripo3D (tripo3d.ai)**:
        1. Vai su **Text-to-3D**.
        2. Scrivi cosa desideri in inglese.
        3. Scarica in formato **GLB**.
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
    html_3d = f'<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script><model-viewer src="{data_url}" camera-controls auto-rotate style="width: 100%; height: 450px; background-color: {bg_v}; border-radius: 12px;"></model-viewer>'
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
    
    # 3. DASHBOARD DIDATTICA (Tab Professionali MIUR)
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
            st.download_button("Scarica File Offline (HTML)", lezione_html, file_name=f"Lezione_{argomento.replace(' ', '_')}.html", mime="text/html")
