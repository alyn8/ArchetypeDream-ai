import streamlit as st
from langchain_groq import ChatGroq
from PIL import Image
import urllib.parse
import requests
import time
import io
import os


st.markdown("""
    <style>
            
    @import url('https://fonts.googleapis.com/css2?family=Modern+Antiqua&display=swap');
    
    html, body, [class*="css"], .main, .stMarkdown, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Modern Antiqua', serif !important;
    }
            
    h1, h2, h3 {
        color: #E0E0E0; 
        letter-spacing: 1px;
    }

    /* Ana arka plan rengi */
    .stApp {
        background: linear-gradient(to bottom, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    
    /* Buton tasarımı */
    div.stButton > button:first-child {
        background-color: #6a11cb;
        color: white;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
 

    /* Sidebar (Yan menü) tasarımı */
    [data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }
    </style>
    """, unsafe_allow_html=True)


st.set_page_config(page_title="Archetype AI", page_icon="🌙", layout="centered")
# --- DİL SEÇİMİ ---
lang = st.sidebar.selectbox("Language / Dil", ["TR", "EN"])


text = {
    "TR": {
        "title": "🌙 Archetype: Bilinçdışı Rehberi",
        "subtitle": "*Jungiyen Perspektif, MBTI & Mistik Görseller*",
        "mbti_label": "MBTI Tipin:",
        "mbti_options": ["INFJ", "INTJ", "INFP", "ENFJ", "ENTP", "INTP", "ISTJ", "ISFJ", "ENTJ", "ESTP", "ESFP", "Bilmiyorum"],
        "num_label": "Rüyanda sayı gördün mü?",
        "num_input": "Gördüğün sayı:",
        "dream_placeholder": "Rüyanı tüm detaylarıyla anlat...",
        "analyze_btn": "Rüya Analizini Başlat 🔮",
        "image_btn": "Rüyanın Resmini Oluştur 🎨",
        "spinner_analyze": "Kolektif Bilinçdışı Analiz Ediliyor...",
        "spinner_image": "Yapay Zeka Sanatçısı Çiziyor...",
        "report_header": "🔮 Bilinçdışı Raporu",
        "canvas_header": "🎨 Bilinçdışının Tuvali",
        "warning": "Lütfen bir rüya giriniz.",
        "success_analyze": "Rüyanız analiz edildi.",
        "success_img": "Görsel başarıyla oluşturuldu!",
        "system_prompt": "Sen uzman bir Jungiyen Analist ve MBTI Danışmanısın. Türkçe cevap ver."
    },
    "EN": {
        "title": "🌙 Archetype: Unconscious Guide",
        "subtitle": "*Jungian Perspective, MBTI & Mystic Visuals*",
        "mbti_label": "Your MBTI Type:",
        "mbti_options": ["INFJ", "INTJ", "INFP", "ENFJ", "ENTP", "INTP", "ISTJ", "ISFJ", "ENTJ", "ESTP", "ESFP", "Unknown"],
        "num_label": "Did you see a number?",
        "num_input": "The number you saw:",
        "dream_placeholder": "Describe your dream in detail...",
        "analyze_btn": "Start Dream Analysis 🔮",
        "image_btn": "Generate Dream Image 🎨",
        "spinner_analyze": "Analyzing Collective Unconscious...",
        "spinner_image": "AI Artist is painting...",
        "report_header": "🔮 Unconscious Report",
        "canvas_header": "🎨 Canvas of the Unconscious",
        "warning": "Please enter a dream.",
        "success_analyze": "Your dream has beeen analyzed.",
        "success_img": "Image generated successfully!",
        "system_prompt": "You are an expert Jungian Analyst and MBTI Consultant. Answer in English."
    }
}


#groq 
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
else:
    user_groq=st.sidebar.text_input("Groq API Key giriniz",type="password")
    if user_groq:
        os.environ["GROQ_API_KEY"]=user_groq
#HuggingFace

if "HF_TOKEN" in st.secrets:
    HF_TOKEN =st.secrets["HF_TOKEN"]
else:
    user_hf= st.sidebar.text_input("Hugging Face Token giriniz",type="password")
    if user_hf:
        HF_TOKEN = user_hf


API_URL = "https://api-inference.huggingface.co/models/Lykon/DreamShaper_v8"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "x-use-cache": "false",
    "x-wait-for-model": "true" 
}


# Model
llm = ChatGroq(model_name="llama-3.1-8b-instant")

st.title(text[lang]["title"])
st.markdown(text[lang]["subtitle"])
st.markdown("---")


col1, col2 = st.columns([2,3])

with col1:

    mbti = st.selectbox(text[lang]["mbti_label"], text[lang]["mbti_options"])

with col2:
    
    options = ["Evet","Hayır"] if lang == "TR" else["Yes","No"]
    sayi_gordu_mu = st.radio(text[lang]["num_label"],options,horizontal=True)
    if sayi_gordu_mu in ["Evet", "Yes"]:
        en_sevilen_sayi = st.number_input(text[lang]["num_input"],min_value=0, step=1)
    else:
        en_sevilen_sayi ="None"    
    
dream_text = st.text_area(text[lang]["dream_placeholder"], height=200)



col_b1, col_b2 = st.columns(2)

with col_b1:
    analyze_button = st.button(text[lang]["analyze_btn"], use_container_width=True)
with col_b2:
    generate_image_button = st.button(text[lang]["image_btn"], use_container_width=True)



if analyze_button:
    if dream_text:
        with st.spinner(text[lang]["spinner_analyze"]):
            
            full_prompt = f"{text[lang]['system_prompt']}\n\nMBTI: {mbti}\nNumber:{en_sevilen_sayi}\nDream: {dream_text}"
            
            try:
                response = llm.invoke(full_prompt)
                st.subheader(text[lang]["report_header"])
                st.markdown(response.content)
                st.success(text[lang]["success_analyze"])
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning(text[lang]["warning"])




if generate_image_button:
    if dream_text:
        with st.spinner(text[lang]["spinner_image"]):
            try:
                # Promptu alıyoruz
                prompt_eng = llm.invoke(f"Create a 1-sentence, highly descriptive English visual art prompt for an oil painting based on this dream: {dream_text}")
                clean_prompt = prompt_eng.content.replace('"', '').replace("'", "")
                
                
                encoded_prompt = urllib.parse.quote(clean_prompt) 
                
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"

                response = requests.get(image_url)

                if response.status_code ==200:
                    st.subheader(text[lang]["canvas_header"])
                    st.image(response.content, use_container_width=True)
                    st.info(f"✨ Technical Note: {clean_prompt}")
                    st.success(text[lang]["success_img"])
                else:
                    st.error("Görsel motoru şu an meşgul, lütfen birkaç saniye sonra tekrar dene.")
            except Exception as e:
                st.error(f"Görselleştirme sırasında bir sorun oluştu: {e}")
    else:
        st.warning(text[lang]["warning"])
       

st.markdown("---")
st.caption("Archetype-AI Project - Jungian AI Intelligence v1.0")