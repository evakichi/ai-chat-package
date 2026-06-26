#!/usr/bin/env python3
"""
HTTP Transport MCPサーバー（IP電話対応版）
"""

from fastmcp import FastMCP
import requests
import os

mcp = FastMCP("HTTP Calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """二つの数値を足し算します"""
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """二つの数値を掛け算します"""
    return a * b

@mcp.tool()
def calculate_power(base: float, exponent: float) -> float:
    """べき乗を計算します（base の exponent 乗）"""
    return base ** exponent

@mcp.tool()
def get_pegasus_summarize(dl_url:str)->str:
    """dl_url をダウンロードしてpegasusで要約します"""
    fname="tmp.pdf"
    print(os.getenv('DOMAIN_NAME'))
    UL_URL=f"http://{os.getenv('DOMAIN_NAME')}:8861/summarize/json?q=pegasus-xsum"
    
    with open(fname, "wb") as f:
        response = requests.get(dl_url, stream=True)
        if not response.ok:
            return response
        for chunk in response.iter_content(1024):
            if not chunk:
                break
            f.write(chunk)
    files = {
            "file": ("tmp.pdf", open(fname, "rb"))
    }
    response = requests.post(UL_URL, files=files)

    # JSON を受け取る
    print(response.status_code)
    print(response.json())

    return response.json()['summary']


@mcp.tool()
def get_bart_summarize(dl_url:str)->str:
    """dl_url をダウンロードしてbartで要約します"""
    fname="tmp.pdf"
    UL_URL="http://{os.getenv('DOMAIN_NAME')}:8861/summarize/json?q=bart-large-cnn"
    
    with open(fname, "wb") as f:
        response = requests.get(dl_url, stream=True)
        if not response.ok:
            return response
        for chunk in response.iter_content(1024):
            if not chunk:
                break
            f.write(chunk)
    files = {
            "file": ("tmp.pdf", open(fname, "rb"))
    }
    response = requests.post(UL_URL, files=files)

    # JSON を受け取る
    print(response.status_code)
    print(response.json())

    return response.json()['summary']

if __name__ == "__main__":
    print("🌐 HTTP MCP Server starting...")
    print("📡 Endpoint: http://localhost:8000/mcp")
    print("🔧 Tools: add, multiply, calculate_power")
    
    # HTTP Transportで起動
    mcp.run(
        transport="http",
        host="0.0.0.0", 
        port=8000,
        path="/mcp"
    )
