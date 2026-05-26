import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64

# 1. Configurazione della pagina (Interfaccia Dashboard ad ampio schermo)
st.set_page_config(page_title="Cell Architecture Studio", layout="wide", initial_sidebar_state="expanded")

# Stile CSS per emulare i colori pastello e l'eleganza della foto dell'utente
st.markdown("""
    <style>
    .stApp { background-color: #F8F6F0; } /* Sfondo avorio/crema rilassante */
    
    /* Stile per i blocchi bianchi delle colonne */
    div[data-testid="stColumn"] {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        min-height: 700px;
    }
    
    /* Personalizzazione dei titoli */
    h1, h2, h3 {
        color: #2C3E50;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-weight: 600;
    }
    
    /* Stile personalizzato per i pulsanti degli organelli */
    .stButton>button {
        background-color: #F0F4F2;
        color: #2C3E50;
        border-radius: 8px;
        border: 1px solid #E2ECE9;
        width: 100%;
        text-align: left;
        padding: 10px 15px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #DBE5E1;
        border-color: #CBDCD6;
        color: #111111;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERALE: Configurazione Chiave API ---
st.sidebar.header("⚙️ Impostazioni di Sistema")
st.sidebar.write("Inserisci la chiave per attivare l'Intelligenza Artificiale di Gemini.")
api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Ottienila gratuitamente su Google AI Studio")

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Come usare l'app in classe:**
1. Seleziona il tipo di cellula a sinistra.
2. Esplora il modello 3D al centro (ruota e zoomma).
3. Clicca sui pulsanti degli organelli a sinistra per aggiornare la scheda tecnica a destra tramite l'I.A.
""")

# --- INTESTAZIONE PRINCIPALE ---
st.title("🧫 Cell Architecture Studio")
st.caption("🔬 *Laboratorio Virtuale Interattivo di Biologia Celulare per le Scuole*")
st.markdown("<br>", unsafe_allow_html=True)

# --- INTERFACCIA A TRE COLONNE (Layout identico alla foto) ---
# Proporzioni: 22% Navigazione, 53% Modello 3D, 25% Scheda Informativa
col_nav, col_visualizzatore, col_info = st.columns([0.22, 0.53, 0.25], gap="large")

# ==========================================
# 1. COLONNA SINISTRA: Menu Organelli
# ==========================================
with col_nav:
    st.markdown("### 🗂️ CELL TYPES")
    tipo_cellula = st.selectbox(
        "Modello cellulare attivo:", 
        ["Cellula Vegetale (Plant Cell)", "Cellula Animale (Animal Cell)", "Procariote (Bacteria)"]
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("### 🧬 ORGANELLES")
    st.write("Seleziona una struttura da analizzare:")
    
    # Gestione dello stato del pulsante cliccato (Streamlit memorizza la scelta nel session_state)
    if 'organello_selezionato' not in st.session_state:
        st.session_state.organello_selezionato = "Nucleo"

    if st.button("🧬 Nucleus (Nucleo)"):
        st.session_state.organello_selezionato = "Nucleo"
    if st.button("🔋 Mitochondria (Mitocondri)"):
        st.session_state.organello_selezionato = "Mitocondrio"
    if st.button("🍃 Chloroplasts (Cloroplasti)"):
        st.session_state.organello_selezionato = "Cloroplasto"
    if st.button("📦 Golgi Apparatus (Apparato di Golgi)"):
        st.session_state.organello_selezionato = "Apparato di Golgi"
    if st.button("🧼 Vacuole (Vacuolo)"):
        st.session_state.organello_selezionato = "Vacuolo"
    if st.button("🛡️ Cell Wall (Parete Cellulare)"):
        st.session_state.organello_selezionato = "Parete Cellulare"

# ==========================================
# 2. COLONNA CENTRALE: Visualizzatore 3D Interattivo
# ==========================================
with col_visualizzatore:
    st.markdown(f"### 🌱 {tipo_cellula}")
    st.caption("Usa il mouse o il dito per ruotare l'immagine in tutte le dimensioni. Usa la rotella per lo zoom.")
    
    # Caricatore di file 3D (Se la prof ha un file specifico .glb, lo trascina qui)
    file_3d = st.file_uploader("Carica un file 3D personalizzato (.glb o .gltf)", type=["glb", "gltf"])
    
    if file_3d is not None:
        bytes_data = file_3d.getvalue()
        base64_3d = base64.b64encode(bytes_data).decode('utf-8')
        data_url = f"data:model/gltf-binary;base64,{base64_3d}"
    else:
        # Modello 3D di esempio di Google (se non viene caricato nulla, mostra questo per evitare errori)
        data_url = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"
    
    # Integrazione del componente nativo <model-viewer> di Google per il 3D fluido
    html_3d = f"""
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
    <div style="width: 100%; display: flex; justify-content: center;">
        <model-viewer src="{data_url}"
                      alt="Modello Biologico 3D"
                      camera-controls
                      auto-rotate
                      touch-action="pan-y"
                      style="width: 100%; height: 420px; background-color: #F8FAFC; border-radius: 12px; border: 1px solid #E2E8F0;">
        </model-viewer>
    </div>
    """
    components.html(html_3d, height=440)
    
    # Sezione Microscopio inferiore (Pannello secondario come nella foto)
    st.markdown("### 🔬 MICROSCOPE VIEWS")
    img_col1, img_col2 = st.columns(2)
    with img_col1:
        st.image("https://images.unsplash.com/photo-1576086213369-97a306d36557?auto=format&fit=crop&w=300&q=80", 
                 caption="Sezione al Microscopio Ottico (Esempio)")
    with img_col2:
        st.image("https://images.unsplash.com/photo-1532187863486-abf9d39d6618?auto=format&fit=crop&w=300&q=80", 
                 caption="Dettaglio a Scansione Elettronica (TEM)")

# ==========================================
# 3. COLONNA DESTRA: Infografica Dinamica con Gemini
# ==========================================
with col_info:
    organello_corrente = st.session_state.organello_selezionato
    st.markdown(f"### 📋 DETTAGLI: {organello_corrente.upper()}")
    
    if not api_key:
        st.warning("🔑 Inserisci la chiave API di Gemini nella barra laterale a sinistra per generare l'infografica didattica in tempo reale.")
        st.markdown("""
        **Anteprima Contenuto:**
        Seleziona un organello e inserisci la chiave. L'Intelligenza Artificiale compilerà automaticamente:
        - Dimensioni in micrometri ($\mu m$)
        - Funzione biologica principale
        - Metafora d'impatto per gli studenti
        - Una domanda per aprire il dibattito in classe
        """)
    else:
        # Quando la chiave è presente, interroghiamo Gemini 2.5 Flash
        with st.spinner(f"Gemini sta analizzando la struttura del {organello_corrente}..."):
            try:
                # Inizializzazione del client aggiornato (SDK 2026)
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                Sei una stimata Professoressa di Biologia delle scuole superiori. 
                Spiega l'organello '{organello_corrente}' nel contesto del modello '{tipo_cellula}'.
                
                Genera un testo formattato in Markdown elegante, che ricordi un'infografica editoriale. 
                Usa elenchi puntati ed emoji a tema scientifico. Segui tassativamente questa struttura:
                
                ### 📏 DATI STRUTTURALI
                - **Dimensioni medie:** [Fornisci il dato scientifico in micrometri o nanometri]
                - **Morfologia:** [Spiega brevemente la sua forma o membrana]
                
                ### 📝 FUNZIONE BIOLOGICA
                [Spiega in modo brillante e comprensibile a cosa serve, evidenziando le parole chiave in grassetto]
                
                ### 💡 LA METAFORA DIDATTICA
                [Crea un'analogia potente per i ragazzi, ad esempio: il nucleo come la centrale operativa/computer, i mitocondri come centrali elettriche, ecc.]
                
                ### ❓ SFIDA PER LA CLASSE
                [Formula una domanda intrigante o una curiosità bizzarra su questo organello per stimolare la discussione tra i banchi]
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                # Stampiamo il testo strutturato da Gemini nella colonna di destra
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Errore nella generazione dell'infografica: {e}")

    st.markdown("---")
    st.caption("🧬 *Sviluppato con amore per la didattica delle scienze.*")