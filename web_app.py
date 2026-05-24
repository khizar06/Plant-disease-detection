import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
import json
import os

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Plant Disease Detection",
    page_icon="🌿",
    layout="wide"
)

# =====================================
# LOGIN SYSTEM
# =====================================

USER_FILE = "users.json"

# Create users file if missing
if not os.path.exists(USER_FILE):

    with open(USER_FILE, "w") as f:

        json.dump({}, f)

# Load users
with open(USER_FILE, "r") as f:

    users = json.load(f)

# Session state
if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

# Login page
if not st.session_state.logged_in:

    st.title("🌿 Plant AI Login")

    option = st.selectbox(
        "Choose Option",
        ["Login", "Signup"]
    )

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    # LOGIN
    if option == "Login":

        if st.button("Login"):

            if username in users and users[username] == password:

                st.success("Login Successful")

                st.session_state.logged_in = True

                st.rerun()

            else:

                st.error("Invalid Username or Password")

    # SIGNUP
    else:

        if st.button("Create Account"):

            if username in users:

                st.warning("Username already exists")

            else:

                users[username] = password

                with open(USER_FILE, "w") as f:

                    json.dump(users, f)

                st.success("Account Created Successfully")

    st.stop()

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>

.main {
    background-color: #f4fff4;
}

.title {
    text-align: center;
    font-size: 45px;
    font-weight: bold;
    color: #1b5e20;
}

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #4caf50;
    margin-bottom: 30px;
}

.result-box {
    background-color: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

# =====================================
# LOAD MODEL
# =====================================

model = tf.keras.models.load_model(
    "plant_disease_model.h5"
)

# =====================================
# LOAD CLASS NAMES
# =====================================

with open("class_names.json", "r") as f:
    class_names = json.load(f)

img_size = 224

# =====================================
# SIDEBAR
# =====================================

st.sidebar.title("🌿 Plant AI")
if st.sidebar.button("Logout"):

    st.session_state.logged_in = False

    st.rerun()

st.sidebar.info(
    "Upload a plant leaf image for disease detection."
)

st.sidebar.markdown("---")

st.sidebar.write("### Supported Plants")

st.sidebar.write("🌾 Rice")
st.sidebar.write("🍅 Tomato")
st.sidebar.write("🥔 Potato")
st.sidebar.write("🍎 Apple")
st.sidebar.write("🍓 Strawberry")

# =====================================
# MAIN HEADER
# =====================================

st.markdown(
    '<div class="title">🌱 Plant Disease Detection</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-Based Plant Disease Prediction System</div>',
    unsafe_allow_html=True
)

# =====================================
# FILE UPLOADER
# =====================================

input_method = st.radio(
    "choose Image Input Method",
    ["Upload Image","Use Camera"]
)
# IMAGE INPUT

uploaded_file = None
camera_image = None

if input_method == "Upload Image":

    uploaded_file = st.file_uploader(
        "📁 Upload Leaf Image",
        type=["jpg", "jpeg", "png"]
    )

else:

    camera_image = st.camera_input(
        "📷 Capture Leaf Image"
    )

# =====================================
# MAIN PREDICTION SECTION
# =====================================

if uploaded_file is not None or camera_image is not None:

    col1, col2 = st.columns(2)

    # READ IMAGE
    if camera_image is not None:

      file_bytes = np.asarray(
        bytearray(camera_image.read()),
        dtype=np.uint8
    )

    elif uploaded_file is not None:

     file_bytes = np.asarray(
        bytearray(uploaded_file.read()),
        dtype=np.uint8
    )

    img = cv2.imdecode(file_bytes, 1)

    # SHOW IMAGE
   
    with col1:

        st.image(
            img,
            caption="Uploaded Leaf Image",
            use_container_width=True
        )

    # PREPROCESS IMAGE
    processed_img = cv2.resize(
        img,
        (img_size, img_size)
    )

    processed_img = processed_img / 255.0

    processed_img = np.expand_dims(
        processed_img,
        axis=0
    )

    # =====================================
    # MODEL PREDICTION
    # =====================================

    prediction = model.predict(
        processed_img,
        verbose=0
    )

    index = int(np.argmax(prediction[0]))

    confidence = float(
        np.max(prediction[0]) * 100
    )
    if confidence < 70:
        st.error("Data Not Found / Unsupported Plant Image)
        st.stop()

    predicted_class = class_names[index].strip()

    clean_name = predicted_class.replace(
        "_",
        " - "
    )

    clean_name = clean_name.replace(
        "_",
        " "
    )

    # =====================================
    # DEFAULT VALUES
    # =====================================

    cause = "No information available"

    treatment = "No treatment available"

    prevention = "No prevention available"

    # =====================================
    # TOMATO
    # =====================================

    if "Tomato___Early_Blight" in predicted_class:

        cause = (
            "Fungal disease affecting tomato leaves."
        )
        treatment = (
            "Apply fungicide and remove infected leaves."
        )

        prevention = (
            "Keep leaves dry and maintain proper spacing."
        )

    elif "Tomato___Late_Blight" in predicted_class:

        cause = (
            "Serious fungal disease caused by moisture."
        )

        treatment = (
            "Remove infected leaves and use fungicide."
        )

        prevention = (
            "Avoid excess moisture around plants."
        )

    elif "Tomato___Leaf_Mold" in predicted_class:

        cause = (
            " Fungus Passalora fulva (formerly called Fulvia fulva or Cladosporium fulvum)."
        )

        treatment = (
            "lower the humidity around the plants and apply targeted fungicides to stop the fungus from releasing spores."
        )

        prevention = (
            "Keep relative humidity below 85% and maximize airflow around the canopy."
        )
    elif "Tomato___Bacterial_spot" in predicted_class:

        cause = (
             "This disease thrives in warm and wet climates, spreading rapidly under specific environmental and physical conditions."
        )
        treatment = (
             "Use a combination of chemical controls and strict cultural practices to minimize damage."
        )
        prevention = (
            "must eliminate the sources of bacteria and create an environment where the pathogen cannot multiply."
        )
    elif "Tomato___Target_Spot" in predicted_class:

        cause = (
             "Fungus Corynespora cassiicola."
        )
        treatment = (
             "Must act quickly with targeted fungicides."
        )
        prevention = (
            "Eliminate soil-borne spores and manage moisture so the fungus cannot germinate."
        )
        
    elif "Tomato___Healthy" in predicted_class:

        cause = (
            "No disease detected."
        )
        treatment = (
            "Tomato plant is healthy."
        )
        prevention = (
            "Continue proper watering and sunlight."
        )

    # =====================================
    # POTATO
    # =====================================

    elif "Potato___Early_Blight" in predicted_class:

        cause = (
            "Fungal disease affecting potato leaves."
        )
        treatment = (
            "Use fungicide and remove infected leaves."
        )

        prevention = (
            "Maintain proper airflow and dry leaves."
        )

    elif "Potato___Late_Blight" in predicted_class:

        cause = (
            "Moisture-based potato disease."
        )
        treatment = (
            "Apply anti-blight fungicide immediately."
        )

        prevention = (
            "Avoid overwatering and humidity."
        )

    elif "Potato___Healthy" in predicted_class:

        cause = (
            "No disease detected."
        )
        treatment = (
            "Potato plant is healthy."
        )
        prevention = (
            "Continue proper plant care."
        )
    # =====================================
    # APPLE
    # =====================================

    elif "Apple___Black_Rot" in predicted_class:

        cause = (
            "Fungal disease causing black rotten spots."
        )

        treatment = (
            "Remove infected fruits and spray fungicide."
        )

        prevention = (
            "Prune infected branches regularly."
        )

    elif "Apple___Apple_Scab" in predicted_class:

        cause = (
            "Fungal pathogen Venturia inaequalis."
        )

        treatment = (
            "Protecting healthy foliage and stopping the fungus from multiplying."
        )

        prevention = (
            "interrupt its lifecycle during the autumn and winter."
        )

    elif "Apple___Cedar_Apple_Rust" in predicted_class:

        cause = (
            "fungal pathogen Gymnosporangium juniperi-virginianae."
        )

        treatment = (
            "protecting healthy tissue and breaking the fungus's lifecycle."
        )

        prevention = (
            "disrupt the multi-mile fungal loop between your apple trees and nearby junipers."
        )

    elif "Apple___Healthy" in predicted_class:

        cause = (
            "No disease detected."
        )
        treatment = (
            "Apple plant is healthy."
        )
        prevention = (
            "Maintain proper irrigation and sunlight."
        )

    # =====================================
    # STRAWBERRY
    # =====================================

    elif "Strawberry___Leaf_Scorch" in predicted_class:

        cause = (
            "Fungal disease causing brown leaf edges."
        )

        treatment = (
            "Remove infected leaves and apply fungicide."
        )

        prevention = (
            "Reduce excess moisture around plants."
        )

    elif "Strawberry___Healthy" in predicted_class:

        cause = (
            "No disease detected."
        )
        treatment = (
            "Strawberry plant is healthy."
        )
        prevention = (
            "Continue proper care."
        )

    # =====================================
    # RICE
    # =====================================

    elif "Rice___Brown_Spot" in predicted_class:

        cause = (
            "Fungal pathogen Bipolaris oryzae (formerly known as Helminthosporium oryzae)."
        )

        treatment = (
            "correct soil nutrient deficiencies immediately and apply targeted foliar fungicides to arrest the spread."
        )

        prevention = (
            "optimal soil nutrient management, seed decontamination, and field sanitation."
        )

    elif "Rice___Hispa" in predicted_class:

        cause = (
            "insect infestation by the rice hispa beetle, scientifically named Dicladispa armigera."
        )

        treatment = (
            "use a combination of mechanical leaf clipping, nutrient adjustments, and targeted chemical insecticides."
        )

        prevention = (
            "eliminating alternative host weeds, managing nitrogen application, and altering your planting density."
        )

    elif "Rice___Leaf_Blast" in predicted_class:

        cause = (
            "airborne fungal pathogen Magnaporthe oryzae (also commonly referred by its asexual stage name, Pyricularia oryzae)."
        )

        treatment = (
            "combine immediate chemical applications with urgent cultural corrections."
        )

        prevention = (
            "balanced fertilization, continuous flooding, and early seed sanitation."
        )

    elif "Rice___Leaf_scald" in predicted_class:

        cause = (
            "fungal pathogen Microdochium oryzae."
        )

        treatment = (
            "deploy protective foliar fungicides and immediately stop applying nitrogen fertilizers."
        )

        prevention = (
            "seed decontamination, strict nitrogen control, and post-harvest sanitation."
        )

    elif "Rice___Narrow_Brown_Leaf_Spot" in predicted_class:

        cause = (
            "fungal pathogen Cercospora janseana (also widely known by its scientific synonyms Sphaerulina oryzina and Cercospora oryzae)."
        )

        treatment = (
            "apply targeted systemic fungicides during critical reproductive growth stages and immediately correct potassium deficiencies in the soil."
        )

        prevention = (
            "soil fertility management, field sanitation, and strategic planting timelines."
        )

    elif "Rice___Sheath_Blight" in predicted_class:

        cause = (
            "soil-borne fungal pathogen Rhizoctonia solani."
        )

        treatment = (
            "combine targeted chemical fungicides with immediate cultural modifications to drop canopy humidity and stop the fungus from climbing toward your flag leaves."
        )

        prevention = (
            "destroying the overwintering soil sclerotia, reducing canopy moisture, and balancing nitrogen inputs."
        )

    elif "Rice___Healthy" in predicted_class:

        cause = (
            "No disease detected."
        )

        treatment = (
            "Rice plant is healthy."
        )

        prevention = (
            "Continue proper care."
        )
    # =====================================
    # HEALTH STATUS
    # =====================================

    if "healthy" in predicted_class.lower():

        health_status = "✅ Healthy Leaf"

    else:

        health_status = "⚠️ Diseased Leaf"

    # =====================================
    # SHOW RESULTS
    # =====================================

    with col2:

        st.markdown(
            '<div class="result-box">',
            unsafe_allow_html=True
        )

        st.subheader("🔍 Prediction Result")

        st.success(clean_name)

        st.write(f"### {health_status}")

        st.write("### 📊 Confidence")

        st.progress(int(confidence))

        st.write(f"{confidence:.2f}%")

        st.markdown("---")

        st.write("### 🦠 Disease Cause")

        st.info(cause)

        st.write("### 💊 Treatment")

        st.warning(treatment)

        st.write("### 🛡️ Prevention")

        st.success(prevention)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

# =====================================
# FOOTER
# =====================================

st.markdown("---")

st.markdown(
    """
    <center>
    🌿 AI-Based Plant Disease Detection System<br>
    Built using TensorFlow, OpenCV & Streamlit
    </center>
    """,
    unsafe_allow_html=True
)
