import uvicorn
from fastapi import FastAPI
from utils.rest_api import app
from utils.injection.containers import Container

async def start_rest_server(container: Container):
    app.container = container
    SECOND_PORT_GRPC = 9999
    print(f'REST API running on port {SECOND_PORT_GRPC}...')
    config = uvicorn.Config(app, host="0.0.0.0", port=SECOND_PORT_GRPC, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
