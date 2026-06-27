#!/usr/bin/env python3
"""
HTTP Transport MCPサーバー（IP電話対応版）
"""

from fastmcp import FastMCP, Context
import requests
import os
import json

mcp = FastMCP(
        name="HTTP Calculator",
        instructions="今日のお題について件数を取得して、その件数のコンテンツを取得します。"
        )



DIR = "/tmp/"

@mcp.prompt()
def revirw_tile()->str:
    return f"今日のお題の結果を表示してください。"

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
async def get_all_articles(analysis_type:str)->list[dict]:
    """ 今日のリストを analysis_type で解析して結果を返します。"""

    if analysis_type == 'bart-large':
        UL_URL=f"http://{os.getenv('DOMAIN_NAME')}:8861/summarize/json?q=bart-large-cnn"
        print("Use bart-large-cnn")
    else:
        UL_URL=f"http://{os.getenv('DOMAIN_NAME')}:8861/summarize/json?q=pegasus-xsum"
        print("Use pegasus-xsum(default)")

    DL_URL=f"http://{os.getenv('DOMAIN_NAME')}:8863/"
    response = requests.get(DL_URL)
    length = int(response.text)
    print(f"{str(length)}件のデータを{analysis_type}で取得します。")
    
    results=[]
    for num in range(length):
        DL_URL=f"http://{os.getenv('DOMAIN_NAME')}:8863/filename/{str(num)}"
        response = requests.get(DL_URL)
        filename = f"/tmp/{response.text}"
        print(f"Download {filename}")
        
        with open(filename, "wb") as f:
            response = requests.get(f"http://{os.getenv('DOMAIN_NAME')}:8863/distribute/{str(num)}", stream=True)
            if not response.ok:
                return response
            for chunk in response.iter_content(1024):
                if not chunk:
                    break
                f.write(chunk)

        files = {
                "file": ("tmp.pdf", open(filename, "rb"))
        }
        
        response = requests.post(UL_URL, files=files)

        # JSON を受け取る
        print(response.status_code)
        print(response.json())
    
        results.append({filename,response.json()['summary']})
    
    return results

@mcp.tool()
async def get_article_summarize(item:str,sum_type:str,cxt:Context)->str:
    """ item を sum_type を使って解析した結果を返す。"""
    filename=f"/tmp/{item}"

    if sum_type == 'bart-large':
        UL_URL=f"http://{os.getenv('DOMAIN_NAME')}:8861/summarize/json?q=bart-large-cnn"
        print("Use bart-large-cnn")
    else:
        UL_URL=f"http://{os.getenv('DOMAIN_NAME')}:8861/summarize/json?q=pegasus-xsum"
        print("Use pegasus-xsum(default)")

    files = {
            "file": ("tmp.pdf", open(filename, "rb"))
    }
    response = requests.post(UL_URL, files=files)

    # JSON を受け取る
    print(response.status_code)
    print(response.json())
    
    return response.json()['summary']

@mcp.tool()
async def get_summarize(sum_type:str,cxt:Context)->str:
    """ 今日のお題を sum_type を使って取得する。"""

    fname="tmp.pdf"
    if sum_type == 'bart-large':
        UL_URL=f"http://{os.getenv('DOMAIN_NAME')}:8861/summarize/json?q=bart-large-cnn"
        print("Use bart-large-cnn")
    else:
        UL_URL=f"http://{os.getenv('DOMAIN_NAME')}:8861/summarize/json?q=pegasus-xsum"
        print("Use pegasus-xsum(default)")

    with open(fname, "wb") as f:
        response = requests.get(f"https://arxiv.org/pdf/2606.27334", stream=True)
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
