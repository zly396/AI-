"""
AI婚恋系统 - FastAPI后端服务器
运行: pip install -r requirements.txt && python server.py
"""
import os, json, hashlib, uuid, random
from datetime import datetime as dt, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="AI婚恋系统", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DB = os.path.join(os.path.dirname(__file__), "data.db")
SECRET_KEY = "ai-matchmaking-secret-2026"
DEMO_PASSWORD_HASH = "d833d60a29d4f6244b8fb2dc9e2af9cac1e6c3c88cada92bb2c3f4e1d33e8e71"

def get_db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA foreign_keys=ON"); return c

def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT UNIQUE, password_hash TEXT, nickname TEXT DEFAULT '', gender TEXT DEFAULT '', age INTEGER DEFAULT 0, city TEXT DEFAULT '', height INTEGER DEFAULT 0, education TEXT DEFAULT '', occupation TEXT DEFAULT '', income TEXT DEFAULT '', bio TEXT DEFAULT '', mbti TEXT DEFAULT '', love_values TEXT DEFAULT '', interests TEXT DEFAULT '', photos TEXT DEFAULT '[]', verified INTEGER DEFAULT 0, vip TEXT DEFAULT 'none', vip_expire TEXT DEFAULT '', status TEXT DEFAULT 'active', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS matches (id INTEGER PRIMARY KEY AUTOINCREMENT, from_uid INTEGER, to_uid INTEGER, action TEXT, is_mutual INTEGER DEFAULT 0, score REAL DEFAULT 0, reason TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, match_id INTEGER UNIQUE, uid1 INTEGER, uid2 INTEGER, ice TEXT DEFAULT '[]', last_msg TEXT DEFAULT '', last_at TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sid INTEGER, sender_id INTEGER, receiver_id INTEGER, type TEXT DEFAULT 'text', content TEXT, status TEXT DEFAULT 'sent', sent_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, token TEXT UNIQUE, expires TEXT);
    """)
    # Seed 10 demo users if empty
    if not db.execute("SELECT 1 FROM users LIMIT 1").fetchone():
        users = [
            (1,'13800000001','小雨','female',26,'北京朝阳',165,'本科','设计师','20_30W','热爱生活，喜欢旅行和摄影~','ENFP','浪漫型,成长型','旅行,摄影,美食,电影','["https://picsum.photos/seed/u1/400/500"]'),
            (2,'13800000002','阿杰','male',28,'北京海淀',178,'硕士','工程师','30_50W','简单的人，喜欢运动和看书','ISTJ','稳定型,家庭型','跑步,阅读,编程,篮球','["https://picsum.photos/seed/u2/400/500"]'),
            (3,'13800000003','思思','female',25,'北京西城',162,'本科','教师','10_20W','温柔善良，喜欢小朋友','ISFJ','家庭型,稳定型','画画,音乐,烘焙,瑜伽','["https://picsum.photos/seed/u3/400/500"]'),
            (4,'13800000004','小宇','male',30,'北京丰台',180,'本科','创业者','50W_ABOVE','性格开朗，事业稳定','ENTJ','成长型,冒险型','创业,投资,旅行,健身','["https://picsum.photos/seed/u4/400/500"]'),
            (5,'13800000005','小文','female',27,'上海浦东',168,'硕士','金融分析师','30_50W','独立自信，热爱生活','INFJ','浪漫型,成长型','艺术展,咖啡,读书,瑜伽','["https://picsum.photos/seed/u5/400/500"]'),
            (6,'13800000006','浩然','male',32,'上海静安',175,'博士','医生','30_50W','有责任心，期待组建家庭','INFP','家庭型,浪漫型','读书,音乐,跑步,公益','["https://picsum.photos/seed/u6/400/500"]'),
            (7,'13800000007','晓晓','female',24,'深圳南山',160,'本科','新媒体运营','10_20W','活力满满，喜欢探索世界','ESFP','冒险型,浪漫型','探店,跳舞,旅行,摄影','["https://picsum.photos/seed/u7/400/500"]'),
            (8,'13800000008','子轩','male',29,'深圳福田',182,'硕士','产品经理','30_50W','理性与感性并存','INTJ','成长型,稳定型','科技,摄影,登山,咖啡','["https://picsum.photos/seed/u8/400/500"]'),
            (9,'13800000009','馨月','female',28,'广州天河',163,'本科','律师','20_30W','独立但不强势','ESTJ','稳定型,成长型','法律,辩论,跑步,阅读','["https://picsum.photos/seed/u9/400/500"]'),
            (10,'13800000010','博文','male',31,'广州越秀',176,'博士','教授','20_30W','温和儒雅，学识渊博','INTP','成长型,浪漫型','学术,哲学,旅行,摄影','["https://picsum.photos/seed/u10/400/500"]'),
        ]
        for u in users:
            db.execute("INSERT INTO users (id,phone,password_hash,nickname,gender,age,city,height,education,occupation,income,bio,mbti,love_values,interests,photos,verified) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)", (u[0],u[1],DEMO_PASSWORD_HASH,*u[2:]))
    db.commit(); db.close()

init_db()

# ─── Helpers ───
def hpw(pw): return hashlib.sha256(f"{pw}:{SECRET_KEY}".encode()).hexdigest()

def make_token(uid):
    db = get_db(); t = str(uuid.uuid4())
    db.execute("INSERT INTO tokens (uid,token,expires) VALUES (?,?,?)", (uid, t, (dt.now()+timedelta(days=7)).isoformat()))
    db.commit(); db.close(); return t

def auth(token):
    db = get_db()
    r = db.execute("SELECT u.* FROM tokens t JOIN users u ON t.uid=u.id WHERE t.token=? AND t.expires>?", (token, dt.now().isoformat())).fetchone()
    db.close()
    if not r: raise HTTPException(401, "请重新登录")
    return dict(r)

# ─── Match Algorithm ───
COMPATIBLE = {
    "ENFP-INFJ":18,"INFJ-ENFP":18,"ENFP-INTJ":15,"INTJ-ENFP":15,"ENTJ-INTP":16,"INTP-ENTJ":16,
    "ISFJ-ESTJ":14,"ESTJ-ISFJ":14,"ISTJ-ESFP":13,"ESFP-ISTJ":13,"INFP-ENFJ":17,"ENFJ-INFP":17,
    "ESTP-ISFP":12,"ISFP-ESTP":12,"ENFP-ENFP":10,"INFJ-INFJ":10
}

def match_score(uid1, uid2):
    db = get_db()
    u1 = dict(db.execute("SELECT * FROM users WHERE id=?",(uid1,)).fetchone())
    u2 = dict(db.execute("SELECT * FROM users WHERE id=?",(uid2,)).fetchone())
    db.close()
    s, reasons = 50.0, []
    if u1.get("age") and u2.get("age"):
        d = abs(u1["age"]-u2["age"])
        if d<=3: s+=15; reasons.append("年龄相仿")
        elif d<=6: s+=8
    c1, c2 = (u1.get("city")or"")[:2], (u2.get("city")or"")[:2]
    if c1 and c2 and c1==c2: s+=10; reasons.append("同城")
    if u1.get("education")==u2.get("education") and u1.get("education"): s+=5; reasons.append("学历匹配")
    pair = f"{u1.get('mbti','')}-{u2.get('mbti','')}"
    if pair in COMPATIBLE: s+=COMPATIBLE[pair]; reasons.append(f"MBTI互补({u1['mbti']}×{u2['mbti']})")
    else: s+=5
    i1 = set((u1.get("interests")or"").split(","))
    i2 = set((u2.get("interests")or"").split(","))
    common = i1&i2
    if common: s+=min(len(common)*4,20); reasons.append(f"共同爱好:{','.join(list(common)[:3])}")
    v1 = set((u1.get("love_values")or"").split(","))
    v2 = set((u2.get("love_values")or"").split(","))
    if v1&v2: s+=min(len(v1&v2)*5,15); reasons.append("价值观契合")
    return {"score": min(round(s,1),99.0), "reasons": reasons[:4]}

def recommend(uid, limit=20):
    db = get_db()
    me = dict(db.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone())
    tg = "male" if me["gender"]=="female" else "female"
    done = set(r[0] for r in db.execute("SELECT to_uid FROM matches WHERE from_uid=?",(uid,)).fetchall())
    done.add(uid)
    fmt = ','.join(map(str,done)) if done else '0'
    rows = db.execute(f"SELECT * FROM users WHERE gender=? AND status='active' AND id NOT IN ({fmt}) ORDER BY RANDOM() LIMIT 100",(tg,)).fetchall()
    db.close()
    res = []
    for r in rows[:limit]:
        d = dict(r)
        d["photos"] = json.loads(d.get("photos")or"[]")
        d["interests"] = (d.get("interests")or"").split(",")
        d["love_values"] = (d.get("love_values")or"").split(",") if d.get("love_values") else []
        for k in ["password_hash"]: d.pop(k,None)
        mi = match_score(uid, r["id"])
        d["match_score"] = mi["score"]; d["match_reason"] = "; ".join(mi["reasons"])
        res.append(d)
    res.sort(key=lambda x:x["match_score"], reverse=True)
    return res

# ─── Pydantic Models ───
class RegisterReq(BaseModel):
    phone: str; password: str; nickname: Optional[str] = None

class LoginReq(BaseModel):
    phone: str; password: str

class ProfileReq(BaseModel):
    nickname: Optional[str]=None; gender: Optional[str]=None; age: Optional[int]=None; city: Optional[str]=None
    height: Optional[int]=None; education: Optional[str]=None; occupation: Optional[str]=None
    income: Optional[str]=None; bio: Optional[str]=None; mbti: Optional[str]=None
    love_values: Optional[str]=None; interests: Optional[str]=None; photos: Optional[str]=None

class LikeReq(BaseModel):
    to_uid: int; action: str = "like"

class SendMsgReq(BaseModel):
    sid: int; content: str; type: str = "text"

# ─── API Routes ───
@app.post("/api/register")
def register(req: RegisterReq):
    db = get_db()
    if db.execute("SELECT 1 FROM users WHERE phone=?",(req.phone,)).fetchone(): db.close(); raise HTTPException(400,"手机号已注册")
    if len(req.password)<6: db.close(); raise HTTPException(400,"密码至少6位")
    nick = req.nickname or f"缘客_{random.randint(1000,9999)}"
    db.execute("INSERT INTO users (phone,password_hash,nickname) VALUES (?,?,?)",(req.phone,hpw(req.password),nick))
    db.commit(); uid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    token = make_token(uid); db.close()
    return {"code":0,"data":{"token":token,"uid":uid,"nickname":nick}}

@app.post("/api/login")
def login(req: LoginReq):
    db = get_db()
    u = db.execute("SELECT * FROM users WHERE phone=?",(req.phone,)).fetchone()
    if not u or u["password_hash"] not in (hpw(req.password), DEMO_PASSWORD_HASH): db.close(); raise HTTPException(401,"手机号或密码错误")
    if u["status"]!="active": db.close(); raise HTTPException(403,"账户已禁用")
    token = make_token(u["id"]); db.close()
    return {"code":0,"data":{"token":token,"uid":u["id"],"nickname":u["nickname"]}}

@app.get("/api/me")
def me(token: str = Query(...)):
    u = auth(token)
    u["photos"] = json.loads(u.get("photos")or"[]")
    u["interests"] = (u.get("interests")or"").split(",") if u.get("interests") else []
    u["love_values"] = (u.get("love_values")or"").split(",") if u.get("love_values") else []
    for k in ["password_hash"]: u.pop(k,None)
    return {"code":0,"data":u}

@app.put("/api/profile")
def profile(req: ProfileReq, token: str = Query(...)):
    u = auth(token)
    db = get_db()
    updates = {k:v for k,v in req.dict().items() if v is not None}
    if updates:
        sets = ", ".join(f"{k}=?" for k in updates)
        db.execute(f"UPDATE users SET {sets}, updated_at=datetime('now','localtime') WHERE id=?", list(updates.values())+[u["id"]])
        db.commit()
    db.close()
    return {"code":0,"msg":"更新成功"}

@app.get("/api/recommendations")
def recommendations(token: str = Query(...)):
    u = auth(token)
    return {"code":0,"data":recommend(u["id"])}

@app.post("/api/like")
def like(req: LikeReq, token: str = Query(...)):
    u = auth(token)
    if req.to_uid==u["id"]: raise HTTPException(400,"不能操作自己")
    db = get_db()
    if db.execute("SELECT 1 FROM matches WHERE from_uid=? AND to_uid=?",(u["id"],req.to_uid)).fetchone(): db.close(); raise HTTPException(400,"已操作过")
    mi = match_score(u["id"],req.to_uid)
    db.execute("INSERT INTO matches (from_uid,to_uid,action,score,reason) VALUES (?,?,?,?,?)",(u["id"],req.to_uid,req.action,mi["score"],"; ".join(mi["reasons"])))
    mutual = db.execute("SELECT id FROM matches WHERE from_uid=? AND to_uid=? AND action IN ('like','super_like')",(req.to_uid,u["id"])).fetchone()
    result = {"is_mutual":False}
    if mutual:
        db.execute("UPDATE matches SET is_mutual=1 WHERE from_uid=? AND to_uid=?",(u["id"],req.to_uid))
        db.execute("UPDATE matches SET is_mutual=1 WHERE id=?",(mutual["id"],))
        mr = db.execute("SELECT id FROM matches WHERE from_uid=? AND to_uid=? AND action IN ('like','super_like')",(u["id"],req.to_uid)).fetchone()
        mid = mr["id"] if mr else mutual["id"]
        if not db.execute("SELECT 1 FROM sessions WHERE match_id=?",(mid,)).fetchone():
            ice = json.dumps(["你们都喜欢什么类型的音乐？","最近有什么有趣的计划？","最喜欢的旅行目的地是哪里？","分享一件最近让你开心的小事吧~"], ensure_ascii=False)
            db.execute("INSERT INTO sessions (match_id,uid1,uid2,ice) VALUES (?,?,?,?)",(mid,u["id"],req.to_uid,ice))
        result = {"is_mutual":True,"match_id":mid}
    db.commit(); db.close()
    msg = "匹配成功！💕 你们互相心仪了！" if result["is_mutual"] else "已发送心仪信号 ❤️"
    return {"code":0,"data":result,"msg":msg}

@app.get("/api/sessions")
def sessions(token: str = Query(...)):
    u = auth(token)
    db = get_db()
    rows = db.execute("SELECT * FROM sessions WHERE uid1=? OR uid2=? ORDER BY COALESCE(last_at,created_at) DESC",(u["id"],u["id"])).fetchall()
    res = []
    for r in rows:
        d = dict(r); pid = r["uid2"] if r["uid1"]==u["id"] else r["uid1"]
        p = db.execute("SELECT id,nickname,photos,age,city,mbti FROM users WHERE id=?",(pid,)).fetchone()
        if p:
            pd = dict(p); pd["photos"] = json.loads(pd.get("photos")or"[]"); d["partner"] = pd
        d["ice"] = json.loads(d.get("ice")or"[]")
        d["unread"] = db.execute("SELECT COUNT(*) FROM messages WHERE sid=? AND receiver_id=? AND status!='read'",(d["id"],u["id"])).fetchone()[0]
        res.append(d)
    db.close()
    return {"code":0,"data":res}

@app.get("/api/messages/{sid}")
def messages(sid: int, token: str = Query(...)):
    u = auth(token)
    db = get_db()
    rows = db.execute("SELECT * FROM messages WHERE sid=? ORDER BY sent_at ASC",(sid,)).fetchall()
    db.close()
    return {"code":0,"data":[dict(r) for r in rows]}

@app.get("/api/my-matches")
def my_matches(token: str = Query(...)):
    u = auth(token)
    db = get_db()
    rows = db.execute("""
        SELECT m.id,m.from_uid,m.to_uid,m.score,m.reason,m.created_at,u2.id as pid,u2.nickname,u2.age,u2.city,u2.occupation,u2.photos,u2.mbti
        FROM matches m JOIN users u2 ON (CASE WHEN m.from_uid=? THEN u2.id=m.to_uid ELSE u2.id=m.from_uid END)
        WHERE m.is_mutual=1 AND (m.from_uid=? OR m.to_uid=?)
        ORDER BY m.created_at DESC
    """,(u["id"],u["id"],u["id"])).fetchall()
    db.close()
    res = []; seen = set()
    for r in rows:
        d = dict(r); d["photos"] = json.loads(d.get("photos")or"[]")
        if d["pid"] not in seen: seen.add(d["pid"]); res.append(d)
    return {"code":0,"data":res}

@app.get("/api/who-liked-me")
def who_liked_me(token: str = Query(...)):
    u = auth(token)
    db = get_db()
    rows = db.execute("SELECT m.id,m.from_uid,m.action,m.score,m.created_at,u2.nickname,u2.age,u2.city,u2.occupation,u2.photos,u2.mbti FROM matches m JOIN users u2 ON m.from_uid=u2.id WHERE m.to_uid=? AND m.action IN ('like','super_like') AND m.is_mutual=0 ORDER BY m.created_at DESC",(u["id"],)).fetchall()
    db.close()
    return {"code":0,"data":[dict(r) for r in rows]}

@app.post("/api/messages")
def send_msg(req: SendMsgReq, token: str = Query(...)):
    u = auth(token)
    db = get_db()
    s = db.execute("SELECT * FROM sessions WHERE id=?",(req.sid,)).fetchone()
    if not s: db.close(); raise HTTPException(404,"会话不存在")
    rid = s["uid2"] if s["uid1"]==u["id"] else s["uid1"]
    db.execute("INSERT INTO messages (sid,sender_id,receiver_id,type,content) VALUES (?,?,?,?,?)",(req.sid,u["id"],rid,req.type,req.content))
    db.execute("UPDATE sessions SET last_msg=?,last_at=datetime('now','localtime') WHERE id=?",(req.content[:50],req.sid))
    db.commit(); db.close()
    return {"code":0,"msg":"发送成功"}

@app.get("/api/ai-coach")
def ai_coach(sid: int, token: str = Query(...)):
    auth(token)
    suggestions = [
        {"style":"幽默 😄","text":"哈哈，你说话真有意思~ 有没有什么特别难忘的经历？"},
        {"style":"真诚 😊","text":"我觉得和你聊天很舒服，希望能多了解你一些"},
        {"style":"好奇 🤔","text":"你周末通常喜欢做什么？有没有推荐的好去处？"},
    ]
    return {"code":0,"data":suggestions}

# ─── WebSocket ───
class WsMgr:
    def __init__(self): self.clients = {}
    async def connect(self, ws, uid): await ws.accept(); self.clients[uid] = ws
    def disconnect(self, uid): self.clients.pop(uid, None)
    async def send(self, uid, data):
        if uid in self.clients:
            try: await self.clients[uid].send_json(data)
            except: self.clients.pop(uid, None)

ws_mgr = WsMgr()

@app.websocket("/ws/{token}")
async def ws_chat(ws: WebSocket, token: str):
    try: u = auth(token)
    except: await ws.close(code=4001); return
    await ws_mgr.connect(ws, u["id"])
    try:
        while True:
            data = await ws.receive_json()
            sid, content = data.get("sid"), data.get("content","")
            db = get_db()
            s = db.execute("SELECT * FROM sessions WHERE id=?",(sid,)).fetchone()
            if not s: db.close(); continue
            rid = s["uid2"] if s["uid1"]==u["id"] else s["uid1"]
            db.execute("INSERT INTO messages (sid,sender_id,receiver_id,content) VALUES (?,?,?,?)",(sid,u["id"],rid,content))
            db.execute("UPDATE sessions SET last_msg=?,last_at=datetime('now','localtime') WHERE id=?",(content[:50],sid))
            db.commit(); db.close()
            await ws_mgr.send(rid, {"type":"new_msg","sid":sid,"content":content,"sender_id":u["id"],"nickname":u["nickname"]})
    except (WebSocketDisconnect, Exception): ws_mgr.disconnect(u["id"])

# ─── Static Frontend ───
@app.get("/", response_class=HTMLResponse)
def index():
    return open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8").read()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print(f"\n{'='*50}")
    print(f"  💕 AI婚恋系统 启动成功!")
    print(f"  🌐 浏览器打开: http://localhost:{port}")
    print(f"  📱 演示账号: 13800000001 ~ 13800000010")
    print(f"  🔑 密码: 123456")
    print(f"{'='*50}\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
