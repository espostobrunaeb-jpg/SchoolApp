import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64

# 1. CONFIGURAZIONE INTERFACCIA
st.set_page_config(page_title="OmniScience 3D Studio", layout="wide", initial_sidebar_state="expanded")

if "tema_scelto" not in st.session_state:
    st.session_state.tema_scelto = "Modalità Scura (Consigliata)"

# --- BARRA LATERALE ---
st.sidebar.markdown("## ⚙️ IMPOSTAZIONI")
tema = st.sidebar.selectbox("🎨 Tema Visivo:", ["Modalità Scura (Consigliata)", "Modalità Chiara"], key="tema_selector")
st.session_state.tema_scelto = tema

api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Inserisci la chiave di Google AI Studio")

# GUIDA PER L'API KEY
with st.sidebar.expander("🔑 Come ottenere una API Key gratuita"):
    st.markdown("""
    1. Vai su [Google AI Studio](https://aistudio.google.com/).
    2. Fai l'accesso con il tuo **account Google**.
    3. Clicca su **"Get API key"**.
    4. Clicca su **"Create API key"**.
    5. Copia la chiave e incollala qui sopra.
    """)

# --- INIEZIONE CSS PERSONALIZZATO (Con FIX per tendine, tooltip e dark mode) ---
if st.session_state.tema_scelto == "Modalità Scura (Consigliata)":
    st.markdown("""
        <style>
        .stApp { background-color: #0f0f0f !important; color: #ffffff !important; }
        section[data-testid="stSidebar"] { background-color: #161616 !important; }
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #ffffff !important; }
        div[data-testid="stColumn"] { background-color: #161616 !important; border-radius: 12px; padding: 24px; border: 1px solid #262626; }
        h1, h2, h3 { color: #00d4aa !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        p, li, span, label { color: #e0e0e0 !important; }
        .stButton>button { background-color: #1f1f1f !important; color: #ffffff !important; border-radius: 6px; border: 1px solid #333333 !important; width: 100%; padding: 10px; font-weight: 500; }
        .stButton>button:hover { background-color: #00d4aa !important; color: #0f0f0f !important; border-color: #00d4aa !important; }
        div[data-baseweb="tab-list"] { gap: 10px; }
        button[data-baseweb="tab"] { color: #8a94a6 !important; font-weight: 600 !important; font-size: 15px !important; padding: 10px 15px !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #00d4aa !important; border-bottom: 3px solid #00d4aa !important; }
        div[data-baseweb="select"] > div { background-color: #1f1f1f !important; color: #ffffff !important; border-color: #333333 !important; }
        input { background-color: #1f1f1f !important; color: #ffffff !important; }
        
        div[data-baseweb="popover"] > div, ul[role="listbox"], li[role="option"] { 
            background-color: #1f1f1f !important; color: #ffffff !important; 
        }
        li[role="option"]:hover, li[role="option"]:focus, li[aria-selected="true"] { 
            background-color: #00d4aa !important; color: #0f0f0f !important; 
        }
        div[data-testid="stTooltipContent"], div[data-baseweb="tooltip"] > div {
            background-color: #1f1f1f !important; color: #ffffff !important; border: 1px solid #333333 !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa !important; color: #212529 !important; }
        section[data-testid="stSidebar"] { background-color: #e9ecef !important; }
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #212529 !important; }
        div[data-testid="stColumn"] { background-color: #ffffff !important; border-radius: 12px; padding: 24px; border: 1px solid #dee2e6 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        h1, h2, h3 { color: #007a60 !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        p, li, span, label { color: #212529 !important; }
        .stButton>button { background-color: #f1f3f5 !important; color: #212529 !important; border-radius: 6px; border: 1px solid #ced4da !important; width: 100%; padding: 10px; font-weight: 500; }
        .stButton>button:hover { background-color: #007a60 !important; color: #ffffff !important; border-color: #007a60 !important; }
        div[data-baseweb="tab-list"] { gap: 10px; }
        button[data-baseweb="tab"] { color: #64748b !important; font-weight: 600 !important; font-size: 15px !important; padding: 10px 15px !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #007a60 !important; border-bottom: 3px solid #007a60 !important; }
        div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #212529 !important; border-color: #ced4da !important; }
        input { background-color: #ffffff !important; color: #212529 !important; }
        </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **OmniScience Studio**: Inserisci l'argomento e il target per generare una lezione inclusiva e visualizzarla in 3D.")

# --- INTESTAZIONE ---
st.title("🧪 OmniScience 3D Studio")
st.caption("🔬 *Piattaforma Multimediale e Progettazione Didattica - Classe di Concorso A050*")
st.markdown("<br>", unsafe_allow_html=True)

# --- LAYOUT A DUE COLONNE ---
col_sinistra, col_destra = st.columns([0.25, 0.75], gap="large")

# ==========================================
# COLONNA DI SINISTRA: Impostazioni Lezione
# ==========================================
with col_sinistra:
    st.markdown("### ✍️ IMPOSTA LEZIONE")
    argomento = st.text_input("Argomento:", value="Membrana Cellulare")
    
    st.markdown("---")
    st.markdown("### 🎯 TARGET")
    livello_scuola = st.selectbox("Grado scolastico:", ["Scuola Elementare", "Scuola Media", "Superiori (Biennio)", "Superiori (Triennio)", "Università"], index=3)
    profilo_studente = st.selectbox("Profilo:", ["Standard", "BES (Bisogni Educativi Speciali)", "DSA (Disturbi Specifici Apprendimento)"])
    
    st.markdown("---")
    st.markdown("### 📦 MODELLO 3D")
    file_3d = st.file_uploader("Carica file .glb:", type=["glb"])

# ==========================================
# COLONNA DI DESTRA: Visualizzatore 3D e Progettazione
# ==========================================
with col_destra:
    
    # 1. VISUALIZZATORE 3D
    st.markdown(f"## 🌐 ESPOSITORE: {argomento.upper()}")
    
    if file_3d is not None:
        bytes_data = file_3d.getvalue()
        base64_3d = base64.b64encode(bytes_data).decode('utf-8')
        data_url = f"data:model/gltf-binary;base64,{base64_3d}"
    else:
        data_url = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"

    bg_viewer = "#111111" if st.session_state.tema_scelto == "Modalità Scura (Consigliata)" else "#ffffff"
    border_viewer = "#333333" if st.session_state.tema_scelto == "Modalità Scura (Consigliata)" else "#ced4da"

    html_code = f"""
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
    <div style="display: flex; justify-content: center;">
        <model-viewer src="{data_url}" camera-controls auto-rotate touch-action="pan-y"
                      style="width: 100%; height: 400px; background-color: {bg_viewer}; border-radius: 12px; border: 1px solid {border_viewer};">
        </model-viewer>
    </div>
    """
    components.html(html_code, height=410)
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    # 2. PROGETTAZIONE DIDATTICA (Nuovo Tab Spiegazione al primo posto)
    st.markdown(f"## 📚 DIDATTICA E PROGETTAZIONE: {argomento.upper()}")
    
    tabs = st.tabs([
        "✨ Spiegazione Lezione",
        "1. Prerequisiti", 
        "2. Competenze", 
        "3. Obiettivi", 
        "4. Inclusione", 
        "5. Valutazione", 
        "6. Collegamenti"
    ])
    
    # Funzioni di supporto
    contesto = f"Stai parlando a studenti di {livello_scuola} con profilo {profilo_studente}."
    
    def call_gemini(prompt_text):
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_text)
            return response.text
        except Exception as e:
            if "503" in str(e): return "⏳ Server occupato. Riprova tra 30 secondi."
            return f"Errore: {e}"

    # --- TAB 0: SPIEGAZIONE LEZIONE ---
    with tabs[0]:
        st.markdown(f"### ✨ Spiegazione per la classe ({profilo_studente})")
        st.write("Genera un testo pronto per essere letto o proiettato, adattato perfettamente al target scelto.")
        if st.button("🚀 Genera Spiegazione Lezione"):
            if api_key:
                with st.spinner("Generazione spiegazione in corso..."):
                    p = f"""Sei una docente di scienze esperta. Spiega l'argomento '{argomento}' in modo affascinante.
                    {contesto}
                    REGOLE DI LINGUAGGIO:
                    - Se DSA: usa paragrafi molto brevi, elenchi puntati e grassetti sulle parole chiave.
                    - Se BES: usa un linguaggio semplice, diretto e rassicurante, evitando astrazioni complesse.
                    - Se Standard: usa un linguaggio scientifico corretto ma coinvolgente.
                    Includi una metafora iniziale per catturare l'attenzione."""
                    st.markdown("---")
                    st.markdown(call_gemini(p))
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 1: PREREQUISITI ---
    with tabs[1]:
        st.markdown("**Conoscenze di base richieste:**")
        st.write("- Comprensione testi informativi/narrativi.\n- Individuazione parole chiave.\n- Lessico disciplinare essenziale.\n- Collaborazione in gruppo e competenze digitali.")
        if st.button("🔍 Genera Prerequisiti Specifici"):
            if api_key:
                with st.spinner("Elaborazione..."):
                    p = f"{contesto} Elenca 3 conoscenze scientifiche specifiche che gli studenti devono avere per capire '{argomento}'."
                    st.markdown("---")
                    st.markdown(call_gemini(p))
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 2: COMPETENZE ATTESE ---
    with tabs[2]:
        st.markdown("**Competenze disciplinari e trasversali:**")
        st.write("- Analizzare fonti e materiali multimediali.\n- Collegare l'argomento al contesto sociale/geografico.\n- Usare il lessico specifico e strumenti digitali.")
        if st.button("🎯 Genera Focus Competenze"):
            if api_key:
                with st.spinner("Elaborazione..."):
                    p = f"{contesto} Descrivi come lo studio di '{argomento}' sviluppa le competenze di analisi e sintesi scientifica."
                    st.markdown("---")
                    st.markdown(call_gemini(p))
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 3: OBIETTIVI DI APPRENDIMENTO ---
    with tabs[3]:
        st.markdown(f"**Traguardi per '{argomento}':**")
        st.write("- Riconoscere i concetti fondamentali.\n- Analizzare elementi, cause e conseguenze.\n- Rielaborare e argomentare quanto appreso.")
        if st.button("📊 Genera Obiettivi Operativi"):
            if api_key:
                with st.spinner("Elaborazione..."):
                    p = f"{contesto} Scrivi 3 obiettivi misurabili (es. 'Saper descrivere...') per la lezione su '{argomento}'."
                    st.markdown("---")
                    st.markdown(call_gemini(p))
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 4: INCLUSIONE E PERSONALIZZAZIONE ---
    with tabs[4]:
        st.markdown("**Strategie Inclusive:**")
        st.write("- Consegne scandite, mappe concettuali e parole chiave.\n- Testi ad alta leggibilità e strumenti compensativi.\n- Valutazione centrata sul percorso.")
        if st.button("🌈 Genera Schema Semplificato"):
            if api_key:
                with st.spinner("Elaborazione..."):
                    p = f"{contesto} Crea uno schema ultra-semplificato con 5 concetti chiave su '{argomento}' adatto a studenti con difficoltà di apprendimento."
                    st.markdown("---")
                    st.markdown(call_gemini(p))
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 5: VALUTAZIONE ---
    with tabs[5]:
        st.markdown("**Criteri di Valutazione:**")
        st.write("- Partecipazione e collaborazione.\n- Uso del lessico e capacità di collegamento.\n- Livelli: Base, Intermedio, Avanzato, Eccellente.")
        if st.button("📝 Genera Esempio di Verifica"):
            if api_key:
                with st.spinner("Elaborazione..."):
                    p = f"{contesto} Crea una prova formativa su '{argomento}' con 2 domande chiuse e 1 domanda aperta di ragionamento."
                    st.markdown("---")
                    st.markdown(call_gemini(p))
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 6: COLLEGAMENTI INTERDISCIPLINARI ---
    with tabs[6]:
        st.write("Connessioni con Educazione Civica, Storia, Fisica o altre scienze.")
        if st.button("🔗 Genera Collegamenti Creativi"):
            if api_key:
                with st.spinner("Elaborazione..."):
                    p = f"{contesto} Suggerisci 3 collegamenti interdisciplinari curiosi partendo da '{argomento}'."
                    st.markdown("---")
                    st.markdown(call_gemini(p))
            else: st.warning("Inserisci la API Key a sinistra.")
