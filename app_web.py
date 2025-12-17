import json
import os

import requests
import streamlit as st
import streamlit.components.v1 as components

# --- Page Configuration ---
st.set_page_config(
    page_title="Iris Species Predictor",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- CSS: Dark Theme, Layout Fixes & Card Styling ---
st.markdown(
    """
    <style>
        /* 1. AGGRESSIVE TOP SPACING REMOVAL */
        header[data-testid="stHeader"] {
            display: none;
        }
        .main .block-container {
            padding-top: 1rem !important; /* Minimal padding */
            padding-bottom: 1rem !important;
            max-width: 95% !important;
        }
        div[data-testid="stAppViewContainer"] {
            overflow-x: hidden;
        }

        /* 2. GLOBAL DARK THEME */
        .stApp {
            background-color: #0F172A; /* Slate 900 */
            color: #F8FAFC;
        }
        
        /* 3. CENTERED TITLE */
        h1 {
            text-align: center;
            font-size: 2.5rem !important;
            padding-bottom: 0.5rem;
            margin-top: -40px !important; /* Pull title up */
            background: linear-gradient(to right, #a78bfa, #2dd4bf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* 4. CARD STYLING VIA CSS SELECTORS */
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
            background-color: #1E293B; /* Slate 800 */
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            height: 100%;
        }

        /* 5. BUTTON STYLING */
        .stButton button {
            width: 100%;
            background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
            color: white;
            font-weight: bold;
            padding: 0.6rem;
            border-radius: 8px;
            border: none;
            margin-top: 25px;
        }
        .stButton button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
        }

        /* 6. IMAGE CONTAINER (UPDATED) */
        .fixed-img-container {
            margin: 20px auto;
            width: 500px;
            /* Removed fixed height and black background */
            border-radius: 8px;
            border: 1px solid #4ade80;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .fixed-img {
            width: 500px;
            height: 500px;
        }
        
        /* Slider Labels */
        .stSlider label {
            color: #e2e8f0 !important;
            font-weight: 600;
            font-size: 0.9rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Helper: Python Flower SVG Generator (Initial State) ---
def get_flower_svg_container(sl, sw, pl, pw):
    scale = 18
    cx, cy = 150, 150
    svg = f'<svg width="300" height="300" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg" style="background:#1E293B; border-radius:12px;">'
    for angle in [0, 120, 240]:
        svg += f'<ellipse cx="{cx}" cy="{cy}" rx="{(sl * scale) / 2}" ry="{(sw * scale) / 2}" fill="#84cc16" fill-opacity="0.5" stroke="#4d7c0f" stroke-width="1" transform="rotate({angle} {cx} {cy})" />'
    for angle in [60, 180, 300]:
        svg += f'<ellipse cx="{cx}" cy="{cy}" rx="{(pl * scale) / 2}" ry="{(pw * scale) / 2}" fill="#a855f7" fill-opacity="0.8" stroke="#6b21a8" stroke-width="1" transform="rotate({angle} {cx} {cy})" />'
    svg += f'<circle cx="{cx}" cy="{cy}" r="6" fill="#fbbf24" /></svg>'
    return f'<div id="flower-svg-container" style="display:flex; justify-content:center;">{svg}</div>'


# --- Main Application Layout ---

st.title("Iris Species Predictor")

# Main Columns
left_col, right_col = st.columns([1, 1], gap="large")

# --- LEFT COLUMN: Inputs & Simulation ---
with left_col:
    st.markdown("### 1. Configure Geometry")

    # Sliders (UPDATED DEFAULTS from image_3.png)
    c1, c2 = st.columns(2)
    with c1:
        # Default: 6.80
        sl = st.slider("Sepal Length (cm)", 4.0, 8.0, 6.8, 0.1, key="sl")
        # Default: 4.50
        pl = st.slider("Petal Length (cm)", 1.0, 7.0, 4.5, 0.1, key="pl")
    with c2:
        # Default: 2.80
        sw = st.slider("Sepal Width (cm)", 2.0, 4.5, 2.8, 0.1, key="sw")
        # Default: 0.70
        pw = st.slider("Petal Width (cm)", 0.1, 2.5, 0.7, 0.1, key="pw")

    st.markdown("---")

    # SVG Display Container
    st.markdown(get_flower_svg_container(sl, sw, pl, pw), unsafe_allow_html=True)

    # Predict Button (CENTERED)
    # We use columns to center the button
    bc1, bc2, *bc3 = st.columns([2, 1, 1, 1])
    with bc2:
        predict_clicked = st.button("RUN PREDICTION")

# --- RIGHT COLUMN: Results ---
with right_col:
    st.markdown("### 2. Analysis Result")

    if not predict_clicked:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 10px;">
                <h2 style="color: #4ade80; margin: 0; font-size: 1.8rem; opacity:0.5;">Awaiting Prediction</h2>
            </div>  
            <div class="fixed-img-container">
                <div style="text-align: center; color: #94a3b8; margin-top: 15px;">
                    <svg width="50" height="50" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="margin: 0 auto; opacity:0.5;">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path>
                    </svg>
                    <p style="margin-top: 15px; font-size: 0.9rem;">Adjust sliders to preview.<br>Click RUN to analyze.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Active State
        features = [sl, sw, pl, pw]
        payload = {"features": features}
        api_url = os.environ.get("API_URL", "http://localhost:5000/predict")

        try:
            with st.spinner("Analyzing..."):
                response = requests.post(
                    api_url,
                    data=json.dumps(payload),
                    headers={"Content-Type": "application/json"},
                    timeout=5,
                )

            if response.status_code == 200:
                data = response.json()
                species_map = {0: "Setosa", 1: "Versicolor", 2: "Virginica"}
                pred_val = data.get("prediction")

                if isinstance(pred_val, int):
                    predicted_species = species_map.get(pred_val, "Unknown")
                else:
                    predicted_species = data.get("species", "Unknown")

                images = {
                    "Setosa": "https://upload.wikimedia.org/wikipedia/commons/5/56/Kosaciec_szczecinkowaty_Iris_setosa.jpg",
                    "Versicolor": "https://upload.wikimedia.org/wikipedia/commons/4/41/Iris_versicolor_3.jpg",
                    "Virginica": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Iris_virginica.jpg",
                    "Unknown": "https://via.placeholder.com/400?text=Unknown+Species",
                }
                img_url = images.get(predicted_species, images["Unknown"])

                # Updated Image Display
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-bottom: 10px;">
                        <h2 style="color: #4ade80; margin: 0; font-size: 1.8rem;">{predicted_species}</h2>
                    </div>
                    
                    <div class="fixed-img-container">
                        <img src="{img_url}" class="fixed-img" alt="Flower Prediction">
                    </div>
                    
                    <p style="margin-top: 20px; text-align: center; color: #cbd5e1; font-size: 1rem;">
                        Identified as <b>Iris {predicted_species}</b>.
                    </p>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.error(f"API Error: {response.status_code}")
        except requests.exceptions.RequestException:
            st.error("API Connection Failed")
            st.caption(f"Backend URL: {api_url}")


# --- REAL-TIME DRAG UPDATE SCRIPT ---
components.html(
    """
    <script>
    const doc = window.parent.document;
    
    // SVG Generator (JS Version)
    function updateFlower(sl, sw, pl, pw) {
        const scale = 18;
        const cx = 150, cy = 150;
        const draw = (rx, ry, color, op, stroke, angles) => 
            angles.map(a => 
                `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="${color}" fill-opacity="${op}" stroke="${stroke}" stroke-width="1" transform="rotate(${a} ${cx} ${cy})" />`
            ).join('');
        const sepals = draw((sl*scale)/2, (sw*scale)/2, "#84cc16", "0.5", "#4d7c0f", [0, 120, 240]);
        const petals = draw((pl*scale)/2, (pw*scale)/2, "#a855f7", "0.8", "#6b21a8", [60, 180, 300]);
        const center = `<circle cx="${cx}" cy="${cy}" r="6" fill="#fbbf24" />`;
        const container = doc.getElementById("flower-svg-container");
        if (container) {
            container.innerHTML = `<svg width="300" height="300" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg" style="background:#1E293B; border-radius:12px;">${sepals}${petals}${center}</svg>`;
        }
    }

    // High-speed Poller (50ms)
    setInterval(() => {
        try {
            const getVal = (label) => {
                const el = doc.querySelector(`div[role="slider"][aria-label^="${label}"]`);
                if (!el) return null;
                return parseFloat(el.getAttribute("aria-valuenow"));
            };
            const sl = getVal("Sepal Length");
            const pl = getVal("Petal Length");
            const sw = getVal("Sepal Width");
            const pw = getVal("Petal Width");
            if (sl !== null && pl !== null && sw !== null && pw !== null) {
                updateFlower(sl, sw, pl, pw);
            }
        } catch(e) { }
    }, 50); 
    </script>
    """,
    height=0,
)
