import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64

# 1. Configurazione della pagina (Dashboard Widescreen)
st.set_page_config(page_title="OmniScience 3D Studio", layout="wide", initial_sidebar_state="expanded")

# Gestione dello stato del tema prima di caricare il CSS per evitare sfarfallii
if "tema_scelto" not in st.session_state:
    st.session_state.tema_scelto = "Modalità Scura (Consigliata)"

# --- INPUT BARRA LATERALE (I CONTROLLI VENGONO INSERITI DOPO IL CSS PERCORRETTO) ---
st.sidebar.markdown("## ⚙️ CONFIGURAZIONE")
tema = st.sidebar.selectbox("🎨 Scegli il Tema visivo:", ["Modalità Scura (Consigliata)", "Modalità Chiara"], key="tema_selector")
st.session_state.tema_scelto = tema

api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Inserisci la chiave ottenuta da Google AI Studio")

# --- INIEZIONE DEL CSS CORRETTO E COERENTE PER ENTRAMBI I TEMI ---
if st.session_state.tema_scelto == "Modalità Scura (Consigliata)":
    st.markdown("""
        <style>
        /* Sfondo principale dell'applicazione */
        .stApp { background-color: #0f0f0f !important; color: #ffffff !important; }
        
        /* FORZATURA TOTALE DELLA BARRA LATERALE IN MODALITÀ SCURA */
        section[data-testid="stSidebar"] { background-color: #161616 !important; }
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label {
            color: #ffffff !important;
        }
        /* Correzione del testo dentro i box informativi (st.info / st.warning) nella barra laterale */
        section[data-testid="stSidebar"] div[data-testid="stNotification"] p {
            color: #0f172a !important; /* Testo scuro dentro i banner colorati per staccare dallo sfondo del banner */
            font-weight: 500;
        }
        
        /* Pannelli stile carte di laboratorio scure */
        div[data-testid="stColumn"] {
            background-color: #161616 !important;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #262626;
            min-height: 720px;
        }
        
        h1, h2, h3 { color: #00d4aa !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        p, li, span, label { color: #e0e0e0 !important; }
        
        /* Stile pulsanti di selezione */
        .stButton>button {
            background-color: #1f1f1f !important;
            color: #ffffff !important;
            border-radius: 6px;
            border: 1px solid #333333 !important;
            width: 100%;
            text-align: left;
            padding: 10px 14px;
            font-weight: 500;
        }
        .stButton>button:hover { background-color: #00d4aa !important; color: #0f0f0f !important; border-color: #00d4aa !important; }
        
        /* Correzione selettori e box di upload testo in nero */
        div[data-baseweb="select"] > div { background-color: #1f1f1f !important; color: #ffffff !important; border-color: #333333 !important; }
        div[data-testid="stFileUploader"] section { background-color: #1f1f1f !important; border: 1px dashed #444444 !important; color: #ffffff !important; }
        input { background-color: #1f1f1f !important; color: #ffffff !important; }
        </style>
    """, unsafe_allow_html=True)
else:
    # MODALITÀ CHIARA COMPLETAMENTE RIVISTA PER MASSIMO CONTRASTO ALLA LIM
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa !important; color: #212529 !important; }
        
        /* FORZATURA BARRA LATERALE IN MODALITÀ CHIARA */
        section[data-testid="stSidebar"] { background-color: #e9ecef !important; }
        section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label {
            color: #212529 !important;
        }
        
        /* Pannelli stile carte di laboratorio chiare */
        div[data-testid="stColumn"] {
            background-color: #ffffff !important;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #dee2e6 !important;
            min-height: 720px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        h1, h2, h3 { color: #007a60 !important; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        p, li, span, label { color: #212529 !important; }
        
        /* Stile pulsanti di selezione in modalità chiara */
        .stButton>button {
            background-color: #f1f3f5 !important;
            color: #212529 !important;
            border-radius: 6px;
            border: 1px solid #ced4da !important;
            width: 100%;
            text-align: left;
            padding: 10px 14px;
            font-weight: 500;
        }
        .stButton>button:hover { background-color: #007a60 !important; color: #ffffff !important; border-color: #007a60 !important; }
        
        /* Input e caricatori in modalità chiara */
        div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #212529 !important; border-color: #ced4da !important; }
        div[data-testid="stFileUploader"] section { background-color: #ffffff !important; border: 1px dashed #ced4da !important; color: #212529 !important; }
        input { background-color: #ffffff !important; color: #212529 !important; }
        </style>
    """, unsafe_allow_html=True)

# Contenuto informativo della barra laterale
st.sidebar.markdown("---")
st.sidebar.info("""
**Guida rapida per la Classe A050:**
1. Scegli la **Materia** e l'argomento a sinistra.
2. Trascina al centro un file 3D (.glb) coerente (es. una molecola, un vulcano o un tessuto).
3. Clicca sui dettagli a sinistra per aggiornare l'infografica dell'I.A. a destra.
""")

# --- INTESTAZIONE PRINCIPALE ---
st.title("🧪 OmniScience 3D Studio")
st.caption("🔬 *Laboratorio Virtuale di Scienze Naturali, Chimica e Geografia - Classe di Concorso A050*")
st.markdown("<br>", unsafe_allow_html=True)

# --- LAYOUT A TRE COLONNE ---
col_menu, col_3d, col_ai = st.columns([0.22, 0.53, 0.25], gap="large")

# ==========================================
# COLONNA 1 (SINISTRA): Selezionatore di Materia e Strutture
# ==========================================
with col_menu:
    st.markdown("### 📚 MATERIA")
    materia = st.selectbox("Seleziona l'ambito disciplinare:", ["Biologia", "Chimica", "Scienze della Terra"])
    
    st.markdown("---")
    st.markdown("### 🔍 ELEMENTO SOTTO ESAME")
    
    # Inizializziamo la variabile di stato per l'elemento da analizzare
    if 'elemento_corrente' not in st.session_state:
        st.session_state.elemento_corrente = "Nucleo Cellulare"

    # Cambiamo le opzioni dei pulsanti dinamicamente in base alla materia scelta
    if materia == "Biologia":
        st.write("Strutture biologiche tipiche:")
        if st.button("🧫 Nucleo Cellulare"): st.session_state.elemento_corrente = "Nucleo Cellulare"
        if st.button("🔋 Mitocondrio"): st.session_state.elemento_corrente = "Mitocondrio"
        if st.button("🧬 Doppia Elica DNA"): st.session_state.elemento_corrente = "Doppia Elica del DNA"
        if st.button("🌿 Cloroplasto"): st.session_state.elemento_corrente = "Cloroplasto"
        
    elif materia == "Chimica":
        st.write("Modelli chimici e molecolari:")
        if st.button("💧 Molecola dell'Acqua ($H_2O$)"): st.session_state.elemento_corrente = "Molecola dell'Acqua (H2O)"
        if st.button("💎 Reticolo del Diamante"): st.session_state.elemento_corrente = "Reticolo Cristallino del Diamante"
        if st.button("⚛️ Atomo di Bohr"): st.session_state.elemento_corrente = "Modello Atomico"
        if st.button("🔥 Legame Covalente"): st.session_state.elemento_corrente = "Legame Covalente"
        
    elif materia == "Scienze della Terra":
        st.write("Fenomeni e strutture geologiche:")
        if st.button("🌋 Vulcano (Sezione Interna)"): st.session_state.elemento_corrente = "Sezione Interna di un Vulcano"
        if st.button("🌍 Strati della Terra"): st.session_state.elemento_corrente = "Strati interni della Terra"
        if st.button("⛰️ Faglia Tettonica"): st.session_state.elemento_corrente = "Faglia Tettonica e Movimento delle Placche"
        if st.button("💎 Silicati (Reticolo)"): st.session_state.elemento_corrente = "Struttura cristallina dei Silicati"

    st.markdown("<br>", unsafe_allow_html=True)
    # Input libero per argomenti Jolly
    input_libero = st.text_input("✍️ Oppure scrivi un argomento personalizzato:", placeholder="Es. Apparato di Golgi, Legame Ionico...")
    if input_libero:
        st.session_state.elemento_corrente = input_libero

# ==========================================
# COLONNA 2 (CENTRO): Il Viewport 3D Universale
# ==========================================
with col_3d:
    elemento = st.session_state.elemento_corrente
    st.markdown(f"### 🌐 MODELLO 3D: {elemento.upper()}")
    st.caption("Trascina per ruotare l'oggetto in tutte le dimensions, usa la rotella per lo zoom.")
    
    # Caricatore universale di file .glb
    file_3d = st.file_uploader("Carica il file .glb corrispondente all'argomento della lezione", type=["glb"])
    
    if file_3d is not None:
        bytes_data = file_3d.getvalue()
        base64_3d = base64.b64encode(bytes_data).decode('utf-8')
        data_url = f"data:model/gltf-binary;base64,{base64_3d}"
    else:
        # Modello neutro di default se nessun file viene caricato
        data_url = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"

    # Colore di sfondo del visualizzatore 3D adattivo in base al tema scelto
    bg_viewer = "#111111" if st.session_state.tema_scelto == "Modalità Scura (Consigliata)" else "#ffffff"
    border_viewer = "#333333" if st.session_state.tema_scelto == "Modalità Scura (Consigliata)" else "#ced4da"

    # Renderizzazione del visualizzatore 3D fluido di Google
    html_code = f"""
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
    <div style="width: 100%; display: flex; justify-content: center;">
        <model-viewer src="{data_url}"
                      alt="Modello Scientifico 3D"
                      camera-controls
                      auto-rotate
                      touch-action="pan-y"
                      style="width: 100%; height: 430px; background-color: {bg_viewer}; border-radius: 8px; border: 1px solid {border_viewer};">
        </model-viewer>
    </div>
    """
    components.html(html_code, height=440)
    
    # Sezione immagini di supporto scientifico inferiore
    st.markdown("### 📸 SUPPORTI DIDATTICI INTEGRATIVI")
    st.write("💡 *Suggerimento per la lezione: proietta al centro il modello 3D e confrontalo con gli schemi dei tuoi libri di testo.*")

# ==========================================
# COLONNA 3 (DESTRA): Infografica Dinamica con Gemini
# ==========================================
with col_ai:
    st.markdown(f"### 📋 DASHBOARD DIDATTICA")
    st.info(f"Focus su: **{elemento}** ({materia})")
    
    if not api_key:
        st.warning("🔑 Inserisci la chiave API nella barra laterale a sinistra per sbloccare l'I.A.")
    else:
        with st.spinner(f"Gemini sta elaborando la scheda didattica per {elemento}..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                Sei una brillante docente di Scienze Naturali, Chimica e Geografia per le scuole superiori (Classe A050).
                Spiega l'argomento '{elemento}' inserito nell'ambito disciplinare '{materia}'.
                
                Crea un testo eccezionalmente chiaro, formattato in Markdown per sembrare un'infografica. 
                Usa elenchi puntati ed emoji pertinenti. Segui rigidamente questa struttura:
                
                ### 📐 PROPRIETÀ E CARATTERISTICHE
                - **Natura scientifica:** [Descrivi cos'è brevemente]
                - **Scala di grandezza:** [Indica l'ordine di grandezza]
                
                ### 📝 PRINCIPIO DI FUNZIONAMENTO / SIGNIFICATO
                [Spiega come funziona o perché è fondamentale questo elemento, massimo 4 righe, evidenzia in grassetto i termini chiave]
                
                ### 💡 LA METAFORA ADATTA AI RAGAZZI
                [Fornisci un'analogia potente o una metafora del mondo quotidiano per far imprimere il concetto nella mente degli studenti]
                
                ### ❓ QUESITO DA COMPITO IN CLASSE / DIBATTITO
                [Formula una domanda stimolante o un piccolo 'mistero' per stimolare la discussione tra i banchi]
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Errore nella connessione con Gemini: {e}")

    st.markdown("---")
    st.caption("🔬 *OmniScience Studio - Uno strumento pronto per l'intera classe A050.*")
