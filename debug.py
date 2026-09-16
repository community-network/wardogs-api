"""Run this to hot reload on changes"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8787, reload=True)

# poetry run debug.py
