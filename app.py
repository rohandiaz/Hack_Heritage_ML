from flask import Flask, request, render_template, jsonify
from surprise import Dataset, SVD, Reader
import pandas as pd

app = Flask(__name__)

# Load and train the recommendation model
def load_model():
    # Load the dataset
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()

    # Use SVD for matrix factorization
    model = SVD()
    model.fit(trainset)

    return model, trainset

model, trainset = load_model()

# Dummy freelancer data (replace with actual data and logic)
freelancers = {
    '1': {'name': 'Alice', 'skills': ['Python', 'Data Analysis'], 'hourly_rate': 50},
    '2': {'name': 'Bob', 'skills': ['JavaScript', 'Web Development'], 'hourly_rate': 40},
    '3': {'name': 'Charlie', 'skills': ['Machine Learning', 'Python'], 'hourly_rate': 60},
    # Add more freelancers
}

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission and provide recommendations
@app.route('/recommend', methods=['POST'])
def recommend():
    project_type = request.form.get('project_type')
    skills_needed = request.form.get('skills_needed').split(',')  # Example input: "Python, Data Analysis"
    budget = float(request.form.get('budget'))

    # Dummy ranking logic (replace with your actual recommendation logic)
    # Here we're just sorting freelancers by hourly rate for demonstration purposes
    ranked_freelancers = sorted(freelancers.items(), key=lambda x: x[1]['hourly_rate'])

    recommendations = []
    for fid, info in ranked_freelancers:
        if any(skill in skills_needed for skill in info['skills']):
            recommendations.append({
                'name': info['name'],
                'skills': info['skills'],
                'hourly_rate': info['hourly_rate']
            })

    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
