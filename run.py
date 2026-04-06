import os
from dotenv import load_dotenv

load_dotenv()  # charge .env si présent

from flask_app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
