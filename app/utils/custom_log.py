import time
from typing import Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute
from loguru import logger as clog

clog.remove()
clog.add("app/zlogs/log_{time:YYYY_MM_DD}.log", rotation='10 MB', retention="30 days", backtrace=True, diagnose=True)


class LogRequest(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            clog.info('======================= START REQUEST =======================')
            clog.opt(colors=True).info(f"<g>Request URL</g>: [{request.method}] {request.url}")
            clog.opt(colors=True).info(f"<g>Request header</g>: {request.headers}")
            content_type = request.headers.get("content-type", "")
            if "multipart/form-data" in content_type:
                clog.opt(colors=True).info("<y>Skipped body logging (multipart/form-data)</y>")
            else:
                try:
                    body = await request.body()
                    clog.opt(raw=True).info(f"<g>Request body</g>: {body.decode('utf-8', errors='ignore')}")
                except Exception as e:
                    clog.opt(colors=True).warning(f"<r>Could not read request body: {e}</r>")
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            clog.opt(colors=True).info(f'<g>Response code</g>: {response.status_code}')
            if hasattr(response, "body"):
                clog.opt(raw=True).info(f"<g>Response data</g>: {getattr(response, 'body', b'')}")
            else:
                clog.opt(colors=True).info("<y>Response data</y>: [Streaming/File content]")
            clog.opt(colors=True).info(f'<r>Time execute</r>: {duration}')
            clog.info('======================= END   REQUEST =======================')
            return response

        return custom_route_handler
