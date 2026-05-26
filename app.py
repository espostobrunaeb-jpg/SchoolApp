import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64

# 1. CONFIGURAZIONE INTERFACCIA
st.set_page_config(page_title="OmniScience 3D Studio Pro", layout="wide", initial_sidebar_state="expanded")

if "tema_scelto" not in st.session_state:
    st.session_state.tema_scelto = "Modalità Scura (Consigliata)"

# --- BARRA LATERALE ---
st.sidebar.markdown("## ⚙️ IMPOSTAZIONI")
tema = st.sidebar.selectbox("🎨 Tema Visivo:", ["Modalità Scura (Consigliata)", "Modalità Chiara"], key="tema_selector")
st.session_state.tema_scelto = tema

api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Inserisci la chiave di Google AI Studio")

# --- INIEZIONE CSS PERSONALIZZATO ---
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
st.sidebar.info("💡 **Modalità Progettazione Attiva**: Lezione strutturata con modello 3D integrato e modulo di pianificazione didattica.")

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
    argomento = st.text_input("Argomento:", value="Nucleo Cellulare")
    
    st.markdown("---")
    st.markdown("### 🎯 TARGET")
    livello_scuola = st.selectbox("Grado scolastico:", ["Scuola Elementare", "Scuola Media", "Superiori (Biennio)", "Superiori (Triennio)", "Università"], index=3)
    profilo_studente = st.selectbox("Profilo:", ["Standard", "BES (Bisogni Educativi Speciali)", "DSA (Alta Leggibilità)"])
    
    st.markdown("---")
    st.markdown("### 📦 MODELLO 3D")
    file_3d = st.file_uploader("Carica file .glb:", type=["glb"])

# ==========================================
# COLONNA DI DESTRA: Visualizzatore 3D e Progettazione Didattica
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
    
    # 2. PROGETTAZIONE DIDATTICA (I Nuovi 6 Tab)
    st.markdown(f"## 📚 PROGETTAZIONE DIDATTICA: {argomento.upper()}")
    st.caption("Il framework metodologico della lezione, adattato tramite I.A. all'argomento scelto.")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "1. Prerequisiti", 
        "2. Competenze", 
        "3. Obiettivi", 
        "4. Inclusione", 
        "5. Valutazione", 
        "6. Collegamenti"
    ])
    
    # --- TAB 1: PREREQUISITI ---
    with tab1:
        st.markdown("""
        **Framework Metodologico Base:**
        Gli studenti dovrebbero già possedere alcune conoscenze di base:
        - Comprensione di testi informativi, narrativi o argomentativi.
        - Capacità di individuare parole chiave e concetti principali.
        - Uso essenziale del lessico disciplinare.
        - Capacità di lavorare in coppia o in piccolo gruppo.
        - Competenze digitali di base per l’uso di LIM, piattaforme condivise, mappe.
        """)
        if st.button("Genera Prerequisiti Specifici per l'argomento", key="btn_pre"):
            if api_key:
                with st.spinner("Generazione..."):
                    client = genai.Client(api_key=api_key)
                    prompt = f"Elenca 3 prerequisiti di conoscenza scientifica specifici che gli studenti di {livello_scuola} devono avere prima di affrontare la lezione su '{argomento}'."
                    st.markdown("---")
                    st.markdown(client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text)
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 2: COMPETENZE ATTESE ---
    with tab2:
        st.markdown("""
        **La lezione mira a sviluppare competenze disciplinari e trasversali.**
        Gli studenti saranno guidati a:
        - Comprendere e analizzare testi, documenti o materiali multimediali.
        - Individuare informazioni principali e secondarie.
        - Collegare l’argomento al contesto storico, culturale, sociale o geografico.
        - Utilizzare il lessico specifico della disciplina.
        - Confrontare punti di vista diversi e rielaborare in modo personale.
        - Collaborare con i compagni e usare strumenti digitali consapevolmente.
        """)
        if st.button("Genera Focus Competenze sull'argomento", key="btn_comp"):
            if api_key:
                with st.spinner("Generazione..."):
                    client = genai.Client(api_key=api_key)
                    prompt = f"Come si applicano le competenze di analisi e uso del lessico specifico per studenti di {livello_scuola} ({profilo_studente}) quando studiano '{argomento}'?"
                    st.markdown("---")
                    st.markdown(client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text)
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 3: OBIETTIVI DI APPRENDIMENTO ---
    with tab3:
        st.markdown(f"""
        **Al termine della lezione, gli studenti saranno in grado di:**
        - Riconoscere i concetti fondamentali relativi a **{argomento}**.
        - Comprendere il significato di testi, fonti o materiali proposti.
        - Analizzare elementi, cause, conseguenze, temi o parole chiave.
        - Collegare l’argomento al contesto disciplinare più ampio.
        - Rielaborare oralmente o per iscritto quanto appreso.
        - Argomentare una posizione personale, se coerente con la traccia.
        """)
        if st.button("Genera Traguardi Specifici", key="btn_ob"):
            if api_key:
                with st.spinner("Generazione..."):
                    client = genai.Client(api_key=api_key)
                    prompt = f"Scrivi 3 obiettivi di apprendimento operativi e misurabili (es. 'Saper descrivere...') specifici per l'argomento '{argomento}' per il target {livello_scuola} ({profilo_studente})."
                    st.markdown("---")
                    st.markdown(client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text)
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 4: INCLUSIONE E PERSONALIZZAZIONE ---
    with tab4:
        st.markdown("""
        **La progettazione tiene conto dei diversi bisogni degli studenti.**
        Per gli studenti con DSA/BES sono previsti:
        - Consegne chiare e scandite per punti; mappe concettuali; parole chiave.
        - Testi semplificati o ad alta leggibilità.
        - Tempi più distesi e possibilità di rispondere oralmente.
        - Uso di strumenti compensativi.
        - Valutazione centrata sui contenuti e sul percorso, non solo sulla forma.
        
        *La classe lavora secondo una logica inclusiva: non si semplifica il sapere, ma si diversificano le vie di accesso all’apprendimento.*
        """)
        if st.button("Genera Parole Chiave e Schema per BES/DSA", key="btn_inc"):
            if api_key:
                with st.spinner("Generazione..."):
                    client = genai.Client(api_key=api_key)
                    prompt = f"Crea un elenco puntato ad altissima leggibilità con le 5 parole chiave fondamentali per capire '{argomento}'. Affianca a ogni parola una definizione di 1 riga estremamente semplice."
                    st.markdown("---")
                    st.markdown(client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text)
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 5: VALUTAZIONE ---
    with tab5:
        st.markdown("""
        **La valutazione sarà prevalentemente formativa e terrà conto di:**
        Partecipazione, comprensione dei contenuti, individuazione concetti chiave, uso del lessico disciplinare, collaborazione, capacità di collegamento, rielaborazione e rispetto della consegna.
        
        **Rubrica di Valutazione:**
        - **Base:** comprende solo gli elementi essenziali.
        - **Intermedio:** comprende e organizza le informazioni principali.
        - **Avanzato:** collega, interpreta e usa un lessico adeguato.
        - **Eccellente:** rielabora criticamente e propone collegamenti personali pertinenti.
        """)
        if st.button("Genera Prova di Verifica Formativa", key="btn_val"):
            if api_key:
                with st.spinner("Generazione..."):
                    client = genai.Client(api_key=api_key)
                    prompt = f"Crea una breve prova di verifica formativa su '{argomento}' per studenti di {livello_scuola} ({profilo_studente}). Includi 2 domande a risposta breve e 1 domanda di ragionamento/collegamento."
                    st.markdown("---")
                    st.markdown(client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text)
            else: st.warning("Inserisci la API Key a sinistra.")

    # --- TAB 6: COLLEGAMENTI INTERDISCIPLINARI ---
    with tab6:
        st.write("Esplorazione delle connessioni tra materie per una visione sistemica del sapere.")
        if st.button("Genera Collegamenti Interdisciplinari", key="btn_coll"):
            if api_key:
                with st.spinner("Generazione..."):
                    client = genai.Client(api_key=api_key)
                    prompt = f"Suggerisci 3 collegamenti interdisciplinari affascinanti partendo dall'argomento '{argomento}' (es. collegamenti con Storia, Letteratura, Fisica, o Ed. Civica) per studenti di {livello_scuola}."
                    st.markdown("---")
                    st.markdown(client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text)
            else: st.warning("Inserisci la API Key a sinistra.")
