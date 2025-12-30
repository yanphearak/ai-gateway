from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import json

app = FastAPI()

# Model → Backend mapping
MODEL_BACKENDS = {
    "Qwen/Qwen2.5-1.5B": "https://grubby-matilda-phearak-org-c38b3717.koyeb.app",
    "Qwen/Qwen2.5-14B-Instruct": "https://stable-merlina-phearak-org1-39a6c716.koyeb.app",
}

DEFAULT_BACKEND = "https://grubby-matilda-phearak-org-c38b3717.koyeb.app"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy(request: Request, path: str):
    body = await request.body()

    backend = DEFAULT_BACKEND

    # Try to detect model from JSON body
    if body:
        try:
            payload = json.loads(body)
            model = payload.get("model")
            if model in MODEL_BACKENDS:
                backend = MODEL_BACKENDS[model]
        except json.JSONDecodeError:
            pass

    url = f"{backend}/{path}"

    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient(timeout=300) as client:
        resp = await client.request(
            request.method,
            url,
            headers=headers,
            content=body,
            params=request.query_params,
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
        media_type=resp.headers.get("content-type"),
    )
