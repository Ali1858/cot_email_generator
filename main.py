from app.routes import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# curl -X POST "http://127.0.0.1:8000/generate_message" \
#      -H "Content-Type: application/json" \
#      -d @data/sample_input_john.json