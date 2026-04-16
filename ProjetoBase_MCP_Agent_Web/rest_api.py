from fastapi import FastAPI
from crud_service import *

import uvicorn

app = FastAPI()

@app.get("/books")
def get_books():
    return read_book_list()

@app.post("/books")
def create_book_api(book: dict):
    return create_book(**book)

@app.put("/books/{id}")
def update_book_api(id: int, book: dict):
    return update_book(id, **book)

@app.delete("/books/{id}")
def delete_book_api(id: int):
    return delete_book(id)

def main():
    uvicorn.run(app, host="127.0.0.1", port=8003)

if __name__ == "__main__":
    main()
