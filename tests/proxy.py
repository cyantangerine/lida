import httpx
from fastapi import FastAPI, Request

app = FastAPI()

# 目标服务器配置
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 11435
TARGET_PATH = "/v1/chat/completions"

# 创建HTTP客户端
client = httpx.AsyncClient(
    base_url=f"http://{TARGET_HOST}:{TARGET_PORT}",
    timeout=httpx.Timeout(90.0)
)

@app.post("/{path:path}")
async def proxy_post(request: Request, path: str):
    """
    将POST请求代理到目标服务器
    """
    try:
        # 获取原始请求体
        body = await request.body()

        # 构建目标URL
        # target_url = f"{TARGET_PATH}/{path}" if path else TARGET_PATH
        target_url = TARGET_PATH

        # 转发请求到目标服务器
        response = await client.post(
            target_url,
            content=body,
            headers=dict(request.headers),
            params=dict(request.query_params)
        )

        # 返回目标服务器的响应
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    except Exception as e:
        return {"error": f"Proxy error: {str(e)}"}
#
# @app.get("/{path:path}")
# async def proxy_get(request: Request, path: str):
#     """
#     将GET请求代理到目标服务器
#     """
#     try:
#         # 构建目标URL
#         target_url = f"{TARGET_PATH}/{path}" if path else TARGET_PATH
#
#         # 转发请求到目标服务器
#         response = await client.get(
#             target_url,
#             headers=dict(request.headers),
#             params=dict(request.query_params)
#         )
#
#         # 返回目标服务器的响应
#         return Response(
#             content=response.content,
#             status_code=response.status_code,
#             headers=dict(response.headers)
#         )
#
#     except Exception as e:
#         return {"error": f"Proxy error: {str(e)}"}

# 添加Response导入
from fastapi.responses import Response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=11435)
