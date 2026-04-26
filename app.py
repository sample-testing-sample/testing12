import uvicorn

from quadra_diag.main import app


if __name__ == "__main__":
    uvicorn.run("quadra_diag.main:app", host="127.0.0.1", port=8000, reload=True)
