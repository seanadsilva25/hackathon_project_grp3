import os
from dotenv import load_dotenv
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', '.env'))
load_dotenv(env_path)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)