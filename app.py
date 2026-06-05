import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
import json
import os
import hashlib

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Plant Disease Detection",
    page_icon="🌿",
    layout="wide"
)

# =====================================
# PASSWORD HASHING
# =====================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =====================================
# LOGIN SYSTEM
# =====================================

USER_FILE = "users.json"

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

with open(USER_FILE, "r") as f:
    users = json.load(f)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>
.main { background: linear-gradient(135deg, #e8f5e9, #f1f8e9); }
.title { text-align: center; font-size: 42px; font-weight: bold; color: #1b5e20; }
.subtitle { text-align: center; font-size: 18px; color: #4caf50; margin-bottom: 30px; }
.result-box { background: white; padding: 30px; border-radius: 20px; box-shadow: 0px 8px 25px rgba(0,0,0,0.1); border-left: 5px solid #4caf50; }
.stButton > button { background: linear-gradient(135deg, #4caf50, #1b5e20); color: white; border: none; border-radius: 10px; padding: 10px 25px; font-size: 16px; font-weight: bold; width: 100%; }
</style>
""", unsafe_allow_html=True)

# =====================================
# LOGIN PAGE
# =====================================

if not st.session_state.logged_in:

    st.markdown('<div class="title">🌿 Plant AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI-Based Plant Disease Detection System</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        option = st.selectbox("Choose Option", ["Login", "Signup", "Forgot Password", "Change Password"])
        username = st.text_input("👤 Username")

        if option == "Login":
            password = st.text_input("🔒 Password", type="password")
            if st.button("🚀 Login"):
                if username in users:
                    stored = users[username]["password"]
                    if stored == hash_password(password) or stored == password:
                        st.success("✅ Login Successful! Welcome " + username)
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.error("❌ Invalid Username or Password")
                else:
                    st.error("❌ Invalid Username or Password")

        elif option == "Signup":
            password = st.text_input("🔒 Create Password", type="password")
            confirm = st.text_input("🔒 Confirm Password", type="password")
            recovery = st.text_input("🔑 Recovery Code")
            if st.button("✅ Create Account"):
                if username == "":
                    st.warning("⚠️ Username cannot be empty")
                elif len(password) < 6:
                    st.warning("⚠️ Password must be at least 6 characters")
                elif password != confirm:
                    st.warning("⚠️ Passwords do not match")
                elif username in users:
                    st.warning("⚠️ Username already exists")
                else:
                    users[username] = {"password": hash_password(password), "recovery": hash_password(recovery)}
                    with open(USER_FILE, "w") as f:
                        json.dump(users, f)
                    st.success("🎉 Account Created Successfully!")

        elif option == "Forgot Password":
            recovery = st.text_input("🔑 Enter Recovery Code")
            new_password = st.text_input("🔒 New Password", type="password")
            if st.button("🔄 Reset Password"):
                if username in users:
                    if users[username]["recovery"] == hash_password(recovery):
                        users[username]["password"] = hash_password(new_password)
                        with open(USER_FILE, "w") as f:
                            json.dump(users, f)
                        st.success("✅ Password Reset Successfully!")
                    else:
                        st.error("❌ Wrong Recovery Code")
                else:
                    st.error("❌ Username not found")

        elif option == "Change Password":
            old_password = st.text_input("🔒 Old Password", type="password")
            new_password = st.text_input("🔒 New Password", type="password")
            confirm = st.text_input("🔒 Confirm New Password", type="password")
            if st.button("🔄 Change Password"):
                if username in users:
                    stored = users[username]["password"]
                    if stored == hash_password(old_password) or stored == old_password:
                        if new_password != confirm:
                            st.warning("⚠️ Passwords do not match")
                        elif len(new_password) < 6:
                            st.warning("⚠️ Password must be at least 6 characters")
                        else:
                            users[username]["password"] = hash_password(new_password)
                            with open(USER_FILE, "w") as f:
                                json.dump(users, f)
                            st.success("✅ Password Changed Successfully!")
                    else:
                        st.error("❌ Wrong Old Password")
                else:
                    st.error("❌ Username not found")

    st.stop()

# =====================================
# LOAD MODEL
# =====================================

@st.cache_resource
def load_model():
    try:
        model = tf.keras.models.load_model("model/plant_disease_model.h5",compile=False)
        return model
    except Exception as e:
        st.error(f"❌ Model load failed: {e}")
        return None

@st.cache_resource
def load_classes():
    try:
        with open("model/class_names.json", "r") as f:
            return json.load(f)
    except:
        st.error("❌ class_names.json not found!")
        return []

model = load_model()
class_names = load_classes()
img_size = 224

# =====================================
# SIDEBAR
# =====================================

st.sidebar.markdown("<h2 style='color:#1b5e20;'>🌿 Plant AI</h2>", unsafe_allow_html=True)
st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.write("### 🌱 Supported Plants")
st.sidebar.write("🍎 Apple")
st.sidebar.write("🍒 Cherry")
st.sidebar.write("🌽 Corn")
st.sidebar.write("🍇 Grape")
st.sidebar.write("🍑 Peach")
st.sidebar.write("🌶️ Pepper")
st.sidebar.write("🥔 Potato")
st.sidebar.write("🌾 Rice")
st.sidebar.write("🍓 Strawberry")
st.sidebar.write("🍅 Tomato")

# =====================================
# MAIN HEADER
# =====================================

st.markdown('<div class="title">🌱 Plant Disease Detection</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Based Plant Disease Prediction System</div>', unsafe_allow_html=True)
st.markdown("---")

# =====================================
# IMAGE INPUT
# =====================================

input_method = st.radio("📸 Choose Image Input Method", ["Upload Image", "Use Camera"], horizontal=True)

uploaded_file = None
camera_image = None

if input_method == "Upload Image":
    uploaded_file = st.file_uploader("📁 Upload Leaf Image", type=["jpg", "jpeg", "png"])
else:
    camera_image = st.camera_input("📷 Capture Leaf Image")

# =====================================
# PREDICTION
# =====================================

if uploaded_file is not None or camera_image is not None:

    col1, col2 = st.columns(2)

    if camera_image is not None:
        file_bytes = np.asarray(bytearray(camera_image.read()), dtype=np.uint8)
    else:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)

    img = cv2.imdecode(file_bytes, 1)

    with col1:
        st.image(img, caption="📷 Uploaded Leaf Image", use_container_width=True)

    processed_img = cv2.resize(img, (img_size, img_size))
    processed_img = processed_img / 255.0
    processed_img = np.expand_dims(processed_img, axis=0)

    with st.spinner("🔍 Analyzing leaf..."):
        prediction = model.predict(processed_img, verbose=0)

    index = int(np.argmax(prediction[0]))
    confidence = float(np.max(prediction[0]) * 100)

    if confidence < 70:
        st.error("⚠️ Data Not Found / Unsupported Plant Image")
        st.stop()

    predicted_class = class_names[index].strip()
    clean_name = predicted_class.replace("___", " - ").replace("_", " ")

    # =====================================
    # DISEASE INFO - ALL 38 CLASSES
    # =====================================

    cause = "No information available"
    treatment = "No treatment available"
    prevention = "No prevention available"

    # =====================================
    # APPLE
    # =====================================

    if "Apple___Apple Scab" in predicted_class:
        cause = "Fungal pathogen Venturia inaequalis."
        treatment = "Apply fungicide sprays to protect healthy foliage."
        prevention = "Interrupt lifecycle during autumn and winter by removing fallen leaves."

    elif "Apple___Black Rot" in predicted_class:
        cause = "Fungal disease Botryosphaeria obtusa causing black rotten spots."
        treatment = "Remove infected fruits and branches, spray fungicide."
        prevention = "Prune infected branches regularly and maintain orchard hygiene."

    elif "Apple___Cedar Apple Rust" in predicted_class:
        cause = "Fungal pathogen Gymnosporangium juniperi-virginianae."
        treatment = "Apply protective fungicides during spring infection period."
        prevention = "Remove nearby juniper trees and apply preventive fungicides."

    elif "Apple___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Apple plant is healthy."
        prevention = "Maintain proper irrigation, pruning and sunlight."

    # =====================================
    # CHERRY
    # =====================================

    elif "Cherry___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Cherry plant is healthy."
        prevention = "Continue proper watering and care."

    elif "Cherry___Powdery Mildew" in predicted_class:
        cause = "Fungal pathogen Podosphaera clandestina causing white powdery coating."
        treatment = "Apply sulfur-based fungicide and remove infected shoots."
        prevention = "Ensure good air circulation and avoid overhead irrigation."

    # =====================================
    # CORN
    # =====================================

    elif "Corn___Common Rust" in predicted_class:
        cause = "Fungal pathogen Puccinia sorghi causing rust colored pustules."
        treatment = "Apply fungicide at early stages of infection."
        prevention = "Plant resistant varieties and monitor fields regularly."

    elif "Corn___Gray Leaf Spot" in predicted_class:
        cause = "Fungal pathogen Cercospora zeae-maydis causing gray rectangular lesions."
        treatment = "Apply fungicide and remove infected plant debris."
        prevention = "Rotate crops and use resistant hybrid varieties."

    elif "Corn___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Corn plant is healthy."
        prevention = "Continue proper fertilization and irrigation."

    elif "Corn___Northern Leaf Blight" in predicted_class:
        cause = "Fungal pathogen Exserohilum turcicum causing long gray-green lesions."
        treatment = "Apply fungicide and remove heavily infected leaves."
        prevention = "Use resistant varieties and practice crop rotation."

    # =====================================
    # GRAPE
    # =====================================

    elif "Grape___Black Rot" in predicted_class:
        cause = "Fungal pathogen Guignardia bidwellii causing black shriveled fruits."
        treatment = "Remove infected fruits and apply fungicide sprays."
        prevention = "Prune for air circulation and remove mummified fruits."

    elif "Grape___Esca" in predicted_class:
        cause = "Complex fungal disease caused by Phaeomoniella chlamydospora."
        treatment = "Remove infected wood and apply fungicide wound protectants."
        prevention = "Avoid pruning wounds and protect cuts with sealants."

    elif "Grape___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Grape plant is healthy."
        prevention = "Maintain proper pruning and vineyard hygiene."

    elif "Grape___Leaf Blight" in predicted_class:
        cause = "Fungal pathogen Pseudocercospora vitis causing brown leaf spots."
        treatment = "Apply copper-based fungicide and remove infected leaves."
        prevention = "Ensure proper air circulation and avoid excess moisture."

    # =====================================
    # PEACH
    # =====================================

    elif "Peach___Bacterial Spot" in predicted_class:
        cause = "Bacterium Xanthomonas arboricola pv. pruni causing water-soaked spots."
        treatment = "Apply copper-based bactericide sprays during growing season."
        prevention = "Plant resistant varieties and avoid overhead irrigation."

    elif "Peach___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Peach plant is healthy."
        prevention = "Continue proper care and regular monitoring."

    # =====================================
    # PEPPER
    # =====================================

    elif "Pepper___Bacterial Spot" in predicted_class:
        cause = "Bacterium Xanthomonas campestris causing water-soaked leaf spots."
        treatment = "Apply copper-based bactericide and remove infected leaves."
        prevention = "Use certified disease-free seeds and avoid overhead watering."

    elif "Pepper___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Pepper plant is healthy."
        prevention = "Continue proper watering and sunlight."

    # =====================================
    # POTATO
    # =====================================

    elif "Potato___Early Blight" in predicted_class:
        cause = "Fungal pathogen Alternaria solani causing dark spots with rings."
        treatment = "Apply fungicide and remove infected leaves immediately."
        prevention = "Maintain proper airflow and avoid overhead irrigation."

    elif "Potato___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Potato plant is healthy."
        prevention = "Continue proper plant care and monitoring."

    elif "Potato___Late Blight" in predicted_class:
        cause = "Oomycete pathogen Phytophthora infestans causing water-soaked lesions."
        treatment = "Apply anti-blight fungicide immediately and remove infected plants."
        prevention = "Avoid overwatering, ensure good drainage and air circulation."

    # =====================================
    # RICE
    # =====================================

    elif "Rice___Bacterial Leaf Blight" in predicted_class:
        cause = "Bacterium Xanthomonas oryzae pv. oryzae causing water-soaked leaf edges."
        treatment = "Apply copper-based bactericide and drain fields when possible."
        prevention = "Use resistant varieties and balanced nitrogen fertilization."

    elif "Rice___Brown Spot" in predicted_class:
        cause = "Fungal pathogen Bipolaris oryzae causing brown oval spots."
        treatment = "Correct soil nutrients and apply foliar fungicides."
        prevention = "Optimal soil nutrient management and field sanitation."

    elif "Rice___Healthy Rice Leaf" in predicted_class:
        cause = "No disease detected."
        treatment = "Rice plant is healthy."
        prevention = "Continue proper care and water management."

    elif "Rice___Leaf Blast" in predicted_class:
        cause = "Airborne fungal pathogen Magnaporthe oryzae."
        treatment = "Apply fungicide immediately and correct cultural practices."
        prevention = "Balanced fertilization and early seed sanitation."

    elif "Rice___Leaf scald" in predicted_class:
        cause = "Fungal pathogen Microdochium oryzae causing scalded leaf appearance."
        treatment = "Apply foliar fungicides and stop excess nitrogen fertilizers."
        prevention = "Seed decontamination and post-harvest field sanitation."

    elif "Rice___Narrow Brown Leaf Spot" in predicted_class:
        cause = "Fungal pathogen Cercospora janseana causing narrow brown spots."
        treatment = "Apply systemic fungicides and correct potassium deficiency."
        prevention = "Soil fertility management and strategic planting timelines."

    elif "Rice___Rice Hispa" in predicted_class:
        cause = "Insect infestation by rice hispa beetle Dicladispa armigera."
        treatment = "Apply targeted insecticides and clip affected leaves."
        prevention = "Eliminate host weeds and manage nitrogen application."

    elif "Rice___Sheath Blight" in predicted_class:
        cause = "Soil-borne fungal pathogen Rhizoctonia solani."
        treatment = "Apply targeted fungicides and reduce canopy humidity."
        prevention = "Destroy overwintering sclerotia and balance nitrogen inputs."

    # =====================================
    # STRAWBERRY
    # =====================================

    elif "Strawberry___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Strawberry plant is healthy."
        prevention = "Continue proper care and monitoring."

    elif "Strawberry___Leaf Scorch" in predicted_class:
        cause = "Fungal pathogen Diplocarpon earlianum causing purple leaf spots."
        treatment = "Remove infected leaves and apply fungicide."
        prevention = "Reduce excess moisture and ensure good air circulation."

    # =====================================
    # TOMATO
    # =====================================

    elif "Tomato___Bacterial Spot" in predicted_class:
        cause = "Bacterium Xanthomonas thrives in warm and wet climates."
        treatment = "Use copper-based bactericide and strict cultural practices."
        prevention = "Eliminate bacteria sources and control field environment."

    elif "Tomato___Early Blight" in predicted_class:
        cause = "Fungal pathogen Alternaria solani affecting tomato leaves."
        treatment = "Apply fungicide and remove infected leaves."
        prevention = "Keep leaves dry and maintain proper plant spacing."

    elif "Tomato___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Tomato plant is healthy."
        prevention = "Continue proper watering and sunlight."

    elif "Tomato___Late Blight" in predicted_class:
        cause = "Oomycete Phytophthora infestans caused by excess moisture."
        treatment = "Remove infected leaves and use fungicide immediately."
        prevention = "Avoid excess moisture and ensure proper drainage."

    # =====================================
    # HEALTH STATUS
    # =====================================

    if "healthy" in predicted_class.lower() or "Healthy" in predicted_class:
        health_status = "✅ Healthy Leaf"
    else:
        health_status = "⚠️ Diseased Leaf"
    # =====================================
    # SHOW RESULTS
    # =====================================

    with col2:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.subheader("🔍 Prediction Result")
        st.success(f"**{clean_name}**")
        st.write(f"### {health_status}")
        st.write("### 📊 Confidence Score")
        st.progress(int(confidence))
        st.write(f"**{confidence:.2f}%**")
        st.markdown("---")
        st.write("### 🦠 Disease Cause")
        st.info(cause)
        st.write("### 💊 Treatment")
        st.warning(treatment)
        st.write("### 🛡️ Prevention")
        st.success(prevention)
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================
# FOOTER
# =====================================

st.markdown("---")
st.markdown("""
<center>
🌿 AI-Based Plant Disease Detection System<br>
Built using TensorFlow, OpenCV & Streamlit
</center>
""", unsafe_allow_html=True)