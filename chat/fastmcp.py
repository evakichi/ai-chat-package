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
        instructions="""
        今日のダイジェストを出します。
        ダイジェストは番号とファイル名と概要の列を表示した表で出力します。
        そしてその番号に対応したファイル名のPDFをダウンロードできるURLを提示します。
        """
        )

@mcp.prompt()
def revirw_tile()->str:
    return f"今日のダイジェストを pegasus-xsum で返してください。"

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
def download_pdf(title:str)->str:
    """tilte のファイルのダウンロードURLを返します。"""
    URL = f"http://{os.getenv('DOMAIN_NAME')}:8863/download/{title}"
    print(URL)
    return URL

@mcp.tool()
async def get_all_articles(analysis_type="pagasus-xsum")->str:
    """ 今日のダイジェストを analysis_type で返します。"""

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
    
    results="""
    | 番号 | ファイル名 | 概要 |
    |-----|-----|-----|
    """
    for num in range(length):
        DL_URL=f"http://{os.getenv('DOMAIN_NAME')}:8863/filename/{str(num)}"
        response = requests.get(DL_URL)
        filename = response.text
        print(f"Download({str(num+1)}) {filename}")
        
        with open(f"/tmp/{filename}", "wb") as f:
            response = requests.get(f"http://{os.getenv('DOMAIN_NAME')}:8863/distribute/{str(num)}", stream=True)
            if not response.ok:
                return response
            for chunk in response.iter_content(1024):
                if not chunk:
                    break
                f.write(chunk)

        files = {
                "file": ("tmp.pdf", open(f"/tmp/{filename}", "rb"))
        }
        
        response = requests.post(UL_URL, files=files)

        # JSON を受け取る
        print(response.status_code)
        print(response.json())
        summary = response.json()['summary']
        results = results+"\n"+f"|{str(num+1)}|{filename}|{summary}|"
    
    return results

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
