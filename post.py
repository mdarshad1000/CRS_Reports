from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/accept-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Ensure that the file is a pdf
    if file.content_type != 'application/pdf':
        return {"error": "Please upload a PDF file."}
    
    # For example, to save the file you could do:
    with open(file.filename, "wb") as buffer:
        buffer.write(file.file.read())
    
    return {"filename": file.filename}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("post:app", host="0.0.0.0", port=9000)