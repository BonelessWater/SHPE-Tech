# Project Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setup Python Virtual Environment](#setup-python-virtual-environment)
3. [Install Backend Dependencies](#install-backend-dependencies)
4. [Setup Frontend (Node & NPM)](#setup-frontend-node--npm)
5. [Running the Flask App](#running-the-flask-app)
6. [Testing the Setup](#testing-the-setup)
7. [Troubleshooting](#troubleshooting)
8. [Summary](#summary)

---

## Prerequisites

Make sure you have the following software installed on your system:

- **Python** (Version 3.8 or higher)
- **pip** (Python package manager)
- **Node.js** and **npm** (Node Package Manager)
- **Flask** (Python microframework)

### Check if Python and pip are installed:
```bash
python --version
pip --version
```

### Check if Node.js and npm are installed:
```bash
node --version
npm --version
```

###Setup Python Virtual Environment
It’s recommended to create a virtual environment to isolate dependencies.

Create a virtual environment:
```bash
python -m venv venv
```

###Activate the virtual environment:
Windows:

```bash
venv\Scripts\activate
```
macOS/Linux:
```bash
source venv/bin/activate
```
Verify the virtual environment is active.
You should see (venv) at the beginning of your terminal prompt.

# Install Backend Dependencies

With the virtual environment activated, install the required Python packages.

### Create a `requirements.txt` file if it doesn't exist. Add the required packages:

```makefile
requirements.txt
Flask==2.3.2
flask_cors
python_dotenv
openai
```

Install dependencies using pip:
```bash
pip install -r requirements.txt
```
