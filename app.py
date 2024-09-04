import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for matplotlib

from flask import Flask, request, jsonify, render_template
import PyPDF2
import re
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text() or ''
        text += page_text
    return text

def preprocess_text(text):
    """Preprocess text by lowering the case and removing non-alphanumeric characters."""
    text = text.lower()
    text = re.sub(r'[\-\n]', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

def extract_skills(text, skills):
    """Extract and match skills from the text using more flexible matching."""
    matched_skills = []
    text = preprocess_text(text)

    for skill in skills:
        skill_lower = skill.lower()
        # Use regex to improve matching by allowing for variations and partial matches
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text):
            matched_skills.append(skill)
        else:
            print(f"Skill not found: {skill_lower}")  # Debug: Print skills not found

    return matched_skills

def calculate_match_score(matched_skills, total_skills):
    """Calculate the match score based on matched skills."""
    match_percentage = (len(matched_skills) / total_skills) * 100
    return match_percentage

def create_pie_chart(match_percentage):
    """Create a pie chart to represent the match score."""
    labels = ['Matched Skills', 'Remaining Skills']
    sizes = [match_percentage, 100 - match_percentage]
    colors = ['#4CAF50', '#FF7043']
    explode = (0.05, 0)

    buf = io.BytesIO()
    plt.figure(figsize=(7, 7))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')
    plt.title('Skill Match Score')
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Get required skills and optional additional skills
        skills = request.form.get('skills', '').split(',')
        additional_skills = request.form.get('additionalSkills', '').split(',')
        
        # Strip extra spaces and remove empty strings
        skills = [skill.strip() for skill in skills if skill.strip()]
        additional_skills = [skill.strip() for skill in additional_skills if skill.strip()]
        
        # Combine skills and ensure all are unique
        all_skills = list(set(skills + additional_skills))  # Combine and deduplicate
        
        # Debug: Print the combined list of all skills
        print(f"Skills: {skills}")
        print(f"Additional Skills: {additional_skills}")
        print(f"All Skills: {all_skills}")

        # Check if a file part exists in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        # Check if a file was selected
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Process the file if it's a PDF
        if file and file.filename.endswith('.pdf'):
            extracted_text = extract_text_from_pdf(file)
            
            # Debug: Print the extracted text from the PDF
            if not extracted_text:
                print("Extracted text is empty.")
            else:
                print(f"Extracted Text: {extracted_text[:1000]}")  # Print first 1000 chars for debugging
            
            matched_skills = extract_skills(extracted_text, all_skills)
            
            # Debug: Print the matched skills
            print(f"Matched Skills: {matched_skills}")
            
            # Calculate missing skills
            missing_skills = list(set(all_skills) - set(matched_skills))
            
            # Calculate match score using all skills
            match_score = calculate_match_score(matched_skills, len(all_skills))  # Use all_skills for total count
            
            # Debug: Print the match score
            print(f"Match Score: {match_score}")

            # Create the pie chart
            pie_chart = create_pie_chart(match_score)

            # Return JSON response with results
            return jsonify({
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "match_score": match_score,
                "pie_chart": pie_chart
            })

        # Return an error if the file is not a PDF
        return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        # Log the exception and return a generic error message
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the request"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
