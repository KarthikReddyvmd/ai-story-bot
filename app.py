import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Cultural Story Weaver AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stTextArea textarea {
        font-size: 16px;
    }
    .generated-content {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False

def configure_api(api_key):
    """Configure the Gemini API"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        st.session_state.model = model
        st.session_state.api_configured = True
        return True
    except Exception as e:
        st.error(f"API Configuration failed: {str(e)}")
        return False

def generate_content(theme, language, style, length, custom_prompt=""):
    """Generate content using Gemini"""
    
    length_guide = {
        "Short (2-3 paragraphs)": "2-3 paragraphs or 8-10 lines",
        "Medium (4-5 paragraphs)": "4-5 paragraphs or 12-16 lines",
        "Long (6-8 paragraphs)": "6-8 paragraphs or 20-24 lines"
    }
    
    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = f"""You are a culturally-aware creative writer. Generate a {style} in {language} language.

Theme: {theme}
Style: {style}
Length: {length_guide[length]}

Requirements:
1. Write ENTIRELY in {language} (no English unless it's English language request)
2. Incorporate authentic cultural elements and details
3. Make it engaging and vivid with rich descriptions
4. Use appropriate literary devices for the {style} format
5. Ensure cultural sensitivity and accuracy

Generate the {style} now:"""

    try:
        with st.spinner('🤖 AI is crafting your content...'):
            response = st.session_state.model.generate_content(prompt)
            
            result = {
                "content": response.text,
                "theme": theme,
                "language": language,
                "style": style,
                "length": length,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "custom": bool(custom_prompt)
            }
            
            st.session_state.history.append(result)
            return result
            
    except Exception as e:
        st.error(f"Generation failed: {str(e)}")
        return None

def translate_content(text, target_language):
    """Translate and explain content"""
    prompt = f"""Translate the following text to {target_language} and provide cultural context:

Text: {text}

Format:
Translation: [translated text]
Cultural Notes: [brief explanation of cultural elements]"""

    try:
        with st.spinner('🌍 Translating...'):
            response = st.session_state.model.generate_content(prompt)
            return response.text
    except Exception as e:
        return f"Translation failed: {str(e)}"

# Main App
def main():
    # Header
    st.title("✨ Cultural Story Weaver AI")
    st.markdown("### Generate creative content in any language with cultural intelligence")
    
    # Sidebar for API configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input(
            "Gemini API Key", 
            type="password",
            help="Get your free API key from https://makersuite.google.com/app/apikey"
        )
        
        if api_key and not st.session_state.api_configured:
            if st.button("Connect API"):
                if configure_api(api_key):
                    st.success("✅ API Connected!")
                    st.rerun()
        
        if st.session_state.api_configured:
            st.success("✅ API Active")
            
        st.markdown("---")
        
        # Language suggestions
        st.header("🌍 Popular Languages")
        st.markdown("""
        - Spanish, French, German
        - Hindi, Urdu, Bengali
        - Chinese, Japanese, Korean
        - Arabic, Hebrew, Persian
        - Russian, Portuguese, Italian
        - And 100+ more!
        """)
        
        st.markdown("---")
        
        # Quick stats
        if st.session_state.history:
            st.header("📊 Stats")
            st.metric("Total Generations", len(st.session_state.history))
            languages = set([h['language'] for h in st.session_state.history])
            st.metric("Languages Used", len(languages))
    
    # Main content area
    if not st.session_state.api_configured:
        st.warning("👈 Please enter your Gemini API key in the sidebar to start")
        
        with st.expander("🔑 How to get your API key (Free!)"):
            st.markdown("""
            1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Sign in with your Google account
            3. Click "Create API Key"
            4. Copy and paste it in the sidebar
            
            The free tier is generous and perfect for this project!
            """)
        return
    
    # Tabs for different features
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎨 Generate", 
        "🌍 Translate", 
        "📚 History",
        "🎯 Custom Prompt"
    ])
    
    # Tab 1: Generate Content
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.text_input(
                "🎭 Cultural Theme",
                placeholder="e.g., Japanese tea ceremony, Indian Diwali, Mexican Day of the Dead",
                help="Enter any cultural theme, tradition, or concept"
            )
            
            style = st.selectbox(
                "📝 Content Style",
                ["Story", "Poem", "Description", "Dialogue", "Letter", "Myth"]
            )
            
        with col2:
            language = st.text_input(
                "🗣️ Target Language",
                placeholder="e.g., Spanish, Hindi, Arabic, Japanese",
                help="The AI will generate content entirely in this language"
            )
            
            length = st.selectbox(
                "📏 Content Length",
                ["Short (2-3 paragraphs)", "Medium (4-5 paragraphs)", "Long (6-8 paragraphs)"]
            )
        
        if st.button("✨ Generate Content", type="primary", use_container_width=True):
            if not theme or not language:
                st.warning("Please fill in both theme and language!")
            else:
                result = generate_content(theme, language, style, length)
                
                if result:
                    st.success("✅ Content generated successfully!")
                    st.markdown("### Generated Content:")
                    st.markdown(f"**Theme:** {result['theme']} | **Language:** {result['language']} | **Style:** {result['style']}")
                    st.markdown("---")
                    st.markdown(result['content'])
                    
                    # Download button
                    st.download_button(
                        label="📥 Download as Text",
                        data=result['content'],
                        file_name=f"{theme.replace(' ', '_')}_{language}.txt",
                        mime="text/plain"
                    )
    
    # Tab 2: Translate
    with tab2:
        st.markdown("### Translate & Explain Previous Content")
        
        if not st.session_state.history:
            st.info("Generate some content first to use translation!")
        else:
            selected_idx = st.selectbox(
                "Select content to translate",
                range(len(st.session_state.history)),
                format_func=lambda x: f"{st.session_state.history[x]['timestamp']} - {st.session_state.history[x]['theme']} ({st.session_state.history[x]['language']})"
            )
            
            selected_content = st.session_state.history[selected_idx]
            
            st.markdown("**Original Content:**")
            st.info(selected_content['content'][:300] + "..." if len(selected_content['content']) > 300 else selected_content['content'])
            
            target_lang = st.text_input("Translate to language:", placeholder="e.g., English, French, German")
            
            if st.button("🌍 Translate & Explain"):
                if target_lang:
                    translation = translate_content(selected_content['content'], target_lang)
                    st.markdown("### Translation & Cultural Context:")
                    st.success(translation)
    
    # Tab 3: History
    with tab3:
        st.markdown("### 📚 Generation History")
        
        if not st.session_state.history:
            st.info("No history yet. Start generating content!")
        else:
            # Option to clear history
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🗑️ Clear History"):
                    st.session_state.history = []
                    st.rerun()
            
            # Display history
            for i, item in enumerate(reversed(st.session_state.history)):
                with st.expander(f"📄 {item['timestamp']} - {item['theme']} ({item['language']})"):
                    st.markdown(f"**Style:** {item['style']} | **Length:** {item['length']}")
                    st.markdown("---")
                    st.markdown(item['content'])
                    
                    st.download_button(
                        label="📥 Download",
                        data=item['content'],
                        file_name=f"{item['theme'].replace(' ', '_')}_{item['language']}.txt",
                        key=f"download_{i}"
                    )
    
    # Tab 4: Custom Prompt
    with tab4:
        st.markdown("### 🎯 Advanced: Custom Prompt Mode")
        st.info("Write your own custom prompt for complete control over the AI generation")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            custom_theme = st.text_input("Theme (for tracking)", placeholder="e.g., Custom Epic Tale")
            custom_language = st.text_input("Language (for tracking)", placeholder="e.g., Sanskrit")
        
        with col2:
            custom_style = st.text_input("Style (for tracking)", value="Custom")
            custom_length = st.selectbox("Length", ["Short (2-3 paragraphs)", "Medium (4-5 paragraphs)", "Long (6-8 paragraphs)"], key="custom_length")
        
        custom_prompt = st.text_area(
            "Your Custom Prompt",
            placeholder="Write your custom instructions for the AI here...\nExample: Write an epic tale in Sanskrit about...",
            height=200
        )
        
        if st.button("🚀 Generate with Custom Prompt", type="primary"):
            if custom_prompt and custom_theme and custom_language:
                result = generate_content(custom_theme, custom_language, custom_style, custom_length, custom_prompt)
                
                if result:
                    st.success("✅ Custom content generated!")
                    st.markdown("### Result:")
                    st.markdown(result['content'])

if __name__ == "__main__":
    main()