import streamlit as st
from ultralytics import YOLO
from PIL import Image
from pathlib import Path
import hashlib


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GreenVision AI",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "history" not in st.session_state:
    st.session_state.history = []

if "last_file_hash" not in st.session_state:
    st.session_state.last_file_hash = None


# =========================================================
# MODEL PATH
# =========================================================

MODEL_CANDIDATES = [
    Path("runs/detect/train-3/weights/best.pt"),
    Path("runs/detect/train/weights/best.pt"),
]

MODEL_PATH = None

for candidate in MODEL_CANDIDATES:
    if candidate.exists():
        MODEL_PATH = str(candidate)
        break

if MODEL_PATH is None:
    st.error("❌ YOLO model not found. Please check the runs/detect folder.")
    st.stop()


# =========================================================
# LOAD MODEL
# =========================================================

@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)


model = load_model(MODEL_PATH)


# =========================================================
# WASTE INFORMATION
# =========================================================

def get_waste_info(class_name):
    name = class_name.lower()

    if "organic" in name:
        return (
            "Wet Waste / Organic",
            "Keep organic waste separate from dry waste. "
            "Composting or local organic-waste collection may be appropriate.",
        )

    elif any(word in name for word in [
        "paper",
        "cardboard",
        "postal packaging",
        "printing industry",
        "papier mache",
        "cellulose",
    ]):
        return (
            "Dry Waste / Paper",
            "Keep clean and dry. Paper and cardboard may be recyclable "
            "where accepted by local facilities.",
        )

    elif any(word in name for word in [
        "plastic",
        "stretch film",
        "combined plastic",
        "zip plastic bag",
        "tetra pack",
        "milk bottle",
    ]):
        return (
            "Dry Waste / Plastic",
            "Separate from wet waste. Recycling may be possible "
            "where the material is accepted by local recyclers.",
        )

    elif any(word in name for word in [
        "aluminum",
        "iron",
        "metal",
        "scrap metal",
        "tin",
        "foil",
    ]):
        return (
            "Potentially Recyclable / Metal",
            "Keep separate from wet waste. Metal recovery or recycling "
            "may be possible through appropriate local facilities.",
        )

    elif "glass" in name:
        return (
            "Potentially Recyclable / Glass",
            "Handle carefully and keep separate. Glass recycling "
            "depends on local collection and facility requirements.",
        )

    elif "electronics" in name:
        return (
            "E-Waste",
            "Do not mix with normal household waste. Use an authorized "
            "e-waste collection or recycling channel where available.",
        )

    elif "textile" in name:
        return (
            "Textile Waste",
            "Consider reuse, donation, repair or textile recovery "
            "where suitable.",
        )

    elif any(word in name for word in ["wood", "furniture"]):
        return (
            "Potentially Reusable / Wood Waste",
            "Consider reuse, repair, donation or appropriate "
            "wood-waste collection.",
        )

    elif any(word in name for word in [
        "aerosol",
        "chemical",
        "liquid",
    ]):
        return (
            "Special Handling",
            "Do not mix with regular waste. Follow local guidance "
            "for safe collection and disposal.",
        )

    elif "ceramic" in name:
        return (
            "General / Special Waste",
            "Ceramic items should be kept separate from recyclable "
            "glass and handled according to local waste guidance.",
        )

    elif "disposable tableware" in name:
        return (
            "Dry Waste",
            "Keep separate from wet waste. Actual recycling depends "
            "on the material and local collection system.",
        )

    else:
        return (
            "Needs Classification",
            "The material could not be confidently assigned "
            "to a specific waste category.",
        )


# =========================================================
# DASHBOARD CATEGORY
# =========================================================

def get_dashboard_category(category):
    category_lower = category.lower()

    if "wet" in category_lower or "organic" in category_lower:
        return "Wet Waste"

    if "reusable" in category_lower or "wood" in category_lower:
        return "Potentially Reusable"

    if "recyclable" in category_lower or "recoverable" in category_lower:
        return "Potentially Recyclable"

    if "dry" in category_lower:
        return "Dry Waste"

    return "Other / Special Waste"


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(48, 140, 95, 0.25),
                transparent 35%
            ),
            radial-gradient(
                circle at bottom right,
                rgba(20, 100, 70, 0.20),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #06150f,
                #0b2a20,
                #06130e
            );
        color: white;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .welcome-box {
        text-align: center;
        padding: 40px 20px 20px 20px;
        animation: welcomeAnimation 1.5s ease-out;
    }

    .welcome-title {
        font-size: 3.1rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 12px;
    }

    .welcome-subtitle {
        font-size: 1.15rem;
        opacity: 0.82;
    }

    @keyframes welcomeAnimation {
        0% {
            opacity: 0;
            transform: translateY(30px) scale(0.96);
        }

        60% {
            opacity: 0.8;
            transform: translateY(-4px) scale(1.01);
        }

        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .hero-box {
        text-align: center;
        padding: 10px 20px 20px 20px;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.82;
    }

    .tagline {
        text-align: center;
        font-size: 1rem;
        font-style: italic;
        opacity: 0.70;
        margin-bottom: 25px;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.065);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 18px;
        padding: 22px;
        text-align: center;
        min-height: 115px;
    }

    .metric-number {
        font-size: 2.3rem;
        font-weight: 800;
    }

    .metric-label {
        opacity: 0.70;
    }

    .footer {
        text-align: center;
        opacity: 0.55;
        margin-top: 50px;
        padding-top: 25px;
        border-top: 1px solid rgba(255, 255, 255, 0.10);
    }

    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
        min-height: 45px;
    }

    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 10px;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="welcome-box">
        <div class="welcome-title">🌱 Welcome to GreenVision AI</div>
        <div class="welcome-subtitle">
            AI-powered waste detection for a more sustainable future.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">♻️ GreenVision AI</div>
        <div class="hero-subtitle">
            AI-Powered Smart Waste Detection & Sustainability Analytics
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="tagline">“Turning Every Waste Decision into a Sustainable Impact.”</div>',
    unsafe_allow_html=True,
)


# =========================================================
# NAVIGATION
# =========================================================

nav1, nav2, nav3, nav4 = st.columns(4)

with nav1:
    if st.button("🏠 Home", use_container_width=True, key="nav_home"):
        st.session_state.page = "Home"
        st.rerun()

with nav2:
    if st.button("🌍 About SDG", use_container_width=True, key="nav_about"):
        st.session_state.page = "About SDG"
        st.rerun()

with nav3:
    if st.button(
        "💚 Importance of SDG",
        use_container_width=True,
        key="nav_importance",
    ):
        st.session_state.page = "Importance"
        st.rerun()

with nav4:
    if st.button(
        "📊 Your Contribution to SDG",
        use_container_width=True,
        key="nav_dashboard",
    ):
        st.session_state.page = "Dashboard"
        st.rerun()

st.divider()


# =========================================================
# HOME PAGE
# =========================================================

if st.session_state.page == "Home":

    st.subheader("🏠 Smart Waste Detection")

    st.write(
        "Upload an image of waste and GreenVision AI will use "
        "computer vision to identify the waste object and provide "
        "responsible handling guidance."
    )

    st.info(
        "💡 Tip: Use a clear image with good lighting and keep the "
        "waste object visible."
    )

    uploaded_file = st.file_uploader(
        "📸 Upload Waste Image",
        type=["jpg", "jpeg", "png"],
        help="Upload a clear image of a waste item.",
        key="waste_uploader",
    )

    if uploaded_file is not None:

        image = Image.open(uploaded_file).convert("RGB")

        st.image(
            image,
            caption="Uploaded Waste Image",
            use_container_width=True,
        )

        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.md5(file_bytes).hexdigest()

        with st.spinner("🤖 GreenVision AI is analysing the image..."):
            results = model.predict(
                source=image,
                conf=0.25,
                verbose=False,
            )

        detected_count = 0
        new_file = file_hash != st.session_state.last_file_hash

        for result in results:

            if result.boxes is None or len(result.boxes) == 0:
                continue

            annotated = result.plot()

            st.image(
                annotated,
                caption="AI Detection Result",
                use_container_width=True,
            )

            for box in result.boxes:

                detected_count += 1

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = result.names[class_id]

                category, recommendation = get_waste_info(class_name)
                dashboard_category = get_dashboard_category(category)

                if new_file:
                    st.session_state.history.append(
                        {
                            "object": class_name,
                            "confidence": confidence,
                            "category": category,
                            "dashboard_category": dashboard_category,
                        }
                    )

                st.markdown(f"### ♻️ Detection {detected_count}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Detected Object", class_name)

                with col2:
                    st.metric("AI Confidence", f"{confidence * 100:.1f}%")

                with col3:
                    st.metric("Waste Category", category)

                st.markdown("#### 💡 Recommended Action")
                st.success(recommendation)

                if confidence < 0.50:
                    st.warning(
                        "⚠️ The AI confidence is relatively low. "
                        "Try a clearer image, better lighting, "
                        "or another viewing angle."
                    )

                st.divider()

        if detected_count > 0:

            if new_file:
                st.session_state.last_file_hash = file_hash

            st.success(
                f"✅ Detection completed successfully — "
                f"{detected_count} object(s) detected."
            )

        else:

            if new_file:
                st.session_state.last_file_hash = file_hash

            st.info(
                "🔎 No waste object was detected confidently "
                "in this image."
            )


# =========================================================
# ABOUT SDG PAGE
# =========================================================

elif st.session_state.page == "About SDG":

    st.header("🌍 About the Sustainable Development Goals")

    st.write(
        "SDG stands for Sustainable Development Goals. They are a "
        "global framework designed to address major environmental, "
        "social and economic challenges."
    )

    st.write(
        "There are 17 Sustainable Development Goals. They cover "
        "areas such as poverty, education, health, sustainable "
        "cities, responsible consumption and climate action."
    )

    st.subheader("♻️ GreenVision AI & SDGs")

    st.write(
        "GreenVision AI focuses on intelligent waste detection, "
        "responsible waste handling and sustainability awareness."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("⭐ SDG 12")
        st.subheader("Responsible Consumption and Production")
        st.write(
            "Encourages responsible use of resources and better "
            "waste-management practices."
        )

    with col2:
        st.info("🏙️ SDG 11")
        st.subheader("Sustainable Cities and Communities")
        st.write(
            "Supports cleaner, safer and more sustainable "
            "communities."
        )

    with col3:
        st.success("🌱 SDG 13")
        st.subheader("Climate Action")
        st.write(
            "Encourages actions that reduce environmental impact "
            "and support climate-conscious living."
        )


# =========================================================
# IMPORTANCE PAGE
# =========================================================

elif st.session_state.page == "Importance":

    st.header("💚 Importance of SDGs")

    st.write(
        "Sustainable Development Goals provide a common direction "
        "for creating a healthier planet and society."
    )

    st.write(
        "They encourage governments, businesses, communities and "
        "individuals to work together toward sustainable development."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("♻️ Environmental Protection")
        st.write(
            "Better waste management can help reduce litter, "
            "pollution and unnecessary resource loss."
        )

    with col2:
        st.subheader("🌱 Sustainable Living")
        st.write(
            "SDGs encourage people and organizations to make "
            "responsible decisions that support long-term "
            "environmental sustainability."
        )

    st.subheader("🌍 Why GreenVision AI matters")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🔍 Identify")
        st.write(
            "Computer vision helps identify waste objects from "
            "uploaded images."
        )

    with col2:
        st.subheader("🗂️ Categorize")
        st.write(
            "Detected objects are mapped to practical "
            "waste-management categories."
        )

    with col3:
        st.subheader("🌱 Guide")
        st.write(
            "The system provides responsible handling guidance "
            "based on the detected material."
        )


# =========================================================
# DASHBOARD PAGE
# =========================================================

elif st.session_state.page == "Dashboard":

    st.header("📊 Your Contribution to SDG")

    st.write(
        "This dashboard summarizes waste detections made during "
        "your current GreenVision AI session."
    )

    if len(st.session_state.history) == 0:

        st.info(
            "🌱 No waste detections recorded yet. "
            "Go to Home and upload a waste image."
        )

    else:

        total_items = len(st.session_state.history)

        wet_count = sum(
            1
            for item in st.session_state.history
            if item["dashboard_category"] == "Wet Waste"
        )

        dry_count = sum(
            1
            for item in st.session_state.history
            if item["dashboard_category"] == "Dry Waste"
        )

        recyclable_count = sum(
            1
            for item in st.session_state.history
            if item["dashboard_category"] == "Potentially Recyclable"
        )

        reusable_count = sum(
            1
            for item in st.session_state.history
            if item["dashboard_category"] == "Potentially Reusable"
        )

        other_count = sum(
            1
            for item in st.session_state.history
            if item["dashboard_category"] == "Other / Special Waste"
            or item["dashboard_category"] == "E-Waste"
            or item["dashboard_category"] == "Textile Waste"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Detections", total_items)

        with col2:
            st.metric("Dry Waste", dry_count)

        with col3:
            st.metric("Potentially Recyclable", recyclable_count)

        with col4:
            st.metric("Wet Waste", wet_count)

        st.divider()

        st.subheader("📋 Detection History")

        for index, item in enumerate(
            reversed(st.session_state.history),
            start=1,
        ):

            st.markdown(f"### Detection {index}")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.write(f"*Object:* {item['object']}")

            with c2:
                st.write(
                    f"*Confidence:* "
                    f"{item['confidence'] * 100:.1f}%"
                )

            with c3:
                st.write(f"*Category:* {item['category']}")

            st.divider()

        st.subheader("🌍 Sustainability Connection")

        st.write(
            "Every correct waste identification can support better "
            "awareness of waste segregation and responsible resource use."
        )

        st.write(
            "GreenVision AI is primarily aligned with SDG 12 and also "
            "supports SDG 11 and SDG 13."
        )

        if reusable_count > 0:
            st.success(
                f"♻️ Potentially reusable items detected: {reusable_count}"
            )

        if other_count > 0:
            st.info(
                f"ℹ️ Other or special-handling detections: {other_count}"
            )

        if st.button(
            "🗑️ Clear Session History",
            use_container_width=True,
            key="clear_history",
        ):
            st.session_state.history = []
            st.session_state.last_file_hash = None
            st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption("♻️ GreenVision AI")
st.caption("Turning Every Waste Decision into a Sustainable Impact.")
st.caption("Prototype powered by YOLO computer vision and Streamlit.")