# Backend Setup

1. Create virtual environment:
   ```
   python3 -m venv venv
   ```

2. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Update .env file with your Gemini API key

5. Run server:
   ```
   uvicorn main:app --reload --port 8000
   ```

6. Visit http://localhost:8000/docs for API documentation
