from flask import Flask, render_template, request, session
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

@app.route('/', methods=['GET', 'POST'])
def home():
    print("Request method:", request.method)  # Debugging print
    file_path = session.get('file_path', None)
    print("Initial session file path:", file_path)  # Debugging print

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            print("File selected:", file.filename)  # Debugging print
            if file.filename != '':
                file_path = os.path.join('static', file.filename)
                file.save(file_path)
                session['file_path'] = file_path  # Save file path in session
                print("File saved to:", file_path)  # Debugging print
            else:
                session.pop('file_path', None)  # Clear the session if no file is uploaded
                file_path = None
                print("No file uploaded, session cleared.")  # Debugging print

    graph_html = ""

    # Check if the file path is valid and file exists before creating the plot
    if file_path and os.path.exists(file_path):
        print("File path valid, reading data from:", file_path)  # Debugging print
        # Read data
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()

        # Ensure Date column is in the correct format
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')

        # Filter data based on user input
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if start_date and end_date:
            start_date = pd.to_datetime(start_date, format='%Y-%m-%d')
            end_date = pd.to_datetime(end_date, format='%Y-%m-%d')
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        # Create a plot
        fig = px.line(df, x='Date', y=['Revenue', 'Expense'], title='Financial Overview')
        graph_html = pio.to_html(fig, full_html=False)
    else:
        print("No valid file path, skipping plot creation.")  # Debugging print

    return render_template('home.html', graph_html=graph_html)

@app.route('/bar_chart')
def bar_chart():
    file_path = session.get('file_path', None)  # Get the file path from the session
    print("Session file path for bar chart:", file_path)  # Debugging print

    graph_html = ""

    if file_path and os.path.exists(file_path):
        print("File path valid for bar chart, reading data from:", file_path)  # Debugging print
        # Read data
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()

        # Ensure Date column is in the correct format
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce')

        # Create a bar chart
        fig = px.bar(df, x='Date', y=['Revenue', 'Expense'], title='Financial Overview - Bar Chart')
        graph_html = pio.to_html(fig, full_html=False)
    else:
        print("No valid file path for bar chart, skipping plot creation.")  # Debugging print

    return render_template('home.html', graph_html=graph_html)

if __name__ == "__main__":
    app.run(debug=True)
