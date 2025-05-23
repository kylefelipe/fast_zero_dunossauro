from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from fast_zero.routers import auth, todos, users
from fast_zero.schemas import Message

app = FastAPI()

app.include_router(users.router)
app.include_router(todos.router)
app.include_router(auth.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
async def read_root_async():
    return {'message': 'Olá Mundo'}


@app.get('/html', status_code=HTTPStatus.OK, response_class=HTMLResponse)
async def send_html():
    return """
    <html>
        <head>
            <title>FastAPI HTML</title>
        </head>
        <body>
            <h1>Olá Mundo</h1>
        </body>
    </html>
    """
