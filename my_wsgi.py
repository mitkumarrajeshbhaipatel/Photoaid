from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware
from starlette.responses import JSONResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI on PythonAnywhere!"}

# Wrap FastAPI app as WSGI
wsgi_app = WSGIMiddleware(app)
