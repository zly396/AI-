# AI婚恋系统 (AI Matchmaking System)

> 基于AI深度学习的智能婚恋匹配平台 —— 完整设计文档

---

## 项目简介

AI婚恋系统是一款结合人工智能与婚恋社交的创新平台。通过MBTI性格分析、大五人格测评、协同过滤推荐算法和深度学习模型，为用户提供精准、高效、安全的婚恋匹配服务。

### 核心技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | **Java Spring Boot 3.x** | 微服务架构 |
| AI引擎 | **Python + PyTorch** | 匹配算法/情感分析/内容审核 |
| 前端 | **Vue 3 + TypeScript** | SPA单页应用 |
| 数据库 | **PostgreSQL 15** | 主数据库 |
| 缓存 | **Redis 7** | 推荐缓存/会话管理 |
| 消息推送 | **WebSocket** | 实时聊天 |
| 搜索引擎 | **Elasticsearch** | 消息全文检索 |
| 消息队列 | **RabbitMQ** | 异步任务/事件驱动 |
| 对象存储 | **OSS/MinIO** | 图片/语音存储 |
| 移动端 | **Flutter** | iOS / Android |

---

## 文档导航

| 序号 | 文档 | 路径 | 说明 |
|------|------|------|------|
| 1 | PRD | [docs/01-PRD.md](./docs/01-PRD.md) | 产品需求文档 |
| 2 | User Story | [docs/02-User-Story.md](./docs/02-User-Story.md) | 用户故事（22个） |
| 3 | Use Case | [docs/03-Use-Case.md](./docs/03-Use-Case.md) | 用例描述（11个） |
| 4 | 主UI设计 | [docs/04-UI-Design.md](./docs/04-UI-Design.md) | 8个核心页面设计 |
| 5 | Class Diagram | [docs/05-Class-Diagram.md](./docs/05-Class-Diagram.md) | 类图+ER图 |
| 6 | DFD | [docs/06-DFD.md](./docs/06-DFD.md) | 数据流图 (Level 0-2) |
| 7 | State Diagram | [docs/07-State-Diagram.md](./docs/07-State-Diagram.md) | 状态图（7种） |

---

## 项目结构

```
ai-matchmaking-system/
├── README.md                   # 项目总览
├── docs/                       # 设计文档
│   ├── 01-PRD.md               # 产品需求文档
│   ├── 02-User-Story.md        # 用户故事
│   ├── 03-Use-Case.md          # 用例文档
│   ├── 04-UI-Design.md         # 主UI设计
│   ├── 05-Class-Diagram.md     # 类图设计
│   ├── 06-DFD.md               # 数据流图
│   └── 07-State-Diagram.md     # 状态图
├── backend/                    # Java Spring Boot 后端（规划中）
├── ai-engine/                  # Python AI引擎（规划中）
├── frontend/                   # Vue3 前端（规划中）
└── mobile/                     # Flutter 移动端（规划中）
```

---

## 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                        Nginx / API Gateway                  │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│          │          │          │          │                │
│  Vue3    │ Flutter  │ Spring   │ Spring   │  Spring Boot   │
│  Web     │ Mobile   │ Boot     │ Boot     │  Admin         │
│  Portal  │ App      │ API      │ Chat     │  Backend       │
│          │          │ Gateway  │ Service  │                │
└──────────┴──────────┴────┬─────┴────┬─────┴───────┬────────┘
                           │          │             │
              ┌────────────┼──────────┼─────────────┼──────────┐
              │            ▼          ▼             ▼          │
              │     ┌──────────┐ ┌──────────┐ ┌──────────┐    │
              │     │ Match    │ │ Chat     │ │ AI       │    │
              │     │ Service  │ │ Service  │ │ Service  │    │
              │     └────┬─────┘ └────┬─────┘ └────┬─────┘    │
              │          │            │            │           │
              │          ▼            ▼            ▼           │
              │     ┌──────────────────────────────────┐      │
              │     │         Python AI Engine         │      │
              │     │   (FastAPI + PyTorch + Transformers)│    │
              │     └──────────────────────────────────┘      │
              │                                                │
              │  ┌──────────┐ ┌──────────┐ ┌──────────┐      │
              │  │PostgreSQL│ │  Redis   │ │  RabbitMQ│      │
              │  └──────────┘ └──────────┘ └──────────┘      │
              └────────────────────────────────────────────────┘
```

---

## 核心功能

### MVP (V1.0)
- ✅ 手机号注册/登录 + JWT鉴权
- ✅ 实名认证 (OCR + 活体检测)
- ✅ AI性格测试 (MBTI + 大五人格)
- ✅ 智能匹配推荐 (每日20人)
- ✅ 心仪/跳过卡片交互
- ✅ 即时文字聊天 (WebSocket)
- ✅ AI破冰话题推荐
- ✅ 基础管理后台

### 后续版本
- 🔜 AI聊天教练
- 🔜 视频通话 (WebRTC)
- 🔜 社区内容 + 直播
- 🔜 线下活动组织

---

## 匹配算法

```
MatchScore = 0.25 × BasicMatch(年龄/地域/学历/收入)
           + 0.30 × PersonalityMatch(MBTI兼容度/大五人格)
           + 0.20 × InterestMatch(协同过滤/兴趣标签)
           + 0.10 × AppearanceMatch(AI颜值偏好)
           + 0.15 × BehaviorWeight(历史行为/活跃度)
```

---

## GitHub 仓库

🔗 **GitHub Repository:** [https://github.com/ai-matchmaking-system/ai-matchmaking](https://github.com/ai-matchmaking-system/ai-matchmaking)

```bash
# 克隆仓库
git clone https://github.com/ai-matchmaking-system/ai-matchmaking.git

# 进入项目
cd ai-matchmaking
```

---

## 快速开始（规划中）

```bash
# 1. 启动后端服务
cd backend
./mvnw spring-boot:run

# 2. 启动AI引擎
cd ai-engine
python -m uvicorn main:app --port 8000

# 3. 启动前端
cd frontend
npm install && npm run dev
```

---

## 团队与贡献

| 角色 | 职责 |
|------|------|
| 产品经理 | PRD、需求管理、优先级排序 |
| Java后端工程师 | Spring Boot API开发、数据库设计 |
| Python AI工程师 | 匹配算法、情感分析、推荐系统 |
| 前端工程师 | Vue3 Web端、Flutter移动端 |
| UI/UX设计师 | 界面设计、交互原型 |

---

## 许可证

本项目为商业项目，代码和文档版权归项目团队所有。

---

> 📅 创建日期: 2026-06-16 | 🏗️ 当前阶段: 设计阶段
