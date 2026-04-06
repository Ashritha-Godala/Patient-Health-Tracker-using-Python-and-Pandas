# create a virtual environment in a folder called .venv

python3 -m venv .venv

# activate the environment

source .venv/bin/activate # on Linux / macOS

# or

.\.venv\Scripts\activate # on Windows PowerShell

# install dependencies from requirements.txt

pip install -r requirements.txt

# activate the environment AGAIN

source .venv/bin/activate # on Linux / macOS

# run streamlit app

streamlit run app.py
