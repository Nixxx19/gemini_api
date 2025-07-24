import streamlit as st
import os
import google.generativeai as genai

# --- CONFIG ---
GENAI_API_KEY = "YOUR_GEMINI_API_KEY"  # 🔁 Replace this with your Gemini API key
genai.configure(api_key=GENAI_API_KEY)

# Gemini model
model = genai.GenerativeModel("gemini-pro-vision")

# Prompt with added validation for video type
PROMPT = """
You are a professional badminton coach and computer vision expert.

First, confirm if this video shows badminton players executing shots in a rally or drill. 
If not, respond clearly: "Please upload a valid badminton video."

If it is badminton, perform a detailed frame-by-frame analysis using advanced badminton-specific terminology. For each shot, provide:

{
  "shot_type": "[e.g. smash, clear, drop, net shot, drive, lift, etc.]",
  "shuttle_speed_estimate_kmh": [approximate speed in km/h],
  "contact_point_on_racket": "[e.g. sweet spot, frame, off-center, top of strings]",
  "player_posture": "[describe stance – e.g. ready stance, crouch, off-balance]",
  "balance_after_shot": "[e.g. recovered well, off-balance, slow recovery]",
  "shot_quality": "[e.g. deceptive, weak, tight to net, attacking clear]",
  "improvement_suggestions": [
    "[Give coaching tips on technique, footwork, recovery, or positioning using terminology familiar to trained badminton players/coaches.]"
  ]
}

Repeat this analysis sequentially for each shot shown in the video. Assume Player 1 is on the near side, and Player 2 is on the far side unless visually labeled.

Conclude with general improvement suggestions per player.
"""

# --- UI ---
st.title("🏸 Badminton Video Analyzer")
st.markdown("Upload a badminton video to begin coaching analysis. (Short clips under ~20MB recommended.)")

# Supported video formats
ALLOWED_EXTENSIONS = ["mp4", "mov", "avi"]

uploaded_file = st.file_uploader("🎥 Upload a short badminton video", type=ALLOWED_EXTENSIONS)

if uploaded_file is not None:
    # Check extension
    file_ext = uploaded_file.name.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        st.error("❌ Unsupported file format. Please upload MP4, MOV, or AVI video.")
    else:
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("✅ Video uploaded and saved!")
        st.video(file_path)

        st.info("🔍 analyzing video ..")

        try:
            with open(file_path, "rb") as f:
                video_bytes = f.read()

            response = model.generate_content(
                contents=[
                    PROMPT,
                    {"mime_type": f"video/{file_ext}", "data": video_bytes}
                ],
                stream=False,
            )

            st.success("✅ Analysis Complete!")
            st.markdown("### 📝 Gemini Output:")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"❌ Error during Gemini analysis: {e}")

