import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64

# 1. CONFIGURAZIONE INTERFACCIA
st.set_page_config(page_title="OmniScience 3D Studio Pro", layout="wide", initial_sidebar_state="expanded")

if "tema_scelto" not in st.session_state:
    st.session_state.tema_scelto = "Modalità Scura (Consigliata)"
if 'elemento_corrente' not in st.session_state:
    st.session_state.elemento_corrente = "🧫 Nucleo Cellulare"
if 'materia_scelta' not in st.session_state:
    st.session_state.materia_scelta = "Biologia"

# --- BARRA LATERALE: TEMA E SICUREZZA ---
st.sidebar.markdown("## ⚙️ PANNELLO DI CONTROLLO")
tema = st.sidebar.selectbox("🎨 Tema Visivo:", ["Modalità Scura (Consigliata)", "Modalità Chiara"], key="tema_selector")
st.session_state.tema_scelto = tema

api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Inserisci la chiave di Google AI Studio")

# --- INIEZIONE CSS AVANZATO PER IL THEME SWITCHING E DROPDOWN ---
if st.session_state.tema_scelto == "Modalità Scura (Consigliata)":
    st.markdown("""
        <style>
        .stApp { background-color: #0d0e12 !important; color: #ffffff !important; }
        section[data-testid="stSidebar"] { background-color: #16171d !important; }
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #ffffff !important; }
        section[data-testid="stSidebar"] div[data-testid="stNotification"] p { color: #0f172a !important; font-weight: 500; }
        
        div[data-testid="stColumn"] {
            background-color: #16171d !important;
            border-radius: 14px;
            padding: 24px;
            border: 1px solid #23252f;
            min-height: 750px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }
        
        h1, h2, h3 { color: #00e5b7 !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        p, li, span, label { color: #e2e8f0 !important; }
        
        .stButton>button {
            background-color: #1f212a !important;
            color: #ffffff !important;
            border-radius: 8px;
            border: 1px solid #2d313f !important;
            width: 100%; text-align: left; padding: 12px; font-weight: 500;
        }
        .stButton>button:hover { background-color: #00e5b7 !important; color: #0d0e12 !important; border-color: #00e5b7 !important; }
        
        div[data-baseweb="popover"], div[role="listbox"], li[role="option"] { background-color: #16171d !important; color: #ffffff !important; }
        li[role="option"]:hover { background-color: #00e5b7 !important; color: #0d0e12 !important; }
        div[data-baseweb="select"] > div { background-color: #1f212a !important; color: #ffffff !important; border-color: #2d313f !important; }
        div[data-testid="stFileUploader"] section { background-color: #1f212a !important; border: 1px dashed #444a5d !important; color: #ffffff !important; }
        input { background-color: #1f212a !important; color: #ffffff !important; }
        
        /* Stile dei Tab Superiori */
        button[data-baseweb="tab"] { color: #8a94a6 !important; font-weight: 600 !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #00e5b7 !important; border-bottom-color: #00e5b7 !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #f8fafc !important; color: #0f172a !important; }
        section[data-testid="stSidebar"] { background-color: #f1f5f9 !important; }
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #0f172a !important; }
        
        div[data-testid="stColumn"] {
            background-color: #ffffff !important;
            border-radius: 14px;
            padding: 24px;
            border: 1px solid #e2e8f0 !important;
            min-height: 750px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        
        h1, h2, h3 { color: #0f766e !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        p, li, span, label { color: #334155 !important; }
        
        .stButton>button {
            background-color: #f8fafc !important;
            color: #0f172a !important;
            border-radius: 8px;
            border: 1px solid #cbd5e1 !important;
            width: 100%; text-align: left; padding: 12px; font-weight: 500;
        }
        .stButton>button:hover { background-color: #0f766e !important; color: #ffffff !important; border-color: #0f766e !important; }
        
        div[data-baseweb="popover"], div[role="listbox"], li[role="option"] { background-color: #ffffff !important; color: #0f172a !important; }
        li[role="option"]:hover { background-color: #0f766e !important; color: #ffffff !important; }
        div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #0f172a !important; border-color: #cbd5e1 !important; }
        div[data-testid="stFileUploader"] section { background-color: #ffffff !important; border: 1px dashed #cbd5e1 !important; color: #0f172a !important; }
        input { background-color: #ffffff !important; color: #0f172a !important; }
        
        button[data-baseweb="tab"] { color: #64748b !important; font-weight: 600 !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #0f766e !important; border-bottom-color: #0f766e !important; }
        </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **OmniScience v2.5**: Espansione del layout ispirata a 'Cell Architecture Studio' per la classe A050.")

# --- INTESTAZIONE PRINCIPALE ---
st.title("🧫 OmniScience 3D Studio Pro")
st.caption("🧬 *Dashboard Didattica Avanzata per Scienze Naturali, Chimica e Geologia*")
st.markdown("<br>", unsafe_allow_html=True)

# --- CREAZIONE DELLA STRUTTURA A TRE COLONNE (Layout Premium) ---
col_menu, col_viewport, col_ai_tutor = st.columns([0.22, 0.53, 0.25], gap="large")

# ==========================================================
# COLONNA 1: SELEZIONE STRUTTURE (BIOLOGIA / CHIMICA / GEOLOGIA)
# ==========================================================
with col_menu:
    st.markdown("### 📚 AMBITO DISCIPLINARE")
    materia_selezionata = st.selectbox("Seleziona Materia:", ["Biologia", "Chimica", "Scienze della Terra"])
    st.session_state.materia_scelta = materia_selezionata
    
    st.markdown("---")
    st.markdown("### 🔍 STRUTTURE DISPONIBILI")
    st.write("Scegli l'oggetto dell'infografica:")
    
    if st.session_state.materia_scelta == "Biologia":
        if st.button("🧫 Nucleo Cellulare"): st.session_state.elemento_corrente = "🧫 Nucleo Cellulare"
        if st.button("🔋 Mitocondrio"): st.session_state.elemento_corrente = "🔋 Mitocondrio"
        if st.button("🧬 Doppia Elica DNA"): st.session_state.elemento_corrente = "🧬 Doppia Elica DNA"
        if st.button("🌿 Cloroplasto"): st.session_state.elemento_corrente = "🌿 Cloroplasto"
    elif st.session_state.materia_scelta == "Chimica":
        if st.button("💧 Molecola dell'Acqua"): st.session_state.elemento_corrente = "💧 Molecola dell'Acqua"
        if st.button("💎 Reticolo del Diamante"): st.session_state.elemento_corrente = "💎 Reticolo del Diamante"
        if st.button("⚛️ Atomo di Bohr"): st.session_state.elemento_corrente = "⚛️ Atomo di Bohr"
    elif st.session_state.materia_scelta == "Scienze della Terra":
        if st.button("🌋 Sezione di un Vulcano"): st.session_state.elemento_corrente = "🌋 Sezione di un Vulcano"
        if st.button("🌍 Strati della Terra"): st.session_state.elemento_corrente = "🌍 Strati della Terra"
        if st.button("⛰️ Faglia Tettonica"): st.session_state.elemento_corrente = "⛰️ Faglia Tettonica"

    st.markdown("<br>", unsafe_allow_html=True)
    input_libero = st.text_input("✍️ Argomento Personalizzato:", placeholder="Es. Apparato di Golgi...")
    if input_libero:
        st.session_state.elemento_corrente = input_libero

# ==========================================================
# COLONNA 2: VIEWPORT MULTI-MODALE (DETTAGLI E MICROSCREENS COME IL REPO)
# ==========================================================
with col_viewport:
    st.markdown(f"### 🌐 ESPOSITORE: {st.session_state.elemento_corrente.upper()}")
    
    # AGGIUNTA DEI TAB DI VISUALIZZAZIONE AVANZATI (Come la modatità Mesh/Focus del repo)
    tab_3d, tab_microscopio, tab_confronto = st.tabs(["📦 Modello 3D (Mesh)", "🔬 Vista Microscopio", "⚖️ Modalità Confronto"])
    
    with tab_3d:
        file_3d = st.file_uploader("Trascina qui il file .glb dell'argomento selezionato", type=["glb"])
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
        <model-viewer src="{data_url}" alt="Modello Scientifico 3D" camera-controls auto-rotate touch-action="pan-y"
                      style="width: 100%; height: 380px; background-color: {bg_viewer}; border-radius: 8px; border: 1px solid {border_viewer};">
        </model-viewer>
        """
        components.html(html_code, height=390)
        st.caption("💡 *Interazione:* Trascina per ruotare in ogni dimensione, rotella del mouse per lo zoom.")

    with tab_microscopio:
        st.write("🤖 *Simulazione di laboratorio basata su campioni reali:*")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.image("https://images.unsplash.com/photo-1576086213369-97a306d36557?w=300", caption="Analisi a Contrasto di Fase (Ottico)")
        with m_col2:
            st.image("https://images.unsplash.com/photo-1532187863486-abf9d39d6618?w=300", caption="Scansione Elettronica ad alta risoluzione (SEM)")

    with tab_confronto:
        st.write("⚖️ *Analisi Comparativa Specimen (Affiancamento Didattico)*")
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.metric(label="Struttura Attiva", value=st.session_state.elemento_corrente)
            st.write("Visualizzazione del pattern tridimensionale standard e stabilità molecolare/strutturale.")
        with c_col2:
            elemento_comp = st.selectbox("Confronta con:", ["Cellula Animale", "Legame Ionico", "Rocce Magmatiche"])
            st.write(f"Differenze chiave nell'organizzazione spaziale rispetto a *{elemento_comp}*.")

# ==========================================================
# COLONNA 3: PANNELLO AI TUTOR AVANZATO (DETTAGLI E PROMPTS)
# ==========================================================
with col_ai_tutor:
    st.markdown("### 🤖 PANNELLO AI TUTOR")
    
    # Divisione in Tab dei dettagli conoscitivi, esattamente come nel repository GitHub
    tab_info, tab_quiz, tab_obiettivi = st.tabs(["📋 Dettagli", "❓ Quiz Classe", "📊 Obiettivi"])
    
    with tab_info:
        if not api_key:
            st.warning("🔑 Inserisci la Gemini API Key per sbloccare l'infografica dettagliata.")
            st.markdown(f"**Elemento:** {st.session_state.elemento_corrente}\n\n*In attesa dell'attivazione dell'Intelligenza Artificiale...*")
        else:
            with st.spinner("Generazione dettagli scientifici..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt_info = f"Sei una docente di scienze (A050). Fornisci una scheda tecnica dettagliata, stile infografica con emoji, per l'elemento '{st.session_state.elemento_corrente}' (Ambito: {st.session_state.materia_scelta}). Includi: Proprietà Fisiche/Biologiche, Scala di grandezza e una Metafora d'impatto."
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_info)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Errore di caricamento: {e}")

    with tab_quiz:
        if not api_key:
            st.info("Inserisci la chiave API per generare quiz interattivi istantanei per i tuoi alunni.")
        else:
            if st.button("🔄 Genera Domande di Verifica"):
                with st.spinner("Gemini sta elaborando i quesiti..."):
                    client = genai.Client(api_key=api_key)
                    prompt_quiz = f"Genera 3 domande a risposta multipla con soluzioni spiegate per verificare la comprensione degli studenti su: '{st.session_state.elemento_corrente}'."
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_quiz)
                    st.markdown(response.text)

    with tab_obiettivi:
        st.write("🎯 *Tracciamento Competenze Didattiche (Classe A050):*")
        st.checkbox("Comprensione della struttura tridimensionale dello specimen", value=True)
        st.checkbox("Capacità di correlazione tra microscopia e modello teorico", value=False)
        st.checkbox("Padronanza nell'esposizione delle metafore scientifiche", value=False)
        st.progress(33, text="Progresso Obiettivi della Lezione")

    st.markdown("---")
    st.caption("🧬 *OmniScience Studio Pro - Sviluppato per la massima precisione didattica.*")
