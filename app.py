import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import streamlit as st
import tensorflow as tf
import numpy as np
import cv2
import json
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
# MULTI-LANGUAGE DICTIONARY
# =====================================
LANGUAGES = {
    "English": {
        "title": "🌱 Plant Disease Detection",
        "subtitle": "AI-Based Plant Disease Prediction System",
        "choose_plant": "🌱 Select Plant Type First:",
        "input_method": "📸 Choose Image Input Method",
        "upload": "📁 Upload Leaf Image",
        "camera": "📷 Capture Leaf Image",
        "analyze": "🔍 Analyzing leaf...",
        "result_title": "🔍 Prediction Result",
        "confidence": "📊 Confidence Score",
        "cause": "🦠 Disease Cause",
        "treatment": "💊 Treatment",
        "prevention": "🛡️ Prevention",
        "weather_head": "🌤️ Live Farm Weather Forecast",
        "weather_btn": "Get Weather",
        "enter_city": "Enter your City (e.g., Sialkot, Lahore)",
        "toast_alert": "🚨 Disease Detected! Time to prepare the spray!",
    },
    "Urdu (اردو)": {
        "title": "🌱 پودوں کی بیماریوں کی تشخیص",
        "subtitle": "مصنوعی ذہانت (AI) پر مبنی پودوں کی بیماریوں کا نظام",
        "choose_plant": "🌱 پہلے پودے کی قسم منتخب کریں:",
        "input_method": "📸 تصویر لینے کا طریقہ منتخب کریں",
        "upload": "📁 پتے کی تصویر اپلوڈ کریں",
        "camera": "📷 کیمرے سے تصویر کھینچیں",
        "analyze": "🔍 پتے کا معائنہ کیا جا رہا ہے...",
        "result_title": "🔍 معائنہ کا نتیجہ",
        "confidence": "📊 یقین دہانی کا اسکور (Confidence)",
        "cause": "🦠 بیماری کی وجہ",
        "treatment": "💊 علاج اور اسپرے",
        "prevention": "🛡️ بچاؤ کی تدابیر",
        "weather_head": "🌤️ آپ کے علاقے کے موسم کا حال",
        "weather_btn": "موسم دیکھیں",
        "enter_city": "اپنے شہر کا نام لکھیں (جیسے Sialkot، Lahore)",
        "toast_alert": "🚨 بیماری کی تشخیص ہو گئی ہے! اسپرے کا وقت ہو گیا ہے۔",
    }
}

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
                        st.success("✅ Login Successful!")
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
                    users[username] = {
                        "password": hash_password(password),
                        "recovery": hash_password(recovery)
                    }
                    with open(USER_FILE, "w") as f:
                        json.dump(users, f)
                    st.success("🎉 Account Created!")
        elif option == "Forgot Password":
            recovery = st.text_input("🔑 Enter Recovery Code")
            new_password = st.text_input("🔒 New Password", type="password")
            if st.button("🔄 Reset Password"):
                if username in users:
                    if users[username]["recovery"] == hash_password(recovery):
                        users[username]["password"] = hash_password(new_password)
                        with open(USER_FILE, "w") as f:
                            json.dump(users, f)
                        st.success("✅ Password Reset!")
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
                            st.warning("⚠️ Too short!")
                        else:
                            users[username]["password"] = hash_password(new_password)
                            with open(USER_FILE, "w") as f:
                                json.dump(users, f)
                            st.success("✅ Password Changed!")
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
        # 1. Sabse pehle completely functional native method se layer loading bypass karein
        import keras
        model = keras.models.load_model("model/best_model.h5", compile=False)
        return model
    except Exception as e:
        try:
            # 2. Agar phir bhi masla ho, to json config layers ko bypass kar ke direct loading implement karein
            with tf.keras.utils.custom_object_scope({'InputLayer': tf.keras.layers.InputLayer}):
                model = tf.keras.models.load_model("model/best_model.h5", compile=False)
                return model
        except Exception as e2:
            st.error(f"❌ Model load failed completely: {e2}")
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
# AUTOMATIC LIVE LOCATION WEATHER ENGINE 🌤️
# =====================================
import requests

def get_weather_report():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        display_city = "Sialkot"
        lat, lon = "32.50", "74.53" 

        # Automatic Live Location Geolocation tracking loop
        try:
            geo_res = requests.get('http://ip-api.com', timeout=3).json()
            if geo_res.get('status') == 'success':
                display_city = geo_res.get('city', 'Sialkot')
                lat = str(geo_res.get('lat', 32.50))
                lon = str(geo_res.get('lon', 74.53))
            else:
                backup_res = requests.get('https://ipinfo.io', timeout=3).json()
                display_city = backup_res.get('city', 'Sialkot')
                loc = backup_res.get('loc', '32.50,74.53').split(',')
                lat, lon = loc, loc
        except:
            pass 

        # Direct Open-Meteo API Call for exact real-time weather metrics
        url = f"https://open-meteo.com{lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code"
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get('current', {})
            
            temp_val = current.get('temperature_2m')
            humidity_val = current.get('relative_humidity_2m')
            w_code = current.get('weather_code', 0)
            
            if temp_val is not None:
                temp = f"{int(round(temp_val))} °C"
                humidity = f"{int(round(humidity_val))}%" if humidity_val else "50%"
                
                if w_code <= 3:
                    desc = "Clear / Sunny"
                elif w_code <= 48:
                    desc = "Partly Cloudy / Foggy"
                else:
                    desc = "Overcast / Rainy"
                    
                return {"temp": temp, "humidity": humidity, "desc": desc, "city": display_city}
        
        return {"temp": "37 °C", "humidity": "48%", "desc": "Clear / Sunny", "city": display_city}
    except:
        return {"temp": "37 °C", "humidity": "48%", "desc": "Clear / Sunny", "city": "Sialkot"}


# =====================================
# SIDEBAR RE-DESIGN (UPDATED SUPPORTED PLANTS LIST)
# =====================================
st.sidebar.markdown("<h2 style='color:#1b5e20;'>🌿 Plant AI Panel</h2>", unsafe_allow_html=True)
st.sidebar.write(f"👤 {st.session_state.username}")

lang_choice = st.sidebar.selectbox("🌐 Choose Language / زبان منتخب کریں", ["English", "Urdu (اردو)"])
txt = LANGUAGES[lang_choice]

st.sidebar.markdown("---")

st.sidebar.write(f"### {txt['weather_head']}")
if st.sidebar.button("🔄 Check Live Farm Weather"):
    with st.sidebar.spinner("Scanning network location..."):
        w_data = get_weather_report() 
        if w_data:
            st.sidebar.success(f"📍 Location: {w_data['city']}")
            st.sidebar.metric(label="🌡️ Temperature", value=w_data['temp'])
            st.sidebar.metric(label="💧 Humidity", value=w_data['humidity'])
            st.sidebar.info(f"☁️ Sky: {w_data['desc']}")

st.sidebar.markdown("---")
st.sidebar.write("### 🌱 Supported Plants")
st.sidebar.write("🍎 Apple | 🍒 Cherry | 🌽 Corn | 🍇 Grape") 
st.sidebar.write("🍑 Peach | 🌶️ Pepper | 🥔 Potato | 🌾 Rice")  
st.sidebar.write("🍓 Strawberry | 🍅 Tomato")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()


# =====================================
# MAIN HEADER & HYBRID OPTIONS (UPDATED DROPDOWN)
# =====================================
st.markdown(f'<div class="title">{txt["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">{txt["subtitle"]}</div>', unsafe_allow_html=True)
st.markdown("---")

# Main Page ka selector dropdown options array fully shamil kiya 👇
selected_plant = st.selectbox(
    "🌱 Know your plant? Select it for 100% accuracy (Optional):", 
    ["Auto Detect / Random (I don't know)", "Apple", "Cherry", "Corn", "Grape", "Peach", "Pepper", "Potato", "Rice", "Strawberry", "Tomato"]
)

st.markdown("---")

# =====================================
# IMAGE INPUT (DYNAMIC LANGUAGE SUPPORT)
# =====================================
input_method = st.radio(txt["input_method"], ["Upload Image", "Use Camera"], horizontal=True)

uploaded_file = None
camera_image = None

if input_method == "Upload Image":
    uploaded_file = st.file_uploader(txt["upload"], type=["jpg", "jpeg", "png"])
else:
    camera_image = st.camera_input(txt["camera"])

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
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # =====================================
    # SMART PLANT VALIDATION CHECK (Green Pixel Filter)
    # =====================================
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV) # RGB image use ki taake mapping sahi ho
    lower_green = np.array([25, 40, 40])       # Light Green threshold arrays
    upper_green = np.array([85, 255, 255])     # Dark Green bounds logic
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    green_percentage = (np.sum(mask > 0) / (img.shape[0] * img.shape[1])) * 100
    
    if green_percentage < 3: # Agar image mein 3% se kam green rang ho to block kar de
        st.error("❌ Invalid Image! This does not look like a plant leaf. Please upload a clear leaf picture. / یہ پودے کا پتہ نہیں لگ رہا، براہ کرم پتے کی صاف تصویر اپلوڈ کریں۔")
        st.stop()

    with col1:
        st.image(img, caption="📷 Uploaded Leaf Image", use_container_width=True)

# =====================================
    # IMAGE PROCESSING & AUTO SHARPENER FILTER
    # =====================================
    processed_img = cv2.resize(img, (img_size, img_size))
    
    # 1. Image ki blurry variance measure karna
    blur_variance = cv2.Laplacian(processed_img, cv2.CV_64F).var()
    
    # 2. SMART FILTER: Agar image thodi blur ho to use sharp karein
    if blur_variance < 250:
        gaussian_blur = cv2.GaussianBlur(processed_img, (0, 0), 3.0)
        processed_img = cv2.addWeighted(processed_img, 1.5, gaussian_blur, -0.5, 0)
        
    # Standard normalization pipeline 
    processed_img = processed_img / 255.0
    processed_img = np.expand_dims(processed_img, axis=0)

    with st.spinner(txt["analyze"]):
        prediction = model.predict(processed_img, verbose=0)
        
    # 👇 YEH LOGIC YAHAN PASTE KAREIN 👇
    if "Auto Detect" not in selected_plant:
        # User ne koi specific plant select kiya hai -> Apply Smart Filter
        filtered_prediction = prediction.copy()
        
        # Baqi saari galat plant classes ko lock (-1) kar do
        for idx, class_name in enumerate(class_names):
            if selected_plant.lower() not in class_name.lower():
                filtered_prediction[0][idx] = -1.0 
                
        index = int(np.argmax(filtered_prediction[0]))  
        confidence = float(filtered_prediction[0][index] * 100)
    else:
        # User ko plant ka nahi pata -> Pure dataset par auto detect chalne do
        index = int(np.argmax(prediction[0]))  
        confidence = float(prediction[0][index] * 100)  

    # Confidence Threshold Checking
    if confidence < 65:
        st.error("⚠️ Image is not clear or plant is unsupported. Please try again.")
        st.stop()
        
    predicted_class = class_names[index].strip()
    clean_name = predicted_class.replace("___", " - ").replace("_", " ") 

    # =====================================
    # SMART SPRAY NOTIFICATION ALERT 
    # =====================================
    if "healthy" not in predicted_class.lower():
        # Instant Web Push Browser Pop-up Alert
        st.toast(txt['toast_alert'], icon="🚨")
        
        # UI ke andar bada red banner message
        st.error(f"⚠️ **Alert:** {txt['toast_alert']}")

    # =====================================
    # DISEASE INFO
    # =====================================

    cause = "No information available"
    treatment = "No treatment available"
    prevention = "No prevention available"

    # APPLE
    if "Apple___Apple Scab" in predicted_class:
        cause = "Fungal pathogen Venturia inaequalis."
        treatment = "Apply fungicide sprays to protect healthy foliage."
        prevention = "Remove fallen leaves and interrupt lifecycle in autumn."
    elif "Apple___Black Rot" in predicted_class:
        cause = "Fungal disease Botryosphaeria obtusa."
        treatment = "Remove infected fruits and spray fungicide."
        prevention = "Prune infected branches and maintain orchard hygiene."
    elif "Apple___Cedar Apple Rust" in predicted_class:
        cause = "Fungal pathogen Gymnosporangium juniperi-virginianae."
        treatment = "Apply protective fungicides during spring."
        prevention = "Remove nearby juniper trees."
    elif "Apple___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Apple plant is healthy."
        prevention = "Maintain proper irrigation and sunlight."

    # PEPPER
    elif "Pepper___Bacterial Spot" in predicted_class:
        cause = "Bacterium Xanthomonas campestris."
        treatment = "Apply copper-based bactericide and remove infected leaves."
        prevention = "Use certified disease-free seeds and avoid overhead watering."
    elif "Pepper___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Pepper plant is healthy."
        prevention = "Continue proper watering and sunlight."

    # POTATO
    elif "Potato___Early Blight" in predicted_class:
        cause = "Fungal pathogen Alternaria solani."
        treatment = "Apply fungicide and remove infected leaves."
        prevention = "Maintain proper airflow and avoid overhead irrigation."
    elif "Potato___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Potato plant is healthy."
        prevention = "Continue proper plant care."
    elif "Potato___Late Blight" in predicted_class:
        cause = "Oomycete pathogen Phytophthora infestans."
        treatment = "Apply anti-blight fungicide immediately."
        prevention = "Avoid overwatering and ensure good drainage."

    # RICE
    elif "Rice___Bacterial Leaf Blight" in predicted_class:
        cause = "Bacterium Xanthomonas oryzae pv. oryzae."
        treatment = "Apply copper-based bactericide and drain fields."
        prevention = "Use resistant varieties and balanced nitrogen fertilization."
    elif "Rice___Brown Spot" in predicted_class:
        cause = "Fungal pathogen Bipolaris oryzae."
        treatment = "Correct soil nutrients and apply foliar fungicides."
        prevention = "Optimal soil nutrient management and field sanitation."
    elif "Rice___Healthy Rice Leaf" in predicted_class:
        cause = "No disease detected."
        treatment = "Rice plant is healthy."
        prevention = "Continue proper care and water management."
    elif "Rice___Leaf Blast" in predicted_class:
        cause = "Airborne fungal pathogen Magnaporthe oryzae."
        treatment = "Apply fungicide immediately."
        prevention = "Balanced fertilization and early seed sanitation."
    elif "Rice___Leaf scald" in predicted_class:
        cause = "Fungal pathogen Microdochium oryzae."
        treatment = "Apply foliar fungicides and stop excess nitrogen."
        prevention = "Seed decontamination and post-harvest sanitation."
    elif "Rice___Narrow Brown Leaf Spot" in predicted_class:
        cause = "Fungal pathogen Cercospora janseana."
        treatment = "Apply systemic fungicides and correct potassium deficiency."
        prevention = "Soil fertility management and strategic planting."
    elif "Rice___Rice Hispa" in predicted_class:
        cause = "Insect infestation by rice hispa beetle."
        treatment = "Apply targeted insecticides and clip affected leaves."
        prevention = "Eliminate host weeds and manage nitrogen."
    elif "Rice___Sheath Blight" in predicted_class:
        cause = "Soil-borne fungal pathogen Rhizoctonia solani."
        treatment = "Apply targeted fungicides and reduce canopy humidity."
        prevention = "Destroy overwintering sclerotia and balance nitrogen."

    # STRAWBERRY
    elif "Strawberry___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Strawberry plant is healthy."
        prevention = "Continue proper care."
    elif "Strawberry___Leaf Scorch" in predicted_class:
        cause = "Fungal pathogen Diplocarpon earlianum."
        treatment = "Remove infected leaves and apply fungicide."
        prevention = "Reduce excess moisture and ensure good air circulation."

    # TOMATO
    elif "Tomato___Bacterial Spot" in predicted_class:
        cause = "Bacterium Xanthomonas in warm and wet climates."
        treatment = "Use copper-based bactericide."
        prevention = "Eliminate bacteria sources and control environment."
    elif "Tomato___Early Blight" in predicted_class:
        cause = "Fungal pathogen Alternaria solani."
        treatment = "Apply fungicide and remove infected leaves."
        prevention = "Keep leaves dry and maintain proper spacing."
    elif "Tomato___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Tomato plant is healthy."
        prevention = "Continue proper watering and sunlight."
    elif "Tomato___Late Blight" in predicted_class:
        cause = "Oomycete Phytophthora infestans."
        treatment = "Remove infected leaves and use fungicide."
        prevention = "Avoid excess moisture and ensure proper drainage."

    # CHERRY    
    elif "Cherry___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Cherry plant is healthy."
        prevention = "Continue proper watering and care."

    elif "Cherry___Powdery Mildew" in predicted_class:
        cause = "Fungal pathogen Podosphaera clandestina causing white powdery coating."
        treatment = "Apply sulfur-based fungicide and remove infected shoots."
        prevention = "Ensure good air circulation and avoid overhead irrigation."

    # CORN
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

    # GRAPE 
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

    # PEACH
    elif "Peach___Bacterial Spot" in predicted_class:
        cause = "Bacterium Xanthomonas arboricola pv. pruni causing water-soaked spots."
        treatment = "Apply copper-based bactericide sprays during growing season."
        prevention = "Plant resistant varieties and avoid overhead irrigation."

    elif "Peach___Healthy" in predicted_class:
        cause = "No disease detected."
        treatment = "Peach plant is healthy."
        prevention = "Continue proper care and regular monitoring."       

    # HEALTH STATUS
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