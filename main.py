# backend/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import aiosqlite
import os
from decimal import Decimal, ROUND_DOWN
from pydantic import BaseModel

DB_PATH = os.getenv("DB_PATH", "balls_bot.db")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS","").split(",") if x.strip().isdigit()}

app = FastAPI(title="Plays.io MiniApp Backend")

app.mount("/static", StaticFiles(directory="../web", html=True), name="static")  # serve front-end files

# money helper
def to_decimal(a):
    d = a if isinstance(a, Decimal) else Decimal(str(a))
    return d.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

# initialize DB (simple)
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance TEXT DEFAULT '0.00'
        );
        CREATE TABLE IF NOT EXISTS tx (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT,
            amount TEXT,
            status TEXT,
            meta TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        await db.commit()

@app.on_event("startup")
async def startup():
    await init_db()

# Simple endpoints ------------------------------------------------
class DepositReq(BaseModel):
    user_id: int
    amount: str

@app.post("/api/deposit")
async def deposit(req: DepositReq):
    amt = to_decimal(req.amount)
    if amt <= 0:
        raise HTTPException(status_code=400, detail="invalid amount")
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("INSERT INTO tx (user_id,type,amount,status,meta) VALUES (?,?,?,?,?)",
                               (req.user_id, "deposit", str(amt), "pending", "webapp"))
        await db.commit()
        txid = cur.lastrowid
    return {"ok": True, "tx_id": txid, "status": "pending"}

class WithdrawReq(BaseModel):
    user_id: int
    amount: str

@app.post("/api/withdraw")
async def withdraw(req: WithdrawReq):
    amt = to_decimal(req.amount)
    if amt <= 0:
        raise HTTPException(status_code=400, detail="invalid amount")
    # check balance
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT balance FROM users WHERE user_id = ?", (req.user_id,))
        row = await cur.fetchone()
        bal = to_decimal(row[0]) if row else to_decimal("0.00")
        if bal < amt:
            raise HTTPException(status_code=400, detail="insufficient_balance")
        cur = await db.execute("INSERT INTO tx (user_id,type,amount,status,meta) VALUES (?,?,?,?,?)",
                               (req.user_id, "withdraw", str(amt), "pending", "webapp"))
        await db.commit()
        txid = cur.lastrowid
    return {"ok": True, "tx_id": txid, "status": "pending"}

@app.get("/api/balance/{user_id}")
async def get_balance(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        bal = str(to_decimal(row[0])) if row else "0.00"
    return {"user_id": user_id, "balance": bal}

# Serve web app index (optional)
@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("../web/index.html")
