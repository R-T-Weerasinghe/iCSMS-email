## How to run Backend

- Ensure all the prerequisits are installed
- If not, navigate to ./backend/ in cmd and execute **pip install -r requirements.txt**
- Put credentials.json you obtained from Google Cloud Platform to ./backend/Email/
- Navigate to ./backend/DB in cmd and execute **uvicorn main:app --reload** to start the server
- Run ./backend/Email/main.py file to obtain and view your emails (latest 3 emails will be shown)
