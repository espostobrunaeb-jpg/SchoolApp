import streamlit as st
import streamlit.components.v1 as components
from google import genai
import base64

# Configurazione della pagina in modalità Dashboard (Widescreen)
st.set_page_config(page_title="Bruna Esposto 3D Studio SchoolApp", layout="wide", initial_sidebar_state="expanded")

# STILE CSS (Ripreso esattamente dal look-and-feel dell'articolo: Dark mode, dettagli teal/azzurro)
st.markdown("""
    <style>
    .stApp { background-color: #0f0f0f; color: #ffffff; } /* Sfondo scurissimo */
    
    /* Pannelli stile carte tecnologiche */
    div[data-testid="stColumn"] {
        background-color: #1a1a1a;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2a2a2a;
        min-height: 680px;
    }
    
    h1, h2, h3 { color: #00d4aa !important; font-family: 'Courier New', sans-serif; } /* Titoli Teal */
    p, li { color: #e0e0e0; }
    
    /* Stile per i pulsanti degli organelli */
    .stButton>button {
        background-color: #222222;
        color: #ffffff;
        border-radius: 6px;
        border: 1px solid #333333;
        width: 100%;
        text-align: left;
        padding: 12px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00d4aa;
        color: #0f0f0f;
        border-color: #00d4aa;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERALE CONFIGURAZIONE ---
st.sidebar.markdown("## ⚙️ CONTROLI SYSTEM")
api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Inserisci la chiave per attivare l'I.A.")

st.sidebar.markdown("---")
st.sidebar.info("""
**Manuale della Prof:**
1. Scegli il tipo di cellula a sinistra.
2. Interagisci con il modello 3D al centro.
3. Clicca su un organello a sinistra: la scheda tecnica a destra verrà compilata all'istante dall'I.A. di Gemini.
""")

# --- INTESTAZIONE APP ---
st.title("🔬 Cell Architecture Studio")
st.caption("Pipeline ispirata alla guida 'The AI Leverage' - Sviluppata per la didattica delle scienze")
st.markdown("<br>", unsafe_allow_html=True)

# --- LAYOUT A 3 COLONNE (20% | 55% | 25%) ---
col_sidebar, col_viewport, col_details = st.columns([0.20, 0.55, 0.25], gap="medium")

# ==========================================
# COLONNA 1 (SINISTRA): Navigazione Tipi e Organelli
# ==========================================
with col_sidebar:
    st.markdown("### 🗂️ CELL TYPES")
    tipo_cellula = st.selectbox("Seleziona modello:", ["Plant Cell (Vegetale)", "Animal Cell (Animale)", "Neuron (Neurone)"])
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 🧬 ORGANELLES")
    st.write("Seleziona una struttura da analizzare:")
    
    if 'selezionato' not in st.session_state:
        st.session_state.selezionato = "Nucleo"

    if st.button("🧬 Nucleus"): st.session_state.selezionato = "Nucleo"
    if st.button("🔋 Mitochondria"): st.session_state.selezionato = "Mitocondrio"
    if st.button("🍃 Chloroplasts"): st.session_state.selezionato = "Cloroplasto"
    if st.button("📦 Golgi Apparatus"): st.session_state.selezionato = "Apparato di Golgi"
    if st.button("🧼 Vacuole"): st.session_state.selezionato = "Vacuolo"

# ==========================================
# COLONNA 2 (CENTRO): Il Viewport 3D Interattivo
# ==========================================
with col_viewport:
    st.markdown(f"### 🌐 VIEWPORT: {tipo_cellula.upper()}")
    
    # Caricatore file .glb (Trascina qui il file scaricato da Tripo3D)
    file_3d = st.file_uploader("Carica il file .glb della cellula", type=["glb"])
    
    if file_3d is not None:
        bytes_data = file_3d.getvalue()
        base64_3d = base64.b64encode(bytes_data).decode('utf-8')
        data_url = f"data:model/gltf-binary;base64,{base64_3d}"
    else:
        # Se non metti file, mostra un modello di prova (Astronauta di Google) per non lasciare vuoto
        data_url = "https://modelviewer.dev/shared-assets/models/Astronaut.glb"

    # Inclusione di <model-viewer> consigliato per la massima fluidità
    html_code = f"""
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
    <model-viewer src="{data_url}"
                  alt="Modello Cellulare 3D"
                  camera-controls
                  auto-rotate
                  touch-action="pan-y"
                  style="width: 100%; height: 400px; background-color: #111111; border-radius: 8px;">
    </model-viewer>
    """
    components.html(html_code, height=410)
    
    # Sezione inferiore: Microscope view simulator (Thumbnails)
    st.markdown("### 🔬 MICROSCOPE SIMULATION VIEW")
    t1, t2 = st.columns(2)
    with t1:
        st.image("https://images.unsplash.com/photo-1576086213369-97a306d36557?w=300", caption="Vista Ottica")
    with t2:
        st.image("https://images.unsplash.com/photo-1532187863486-abf9d39d6618?w=300", caption="Vista Elettronica")

# ==========================================
# COLONNA 3 (DESTRA): Pannello Dettagli Organello (Infografica con Gemini)
# ==========================================
with col_details:
    org = st.session_state.selezionato
    st.markdown(f"### 📋 DETAILS: {org.upper()}")
    
    if not api_key:
        st.warning("🔑 Inserisci la tua Gemini API Key nella barra laterale a sinistra per generare i dettagli in tempo reale.")
    else:
        with st.spinner("Generazione scheda tecnica via Gemini..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = f"""
                Sei un assistente AI integrato in un software di biologia per la scuola.
                Genera i dettagli per l'organello '{org}' nella '{tipo_cellula}'.
                
                Formatta l'output rigorosamente in Markdown così (usa le emoji indicate):
                
                #### 📏 DETTAGLI STRUTTURALI
                - **Dimensioni:** [Fornisci dati realistici]
                - **Presenza:** [In quali cellule si trova]
                
                #### 📝 NOTE BIOLOGICHE
                [Fornisci una spiegazione scientifica ma chiarissima di massimo 3 righe]
                
                #### 💡 FUN FACT / METAFORA
                [Fornisci una curiosità o una metafora per spiegare il concetto agli studenti]
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Errore Gemini: {e}")
