## How to run Backend

- Ensure all the prerequisits are installed
- If not, navigate to ./backend/ in cmd and execute **pip install -r requirements.txt**
- Put credentials.json you obtained from Google Cloud Platform to ./backend/Email/
- Ensure mongoDB is installed locally
- Navigate to ./backend in cmd and execute **uvicorn Server:app --reload** to start the server
- Run Main.py in ./backend
