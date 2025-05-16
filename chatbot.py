from flask import Flask, request, jsonify, render_template, Response
import openai  # Changed from "from openai import OpenAI"
from googletrans import Translator
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found in environment variables.")

openai.api_key = OPENAI_API_KEY  # Changed from client initialization
translator = Translator()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"response": "Please share how you're feeling or what's on your mind."})

    try:
        # Enhanced prompt for mental health analysis
        prompt = f"""
        The user is seeking mental health support. Here's what they shared:
        "{user_input}"
        
        Please provide a compassionate response that:
        1. Acknowledges their feelings
        2. Identifies potential mental health patterns
        3. Offers 3-5 practical strategies to improve mental wellbeing
        4. Suggests when professional help might be beneficial
        5. Provides encouragement and hope
        
        Structure your response with clear sections and bullet points.
        """

        response = openai.ChatCompletion.create(  # Changed from client.chat.completions.create
            model="gpt-4",
            messages=[
                {"role": "system", "content": """You are a compassionate mental health assistant. Provide:
                - Empathetic understanding of the user's situation
                - Actionable self-care strategies
                - Clear indicators when professional help is recommended
                - Hope and encouragement
                """},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.1
        )

        response_content = response['choices'][0]['message']['content'].strip()  # Changed access method
        
        # Format the response for better readability
        formatted_response = format_mental_health_response(response_content)

        try:
            translated_response = translator.translate(formatted_response, dest='ta').text
        except Exception as e:
            print(f"Translation error: {e}")
            translated_response = formatted_response

        return jsonify({
            "response": formatted_response,
            "translated_response": translated_response
        })
    except Exception as e:
        return jsonify({"response": f"I want to help but I'm having trouble processing that. Could you try rephrasing? Error: {str(e)}"})

def format_mental_health_response(text):
    """Format the response for better readability"""
    # Add section headers if not present
    if "1." not in text and "- " not in text:
        sections = text.split('\n\n')
        formatted = []
        headers = [
            "I hear you",
            "What might help",
            "When to seek professional support",
            "Remember"
        ]
        for i, section in enumerate(sections[:4]):
            if i < len(headers):
                formatted.append(f"**{headers[i]}**\n{section}")
            else:
                formatted.append(section)
        return '\n\n'.join(formatted)
    return text

@app.route('/quick-assessment', methods=['POST'])
def quick_assessment():
    """Endpoint for quick mental health check"""
    try:
        response = openai.ChatCompletion.create(  # Changed from client.chat.completions.create
            model="gpt-4",
            messages=[
                {"role": "system", "content": """Provide a brief mental health assessment with:
                - Current state evaluation
                - Immediate coping strategy
                - One self-care activity to try now"""},
                {"role": "user", "content": request.json.get('message', 'I need a quick mental health check')}
            ],
            max_tokens=400
        )
        return jsonify({"assessment": response['choices'][0]['message']['content']})  # Changed access method
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)