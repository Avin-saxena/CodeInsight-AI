## Demo Video

![Demo Video](https://github.com/Avin-saxena/Tunable_labs_assessment/blob/master/demo_video/Untitled%20design.gif?raw=true)


# Code Analysis Tool with React Frontend and FastAPI Backend

Welcome to the Code Analysis Tool project! This application allows users to upload Python code files (app.py and api.py), perform static code analysis using an Abstract Syntax Tree (AST) parser, generate detailed insights, ask questions powered by OpenAI's GPT-4 model, and visualize the code structure through Mermaid diagrams.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Project Scripts](#project-scripts)
- [Testing](#testing)
- [Security Considerations](#security-considerations)

## Features

* **Upload Python Files**: Users can upload app.py and api.py files for analysis
* **AST Parsing**: Utilize Tree Sitter to parse the code and extract detailed information
* **Function and Class Analysis**: Extract relationships, function definitions, class hierarchies, imports, and more
* **GPT-4 Integration**: Ask questions about the codebase, powered by OpenAI's GPT-4 model
* **Mermaid Diagrams**: Generate visual diagrams (flowcharts and class diagrams) representing the code structure
* **Interactive Frontend**: A React-based frontend provides an intuitive user interface
* **FastAPI Backend**: A robust backend handles analysis, GPT queries, and diagram generation

## Prerequisites

* Python 3.7 or higher
* Node.js and npm
* OpenAI API Key: Required for GPT-4 integration and Mermaid diagram generation
* Git: For cloning the repository

## Project Structure

```
project_root/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── requirements.txt    
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py
│   │   │   ├── gpt.py
│   │   │   └── mermaid.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── code_analyzer.py
│   │       ├── gpt_analyzer.py
│   │       └── mermaid_generator.py
│   └── .env
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   ├── components/
│   │   │   ├── UploadFiles.js
│   │   │   ├── AnalysisResults.js
│   │   │   ├── GPTQuestions.js
│   │   │   └── MermaidDiagram.js
│   └── package.json
├── scripts/
│   ├── app.py
│   ├── api.py
│   ├── code_analyzer.py
│   ├── gpt_analyzer.py
│   └── mermaid_generator.py
└── README.md
```

## Installation

### Backend Setup

1. Clone the Repository
    ```bash
    git clone https://github.com/Avin-saxena/Tunable_labs_assessment
    cd Tunable_labs_assessment/backend
    ```

2. Create a Virtual Environment
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install Dependencies
    ```bash
    pip install -r backend/app/requirements.txt
    ```


### Frontend Setup

1. Navigate to Frontend Directory
    ```bash
    cd ../frontend
    ```

2. Install Dependencies
    ```bash
    npm install
    npm install mermaid
    ```

## Configuration

### OpenAI API Key Setup

1. Create a .env file in the backend directory:
    ```bash
    cd ../backend
    touch .env
    ```

2. Add your OpenAI API key to the .env file:
    ```
    OPENAI_API_KEY=your-openai-api-key
    ```

**Important**: Do not commit the .env file to version control.

## Running the Application

### Starting the Backend Server

1. Navigate to Backend Directory
    ```bash
    cd backend
    ```

2. Activate Virtual Environment
    ```bash
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Start the Server
    ```bash
    uvicorn app.main:app --reload
    ```
    The backend will be running at http://localhost:8000.

### Starting the Frontend Server

1. Navigate to Frontend Directory
    ```bash
    cd ../frontend
    ```

2. Start the React App
    ```bash
    npm start
    ```
    The frontend will be running at http://localhost:3000.

## Usage

1. Access the Application
   * Open your browser and navigate to http://localhost:3000

2. Upload Files
   * Click on Upload Files
   * Select your app.py and api.py files

3. Analyze Code
   * Click on Analyze to perform the static code analysis
   * The analysis results will be displayed

4. Ask Questions to GPT-4
   * In the Ask GPT section, enter a question about the codebase
   * Click on Ask to get a response powered by GPT-4

5. Generate Mermaid Diagrams
   * Select the diagram type (flowchart or class)
   * Click on Generate to create the diagram
   * The diagram will be rendered on the page

## Project Scripts

### code_analyzer.py
Location: `backend/app/services/code_analyzer.py`
```python
from app.services.code_analyzer import analyze_code

app_code = '...contents of app.py...'
api_code = '...contents of api.py...'

analysis_result = analyze_code(app_code, api_code)
```

### gpt_analyzer.py
Location: `backend/app/services/gpt_analyzer.py`
```python
from app.services.gpt_analyzer import analyze_with_gpt

analysis_data = {...}  # Output from code_analyzer
question = "What functions does api.py have?"

result = analyze_with_gpt(analysis_data, question)
```

### mermaid_generator.py
Location: `backend/app/services/mermaid_generator.py`
```python
from app.services.mermaid_generator import generate_mermaid_diagram

analysis_data = {...}  # Output from code_analyzer
diagram_type = "flowchart"

result = generate_mermaid_diagram(analysis_data, diagram_type)
```
