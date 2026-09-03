import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'frontend', '.env'))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)