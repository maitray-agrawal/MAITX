with open("app/main.py", "a", encoding="utf-8") as f:
    f.write("""
@app.get("/debug/env")
async def debug_env():
    import os
    key = os.getenv("FAST2SMS_KEY", "NOT SET")
    return {"key_length": len(key), "key_preview": key[:6] + "..." if len(key) > 6 else "TOO SHORT"}
""")
print("patched app/main.py")