import streamlit as st
import pandas as pd
import pickle
import time
import requests
from PIL import Image
from streamlit_lottie import st_lottie


# ------------------ Helper Function for Lottie Animations ------------------
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


# ------------------ Helper Function for Resizing Images ------------------
def get_resized_image(path, size=(100, 100)):
    """Open an image from the given path and resize it to the given size."""
    try:
        img = Image.open(path)
        return img.resize(size)
    except Exception as e:
        st.error(f"Error loading image: {path}")
        return None


# ------------------ Load Lottie Animations ------------------
lottie_transition = load_lottieurl("https://assets7.lottiefiles.com/packages/lf20_iwmd6pyr.json")
# Updated success animation URL (change if needed)
lottie_success = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_j1adxtyb.json")

# ------------------ Load Prediction Model ------------------
pipe = pickle.load(open('pipe.pkl', 'rb'))

# ------------------ Session State Initialization ------------------
if 'step' not in st.session_state:
    st.session_state.step = 1

# ------------------ Define Teams, Logo Paths, and Full Names ------------------
teams = ["RCB", "PBKS", "CSK", "MI", "SRH", "KKR", "RR", "DC"]
team_logos = {
    "RCB": "logo/RCB.png",
    "PBKS": "logo/PBKS.png",
    "CSK": "logo/CSK.png",
    "MI": "logo/MI.png",
    "SRH": "logo/SRH.png",
    "KKR": "logo/KKR.png",
    "RR": "logo/RR.png",
    "DC": "logo/DC.png"
}

team_full_names = {
    "RCB": "Royal Challengers Bangalore",
    "PBKS": "Kings XI Punjab",
    "CSK": "Chennai Super Kings",
    "MI": "Mumbai Indians",
    "SRH": "Sunrisers Hyderabad",
    "KKR": "Kolkata Knight Riders",
    "RR": "Rajasthan Royals",
    "DC": "Delhi Capitals"
}

cities = sorted([
    'Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
    'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
    'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
    'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
    'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
    'Sharjah', 'Mohali', 'Bengaluru'
])

# ------------------ Custom CSS Styling with IPL Colors ------------------
st.set_page_config(page_title="IPL Win Predictor", layout="wide")
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
        body {
            background-color: #f4f4f4;
            font-family: 'Montserrat', sans-serif;
            margin: 0;
            padding: 0;
        }
        /* Header with Tata IPL Logo (big) */
        .header {
            background-color: #000;
            padding: 10px 20px;
            text-align: center;
        }
        .header img {
            height: 150px; /* Bigger Tata IPL logo */
        }
        /* Navigation Bar using IPL Red */
        .nav {
            background-color: #e10600;
            color: #fff;
            padding: 10px 20px;
            text-align: center;
            font-size: 20px;
            letter-spacing: 1px;
        }
        /* Blue Banner Accent */
        .blue-banner {
            background-color: #005ba3;
            height: 5px;
        }
        /* Big Title */
        .main-title {
            text-align: center;
            font-size: 60px; /* Bigger title */
            margin-top: 20px;
            color: #e10600;
        }
        .section-title {
            text-align: center;
            font-size: 32px;
            margin: 30px 0 20px;
            color: #000;
        }
        /* Centered Buttons */
        .stButton > button {
            background-color: #e10600;
            color: #fff;
            border: none;
            padding: 10px 20px;
            font-size: 20px;
            border-radius: 5px;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        .stButton > button:hover {
            background-color: #b00400;
        }
        /* Card Styling for Outcome Display */
        .card {
            background-color: #fff;
            border-left: 5px solid #005ba3;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ Header and Navigation ------------------
st.markdown("""
    <div class="header">
        <!-- Tata IPL Logo: Replace the URL with your Tata IPL logo if available -->
        <img src="https://www.iplt20.com/assets/images/IPL_LOGO_CORPORATE_2024.png" alt="Tata IPL Logo">
    </div>
    <div class="nav">
        Official IPL Win Predictor
    </div>
    <div class="blue-banner"></div>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>IPL Win Predictor</h1>", unsafe_allow_html=True)


# ------------------ Helper Function: Display Team Grid ------------------
def team_selector(prefix, team_list, selected_key, logos_dict):
    """
    Displays teams in a 4x2 grid.
    If a team is already selected (stored in session state under selected_key),
    only that team's logo and name will be displayed.
    All images are resized to 100x100 pixels.
    """
    selected_team = st.session_state.get(selected_key, None)
    if selected_team is not None:
        img = get_resized_image(logos_dict[selected_team])
        if img is not None:
            st.image(img)
        st.write(f"**{selected_team} (Selected)**")
    else:
        rows = [team_list[i:i + 4] for i in range(0, len(team_list), 4)]
        for row in rows:
            cols = st.columns(4)
            for i, team in enumerate(row):
                with cols[i]:
                    img = get_resized_image(logos_dict[team])
                    if img is not None:
                        st.image(img)
                    if st.button(team, key=f"{prefix}_{team}"):
                        st.session_state[selected_key] = team
                        st.experimental_rerun()


# ------------------ Step 1: Match Setup ------------------
if st.session_state.step == 1:
    st.markdown("<h2 class='section-title'>Match Setup</h2>", unsafe_allow_html=True)

    # Display team selectors in two columns.
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Select Batting Team")
        team_selector("batting", teams, "batting_team", team_logos)
    with col2:
        st.markdown("#### Select Bowling Team")
        batting_selected = st.session_state.get("batting_team", None)
        available_bowling = [t for t in teams if t != batting_selected] if batting_selected else teams
        team_selector("bowling", available_bowling, "bowling_team", team_logos)

    st.markdown("---")
    st.selectbox('Select Match City', cities, key="selected_city")
    st.slider('Target Score', min_value=50, max_value=300, value=150, step=1, key="target")

    if st.session_state.get("batting_team") and st.session_state.get("bowling_team"):
        if st.button("Next", key="next1"):
            if lottie_transition:
                st_lottie(lottie_transition, height=150)
            time.sleep(1)
            st.session_state.step = 2
            st.experimental_rerun()
    else:
        st.warning("Please select both a batting and a bowling team.")

# ------------------ Step 2: Live Scoreboard ------------------
elif st.session_state.step == 2:
    st.markdown("<h2 class='section-title'>Live Scoreboard</h2>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.slider('Current Score', min_value=0, max_value=st.session_state.get("target", 150), value=0, step=1,
                      key="score")
        with col2:
            st.slider('Wickets Lost', min_value=0, max_value=9, value=0, step=1, key="wickets")
        with col3:
            st.slider('Overs Completed', min_value=0, max_value=20, value=0, step=1, key="overs")
    if st.button("Next", key="next2"):
        if lottie_transition:
            st_lottie(lottie_transition, height=150)
        time.sleep(1)
        st.session_state.step = 3
        st.experimental_rerun()

# ------------------ Step 3: Prediction Outcome ------------------
elif st.session_state.step == 3:
    st.markdown("<h2 class='section-title'>Prediction Outcome</h2>", unsafe_allow_html=True)

    # Convert abbreviated team names to full names for the model.
    batting_team_abbr = st.session_state.get("batting_team", teams[0])
    bowling_team_abbr = st.session_state.get("bowling_team", teams[1])
    batting_team = team_full_names[batting_team_abbr]
    bowling_team = team_full_names[bowling_team_abbr]

    selected_city = st.session_state.get("selected_city", cities[0])
    target = st.session_state.get("target", 150)
    score = st.session_state.get("score", 0)
    wickets = st.session_state.get("wickets", 0)
    overs = st.session_state.get("overs", 0)

    runs_left = max(target - score, 0)
    balls_left = max(120 - (overs * 6), 1)
    remaining_wickets = 10 - wickets
    crr = score / overs if overs > 0 else 0
    rrr = (runs_left * 6 / balls_left) if balls_left > 0 else 0

    df = pd.DataFrame({
        'batting_team': [batting_team],
        'bowling_team': [bowling_team],
        'city': [selected_city],
        'runs_left': [runs_left],
        'balls_left': [balls_left],
        'wickets': [remaining_wickets],
        'total_runs_x': [target],
        'crr': [crr],
        'rrr': [rrr]
    })

    result = pipe.predict_proba(df)
    batting_prob = round(result[0][1] * 100)
    bowling_prob = round(result[0][0] * 100)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class='card'>
                    <h3>{batting_team}</h3>
                    <p><strong>{batting_prob}%</strong> chance to win</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class='card'>
                    <h3>{bowling_team}</h3>
                    <p><strong>{bowling_prob}%</strong> chance to win</p>
                </div>
            """, unsafe_allow_html=True)
    st.progress(batting_prob / 100)
    if lottie_success:
        st_lottie(lottie_success, height=200)
    else:
        st.write("Animation unavailable.")
    if st.button("Start Over", key="restart"):
        for key in ["batting_team", "bowling_team", "selected_city", "target", "score", "wickets", "overs"]:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.step = 1
        st.experimental_rerun()
