import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64

# 1. CONFIGURAZIONE INTERFACCIA (Dashboard ottimizzata per LIM)
st.set_page_config(page_title="OmniScience 3D Studio Pro", layout="wide", initial_sidebar_state="expanded")

# Gestione dello stato del tema prima di caricare il CSS
if "tema_scelto" not in st.session_state:
    st.session_state.tema_scelto = "Modalità Scura (Consigliata)"

# --- BARRA LATERALE: TEMA E SICUREZZA ---
st.sidebar.markdown("## ⚙️ IMPOSTAZIONI")
tema = st.sidebar.selectbox("🎨 Tema Visivo:", ["Modalità Scura (Consigliata)", "Modalità Chiara"], key="tema_selector")
st.session_state.tema_scelto = tema

api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Inserisci la chiave di Google AI Studio")

# --- INIEZIONE CSS PERSONALIZZATO (Dark/Light Mode coerente) ---
if st.session_state.tema_scelto == "Modalità Scura (Consigliata)":
    st.markdown("""
        <style>
        .stApp { background-color: #0f0f0f !important; color: #ffffff !important; }
        section[data-testid="stSidebar"] { background-color: #161616 !important; }
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #ffffff !important; }
        section[data-testid="stSidebar"] div[data-testid="stNotification"] p { color: #0f172a !important; font-weight: 500; }
        
        div[data-testid="stColumn"] {
            background-color: #161616 !important;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #262626;
        }
        
        h1, h2, h3 { color: #00d4aa !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        p, li, span, label { color: #e0e0e0 !important; }
        
        .stButton>button {
            background-color: #1f1f1f !important;
            color: #ffffff !important;
            border-radius: 6px;
            border: 1px solid #333333 !important;
            width: 100%; padding: 10px; font-weight: 500;
        }
        .stButton>button:hover { background-color: #00d4aa !important; color: #0f0f0f !important; border-color: #00d4aa !important; }
        
        div[data-baseweb="popover"], div[role="listbox"], li[role="option"] { background-color: #161616 !important; color: #ffffff !important; }
        li[role="option"]:hover { background-color: #00d4aa !important; color: #0f0f0f !important; }
        div[data-baseweb="select"] > div { background-color: #1f1f1f !important; color: #ffffff !important; border-color: #333333 !important; }
        div[data-testid="stFileUploader"] section { background-color: #1f1f1f !important; border: 1px dashed #444444 !important; color: #ffffff !important; }
        input { background-color: #1f1f1f !important; color: #ffffff !important; }
        
        button[data-baseweb="tab"] { color: #8a94a6 !important; font-weight: 600 !important; font-size: 16px !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #00d4aa !important; border-bottom-color: #00d4aa !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa !important; color: #212529 !important; }
        section[data-testid="stSidebar"] { background-color: #e9ecef !important; }
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label { color: #212529 !important; }
        
        div[data-testid="stColumn"] {
            background-color: #ffffff !important;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #dee2e6 !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        h1, h2, h3 { color: #007a60 !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        p, li, span, label { color: #212529 !important; }
        
        .stButton>button {
            background-color: #f1f3f5 !important;
            color: #212529 !important;
            border-radius: 6px;
            border: 1px solid #ced4da !important;
            width: 100%; padding: 10px; font-weight: 500;
        }
        .stButton>button:hover { background-color: #007a60 !important; color: #ffffff !important; border-color: #007a60 !important; }
        
        div[data-baseweb="popover"], div[role="listbox"], li[role="option"] { background-color: #ffffff !important; color: #212529 !important; }
        li[role="option"]:hover { background-color: #007a60 !important; color: #ffffff !important; }
        div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #212529 !important; border-color: #ced4da !important; }
        div[data-testid="stFileUploader"] section { background-color: #ffffff !important; border: 1px dashed #ced4da !important; color: #212529 !important; }
        input { background-color: #ffffff !important; color: #212529 !important; }
        
        button[data-baseweb="tab"] { color: #64748b !important; font-weight: 600 !important; font-size: 16px !important; }
        button[data-baseweb="tab"][aria-selected="true"] { color: #007a60 !important; border-bottom-color: #007a60 !important; }
        </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **OmniScience Universale**: Layout a scorrimento ottimizzato per proiezioni su LIM scolastiche.")

# --- INTESTAZIONE PRINCIPALE ---
st.title("🧪 OmniScience 3D Studio")
st.caption("🔬 *Laboratorio Virtuale di Scienze Naturali, Chimica e Geografia - Classe di Concorso A050*")
st.markdown("<br>", unsafe_allow_html=True)

# --- NUOVO LAYOUT A DUE COLONNE (25% Pannello di Input | 75% Visualizzatore e IA sotto) ---
col_sinistra, col_destra_principale = st.columns([0.25, 0.75], gap="large")

# ==========================================
# COLONNA DI SINISTRA: Solo gestione dell'argomento
# ==========================================
with col_sinistra:
    st.markdown("### ✍️ IMPOSTA LA LEZIONE")
    st.write("Digita l'oggetto o la struttura che vuoi spiegare oggi alla classe:")
    
    argomento = st.text_input("Oggetto della spiegazione:", value="Nucleo Cellulare", help="Es. Mitocondrio, Molecola dell'Acqua, Vulcano, Faglia Tettonica...")
    
    st.markdown("---")
    st.markdown("### 📦 CARICA MODELLO 3D")
    file_3d = st.file_uploader("Trascina qui il file .glb dell'argomento (Opzionale):", type=["glb"])

# ==========================================
# COLONNA DI DESTRA (PRINCIPALE): Espositore sopra e IA sotto
# ==========================================
with col_destra_principale:
    
    # 1. L'ESPOSITORE 3D (Ora occupa molto più spazio visivo sul grande schermo)
    st.markdown(f"## 🌐 ESPOSITORE GENERALE: {argomento.upper()}")
    
    if file_3d is not None:
        bytes_data = file_3d.getvalue()
        base64_3d = base64.b64encode(bytes_data).decode('utf-8')
        data_url = f"data:model/gltf-binary;base64,{base64_3d}"
    else:
        # Modello di prova standard (Astronauta di Google) se non c'è un file caricato
        data_url = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"

    bg_viewer = "#111111" if st.session_state.tema_scelto == "Modalità Scura (Consigliata)" else "#ffffff"
    border_viewer = "#333333" if st.session_state.tema_scelto == "Modalità Scura (Consigliata)" else "#ced4da"

    html_code = f"""
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
    <div style="width: 100%; display: flex; justify-content: center;">
        <model-viewer src="{data_url}"
                      alt="Modello Scientifico 3D"
                      camera-controls
                      auto-rotate
                      touch-action="pan-y"
                      style="width: 100%; height: 450px; background-color: {bg_viewer}; border-radius: 12px; border: 1px solid {border_viewer};">
        </model-viewer>
    </div>
    """
    components.html(html_code, height=460)
    st.caption("💡 *Consiglio per gli studenti:* Trascina con il mouse/dito per ruotare in ogni dimensione, usa la rotella per lo zoom.")
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    # 2. IL PANNELLO AI TUTOR SPOSTATO SOTTO (Organizzato in comodi Tab per la LIM)
    st.markdown("## 🤖 ASSISTENTE DIDATTICO GEMINI AI")
    
    tab_infografica, tab_microscopio, tab_confronto, tab_quiz = st.tabs([
        "📋 Infografica Riassuntiva", 
        "🔬 Guida al Microscopio (Dinamica)", 
        "⚖️ Modalità Confronto", 
        "❓ Quiz Rapido per la Classe"
    ])
    
    # --- TAB 1: INFOGRAFICA ---
    with tab_infografica:
        if not api_key:
            st.warning("🔑 Inserisci la tua Gemini API Key nella barra laterale sinistra per sbloccare i contenuti dell'I.A.")
        else:
            with st.spinner(f"Gemini sta elaborando l'infografica per {argomento}..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    Sei una docente di Scienze Superiori (classe A050). Spiega l'argomento '{argomento}'.
                    Crea un testo formattato in Markdown simile a un'infografica editoriale. Usa molte emoji e titoli chiari.
                    Includi: Proprietà e caratteristiche principali, Scala di grandezza reale, e una Metafora potente per farlo capire ai ragazzi.
                    """
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Errore Gemini: {e}")

    # --- TAB 2: GUIDA AL MICROSCOPIO (Ora totalmente dinamica!) ---
    with tab_microscopio:
        if not api_key:
            st.warning("🔑 Inserisci la tua Gemini API Key per sbloccare la simulazione.")
        else:
            with st.spinner(f"Gemini sta generando la guida all'osservazione per {argomento}..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt_mic = f"""
                    Sei un tecnico di laboratorio biologico e geologico. Spiega agli studenti cosa vedrebbero se analizzassero '{argomento}' al microscopio.
                    Dividi la risposta in:
                    1. 🔬 **OSSERVAZIONE AL MICROSCOPIO OTTICO:** (Cosa si vede, quali coloranti usare se necessari, ingrandimento consigliato es. 400x).
                    2. 🧬 **OSSERVAZIONE AL MICROSCOPIO ELETTRONICO (SEM/TEM):** (Quali dettagli ultrastrutturali emergono ad altissimo ingrandimento).
                    Sii molto visivo nelle descrizioni testuali.
                    """
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_mic)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Errore Gemini: {e}")

    # --- TAB 3: MODALITÀ CONFRONTO (Dinamica su input dell'utente) ---
    with tab_confronto:
        st.write("⚖️ **Compara due strutture scientifiche in tempo reale**")
        argomento_confronto = st.text_input("Inserisci il secondo argomento con cui fare il confronto:", placeholder="Es. Cellula Animale, Legame Ionico, Vulcano...")
        
        if argomento_confronto:
            if not api_key:
                st.warning("🔑 Inserisci la chiave API per generare il confronto.")
            else:
                with st.spinner(f"Gemini sta mettendo a confronto {argomento} e {argomento_confronto}..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt_comp = f"""
                        Sei una professoressa di scienze. Crea una tabella comparativa in Markdown confrontando '{argomento}' e '{argomento_confronto}'.
                        Sotto la tabella, elenca le 3 differenze fondamentali e le eventuali analogie strutturali o funzionali.
                        """
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_comp)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Errore Gemini: {e}")
        else:
            st.info("💡 Scrivi un secondo argomento nel riquadro sopra per avviare l'analisi comparativa generata dall'I.A.")

    # --- TAB 4: QUIZ INTERATTIVO ---
    with tab_quiz:
        if not api_key:
            st.warning("🔑 Inserisci la chiave API per sbloccare i quiz.")
        else:
            if st.button("🔄 Genera 3 Domande per la Classe"):
                with st.spinner("Gemini sta preparando i quesiti..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt_quiz = f"Crea un mini-quiz di 3 domande a risposta multipla su '{argomento}' adatto a studenti delle superiori. Includi le soluzioni spiegate in fondo nascoste o chiaramente indicate."
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt_quiz)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Errore Gemini: {e}")

    st.markdown("---")
    st.caption("🔬 *OmniScience Studio Pro v3.0 - Layout a scorrimento verticale adattivo.*")
