# AI婚恋系统 - 类图设计 (Class Diagram)

---

## 文档信息

| 项目 | 内容 |
|------|------|
| 产品名称 | AI婚恋系统 |
| 版本 | V1.0 |
| 创建日期 | 2026-06-16 |
| 后端框架 | Java Spring Boot |

---

## 1. 系统类图总览

```
                        ┌─────────────────────────────────────────┐
                        │           系统架构分层                   │
                        └─────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                           Controller Layer (控制器层)                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │AuthController│ │UserController│ │MatchController│ │ChatController │    │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘    │
│         │                │                │                │             │
├─────────┼────────────────┼────────────────┼────────────────┼─────────────┤
│         ▼                ▼                ▼                ▼             │
│                           Service Layer (服务层)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │AuthService   │ │UserService   │ │MatchService  │ │ChatService   │    │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘    │
│  ┌──────┴───────┐ ┌──────┴───────┐ ┌──────┴───────┐                   │
│  │VerifyService │ │ProfileService│ │AIEngineService│                   │
│  └──────────────┘ └──────────────┘ └──────────────┘                   │
│         │                │                │                             │
├─────────┼────────────────┼────────────────┼─────────────────────────────┤
│         ▼                ▼                ▼                             │
│                       Repository Layer (数据访问层)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │UserRepo  │ │MatchRepo │ │MessageRepo│ │OrderRepo │ │AuditRepo │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│         │                                                                 │
├─────────┼─────────────────────────────────────────────────────────────────┤
│         ▼                                                                 │
│                       Model Layer (实体层)                                 │
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐          │
│  │ User  │ │Profile│ │ Match │ │Message│ │ Order │ │ Audit │          │
│  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 核心实体类详细设计

### 2.1 User (用户)

```
┌──────────────────────────────────────────────┐
│                    User                       │
├──────────────────────────────────────────────┤
│ - id: Long (PK)                              │  ← 用户唯一ID
│ - phone: String (加密存储)                     │  ← 手机号
│ - password: String (BCrypt加密)               │  ← 密码HASH
│ - wechatOpenId: String                       │  ← 微信OpenID
│ - qqOpenId: String                           │  ← QQ OpenID
│ - status: UserStatus (ACTIVE/BANNED/DELETED) │  ← 账户状态
│ - vipLevel: VipLevel (NONE/MONTH/QUARTER/YEAR)│  ← VIP等级
│ - vipExpireAt: LocalDateTime                 │  ← VIP过期时间
│ - verified: Boolean                          │  ← 是否已实名
│ - createdAt: LocalDateTime                   │
│ - updatedAt: LocalDateTime                   │
├──────────────────────────────────────────────┤
│ + register(phone, password): User            │
│ + login(phone, password): String(JWT)        │
│ + upgradeVip(level): void                    │
│ + ban(): void                                │
│ + delete(): void                             │
└──────────────────────────────────────────────┘
         │ 1        1
         ├──────────────────────►┌──────────────────┐
         │                       │     Profile       │
         │                       └──────────────────┘
         │ 1        *
         └──────────────────────►┌──────────────────┐
                                 │      Photo        │
                                 └──────────────────┘
```

### 2.2 Profile (用户画像/资料)

```
┌──────────────────────────────────────────────┐
│                   Profile                     │
├──────────────────────────────────────────────┤
│ - id: Long (PK)                              │
│ - userId: Long (FK → User)                   │  ← 关联用户
│ - nickname: String                           │  ← 昵称
│ - gender: Gender (MALE/FEMALE)               │  ← 性别
│ - birthday: LocalDate                        │  ← 生日
│ - height: Integer (cm)                       │  ← 身高
│ - education: Education                       │  ← 学历枚举
│ - occupation: String                         │  ← 职业
│ - income: IncomeRange                        │  ← 收入范围枚举
│ - province: String                           │  ← 省
│ - city: String                               │  ← 市
│ - marriageStatus: MarriageStatus             │  ← 婚姻状况
│ - hasChildren: Boolean                       │  ← 是否有子女
│ - bio: Text                                  │  ← 个人简介(300字)
│ - completeness: Integer (0-100)              │  ← 资料完成度
│ - privacyLevel: PrivacyLevel                 │  ← 隐私级别
├──────────────────────────────────────────────┤
│ + calculateCompleteness(): int               │
│ + updateProfile(data: ProfileDTO): void      │
│ + setPrivacy(level): void                    │
└──────────────────────────────────────────────┘
         │ 1        1
         ├──────────────────────►┌──────────────────┐
         │                       │  PersonalityTest  │
         │                       └──────────────────┘
         │ 1        *
         └──────────────────────►┌──────────────────┐
                                 │  MatchPreference  │
                                 └──────────────────┘
```

### 2.3 PersonalityTest (性格测评)

```
┌──────────────────────────────────────────────┐
│               PersonalityTest                 │
├──────────────────────────────────────────────┤
│ - id: Long (PK)                              │
│ - userId: Long (FK)                          │
│ - mbtiType: String (ENFP/INTJ等)             │  ← MBTI类型
│ - eiScore: Double (外向-内向)                  │
│ - snScore: Double (感觉-直觉)                  │
│ - tfScore: Double (思考-情感)                  │
│ - jpScore: Double (判断-感知)                  │
│ - openness: Double (开放性 大五人格)            │
│ - conscientiousness: Double (尽责性)           │
│ - extraversion: Double (外向性)                │
│ - agreeableness: Double (宜人性)               │
│ - neuroticism: Double (神经质)                 │
│ - loveValues: List<LoveValue>                │  ← 婚恋价值观
│ - testCompletedAt: LocalDateTime             │
├──────────────────────────────────────────────┤
│ + calculateMBTI(): String                    │
│ + generateReport(): String                   │
│ + getCompatibleTypes(): List<String>         │
└──────────────────────────────────────────────┘

<<Enumeration>> MBTIType:
  INTP, INTJ, INFP, INFJ, ISTP, ISTJ, ISFP, ISFJ,
  ENTP, ENTJ, ENFP, ENFJ, ESTP, ESTJ, ESFP, ESFJ

<<Enumeration>> LoveValue:
  ROMANTIC, PRAGMATIC, GROWTH, FAMILY, ADVENTURE, STABILITY
```

### 2.4 MatchPreference (择偶偏好)

```
┌──────────────────────────────────────────────┐
│               MatchPreference                 │
├──────────────────────────────────────────────┤
│ - id: Long (PK)                              │
│ - userId: Long (FK)                          │
│ - minAge: Integer (18-70)                    │  ← 年龄范围
│ - maxAge: Integer                            │
│ - preferredGender: Gender                    │  ← 期望性别
│ - maxDistanceKm: Integer                     │  ← 最大距离
│ - minHeight: Integer                         │  ← 身高要求
│ - minEducation: Education                    │  ← 最低学历
│ - preferredMBTITypes: List<String>           │  ← 期望MBTI类型
│ - incomeRequirement: IncomeRange             │  ← 收入要求
├──────────────────────────────────────────────┤
│ + matches(target: Profile): boolean          │
└──────────────────────────────────────────────┘
```

### 2.5 Photo (用户照片)

```
┌──────────────────────────────────────────────┐
│                    Photo                      │
├──────────────────────────────────────────────┤
│ - id: Long (PK)                              │
│ - userId: Long (FK → User)                   │
│ - url: String (OSS地址)                       │
│ - thumbnailUrl: String                       │  ← 缩略图
│ - isPrimary: Boolean                         │  ← 是否主照片
│ - sortOrder: Integer                         │  ← 排序
│ - auditStatus: AuditStatus                   │  ← 审核状态
│ - aiFaceScore: Double                        │  ← AI颜值评分
│ - uploadedAt: LocalDateTime                  │
├──────────────────────────────────────────────┤
│ + submitAudit(): void                        │
│ + setPrimary(): void                         │
│ + delete(): void                             │
└──────────────────────────────────────────────┘
```

### 2.6 Match (匹配记录)

```
┌──────────────────────────────────────────────┐
│                    Match                      │
├──────────────────────────────────────────────┤
│ - id: Long (PK)                              │
│ - fromUserId: Long (FK → User)               │  ← 主动心仪方
│ - toUserId: Long (FK → User)                 │  ← 被心仪方
│ - action: MatchAction (LIKE/SUPER_LIKE/SKIP) │  ← 操作类型
│ - isMutual: Boolean                          │  ← 是否双向匹配
│ - matchScore: Double (0-100)                 │  ← 匹配度分数
│ - matchReason: String                        │  ← AI匹配理由
│ - matchedAt: LocalDateTime                   │  ← 匹配成功时间
│ - createdAt: LocalDateTime                   │
├──────────────────────────────────────────────┤
│ + checkMutual(): boolean                     │
│ + generateMatchReason(): String              │
└──────────────────────────────────────────────┘
```

### 2.7 Message (消息)

```
┌──────────────────────────────────────────────┐
│                   Message                     │
├──────────────────────────────────────────────┤
│ - id: Long (PK)                              │
│ - sessionId: Long (FK → ChatSession)         │  ← 会话ID
│ - senderId: Long (FK → User)                 │  ← 发送者
│ - receiverId: Long (FK → User)               │  ← 接收者
│ - type: MsgType (TEXT/IMAGE/VOICE/EMOJI)    │  ← 消息类型
│ - content: Text                              │  ← 消息内容
│ - status: MsgStatus (SENT/DELIVERED/READ)   │  ← 消息状态
│ - isRecalled: Boolean                        │  ← 是否撤回
│ - isAISuggestion: Boolean                    │  ← 是否AI建议
│ - sentAt: LocalDateTime                      │
├──────────────────────────────────────────────┤
│ + canRecall(): boolean (3分钟以内)            │
│ + recall(): void                             │
│ + markAsRead(): void                         │
└──────────────────────────────────────────────┘
```

### 2.8 ChatSession (聊天会话)

```
┌──────────────────────────────────────────────┐
│                 ChatSession                   │
├──────────────────────────────────────────────┤
│ - id: Long (PK)                              │
│ - matchId: Long (FK → Match)                 │  ← 关联匹配
│ - user1Id: Long                              │
│ - user2Id: Long                              │
│ - lastMessage: String                        │  ← 最后一条消息
│ - lastMessageAt: LocalDateTime               │
│ - iceBreakTopics: String (JSON Array)        │  ← 破冰话题
│ - aiCoachEnabled: Boolean (VIP)              │  ← AI教练开关
│ - createdAt: LocalDateTime                   │
├──────────────────────────────────────────────┤
│ + generateIceBreak(): List<String>           │
│ + getAISuggestions(): List<String>           │
└──────────────────────────────────────────────┘
```

### 2.9 Order / VipOrder (订单)

```
┌──────────────────────────────────────────────┐
│                   VipOrder                    │
├──────────────────────────────────────────────┤
│ - id: Long (PK)                              │
│ - orderNo: String (唯一订单号)                 │
│ - userId: Long (FK → User)                   │
│ - planType: VipLevel                         │  ← 套餐类型
│ - amount: BigDecimal                          │  ← 金额(元)
│ - payMethod: PayMethod (WECHAT/ALIPAY)      │  ← 支付方式
│ - status: OrderStatus (PENDING/PAID/REFUND) │  ← 订单状态
│ - paidAt: LocalDateTime                      │
│ - createdAt: LocalDateTime                   │
├──────────────────────────────────────────────┤
│ + createOrder(user, plan): VipOrder          │
│ + pay(): void                                │
│ + refund(): void                             │
└──────────────────────────────────────────────┘
```

### 2.10 AuditLog (审核/风控日志)

```
┌──────────────────────────────────────────────┐
│                   AuditLog                    │
├──────────────────────────────────────────────┤
│ - id: Long (PK)                              │
│ - targetType: AuditTarget (PHOTO/TEXT/USER) │  ← 审核对象类型
│ - targetId: Long                             │
│ - riskLevel: RiskLevel (LOW/MEDIUM/HIGH)    │  ← 风险等级
│ - aiDecision: AuditResult                    │  ← AI判定
│ - humanDecision: AuditResult                 │  ← 人工判定
│ - reviewerId: Long                           │  ← 审核员ID
│ - reason: String                             │  ← 审核原因
│ - createdAt: LocalDateTime                   │
├──────────────────────────────────────────────┤
│ + autoAudit(): AuditResult                   │
│ + manualAudit(result, reason): void          │
└──────────────────────────────────────────────┘
```

---

## 3. 核心Service类

### 3.1 MatchService (匹配服务)

```
┌──────────────────────────────────────────────┐
│                MatchService                   │
├──────────────────────────────────────────────┤
│ - userRepo: UserRepository                   │
│ - matchRepo: MatchRepository                 │
│ - aiEngineService: AIEngineService           │
│ - cacheService: RedisCacheService            │
├──────────────────────────────────────────────┤
│ + getDailyRecommendations(userId): List<UserProfileDTO> │
│ + performLike(fromUserId, toUserId): MatchResult │
│ + performSkip(fromUserId, toUserId): void    │
│ + calculateMatchScore(user1, user2): Double  │
│ + generateDailyList(userId): List<Long>      │  ← 后台任务
│ + getWhoLikedMe(userId, vipOnly): List       │
└──────────────────────────────────────────────┘

MatchScore计算权重:
  BasicMatch      25%  (年龄/地域/学历/收入)
  PersonalityMatch 30%  (MBTI兼容度/大五人格相似度)
  InterestMatch   20%  (协同过滤/兴趣标签)
  AppearanceMatch 10%  (AI颜值分析偏好)
  BehaviorWeight  15%  (历史行为/活跃度)
```

### 3.2 AIEngineService (AI引擎服务)

```
┌──────────────────────────────────────────────┐
│               AIEngineService                 │
├──────────────────────────────────────────────┤
│ - httpClient: RestTemplate                   │
│ - aiApiBaseUrl: String (Python AI服务)        │
├──────────────────────────────────────────────┤
│ + calculateCompatibility(user1, user2): MatchResult │
│ + analyzePhoto(image): PhotoAnalysis         │
│ + generateIceBreaker(user1, user2): String   │
│ + generateChatSuggestion(context): List<String> │
│ + analyzePersonality(answers): PersonalityReport │
│ + analyzeSentiment(messages): SentimentReport│
│ + detectRiskContent(content): RiskAssessment │
│ + verifyIdentity(idCard, face): VerifyResult │
└──────────────────────────────────────────────┘
```

### 3.3 AuthService (认证服务)

```
┌──────────────────────────────────────────────┐
│                 AuthService                   │
├──────────────────────────────────────────────┤
│ - userRepo: UserRepository                   │
│ - jwtUtil: JwtUtil                           │
│ - smsService: SmsService                     │
│ - passwordEncoder: BCryptPasswordEncoder     │
├──────────────────────────────────────────────┤
│ + register(RegisterRequest): User            │
│ + login(LoginRequest): LoginResponse(JWT)    │
│ + sendSmsCode(phone): void                   │
│ + verifySmsCode(phone, code): boolean        │
│ + refreshToken(token): String                │
│ + thirdPartyLogin(openId, type): LoginResponse│
└──────────────────────────────────────────────┘
```

### 3.4 ChatService (聊天服务)

```
┌──────────────────────────────────────────────┐
│                 ChatService                   │
├──────────────────────────────────────────────┤
│ - sessionRepo: ChatSessionRepository          │
│ - messageRepo: MessageRepository             │
│ - wsSessionManager: WebSocketSessionManager  │
│ - aiEngineService: AIEngineService           │
├──────────────────────────────────────────────┤
│ + sendMessage(sessionId, content): Message   │
│ + getMessages(sessionId, page): Page<Message>│
│ + recallMessage(messageId): void             │
│ + markAsRead(sessionId, userId): void        │
│ + getAICoachSuggestions(sessionId): List     │
│ + createSession(matchId): ChatSession        │
└──────────────────────────────────────────────┘
```

---

## 4. 实体关系图 (ER / 简化类关系)

```
┌────────┐ 1    1 ┌──────────┐ 1    1 ┌──────────────┐
│  User  │────────│ Profile  │────────│PersonalityTest│
└───┬────┘        └────┬─────┘        └──────────────┘
    │ 1                │ 1
    │ *                │ *
    ├──────────────────┼──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼
┌───────┐ 1    * ┌──────────┐ 1    1 ┌──────────┐
│ Photo │        │  Match   │────────│ChatSession│
└───────┘        └────┬─────┘        └────┬─────┘
                      │                   │ 1
                      │                   │ *
                      ▼                   ▼
              ┌──────────────┐    ┌────────────┐
              │MatchPreference│    │  Message   │
              └──────────────┘    └────────────┘

┌────────┐ 1    * ┌──────────┐
│  User  │────────│ VipOrder │
└────────┘        └──────────┘

┌────────┐       ┌──────────┐
│  User  │───────│ AuditLog │ (审核对象)
└────────┘       └──────────┘
```

---

## 5. 枚举类型定义

```java
public enum UserStatus     { ACTIVE, BANNED, DELETED }
public enum VipLevel       { NONE, MONTH, QUARTER, YEAR }
public enum Gender         { MALE, FEMALE }
public enum Education      { HIGH_SCHOOL, COLLEGE, BACHELOR, MASTER, PHD }
public enum IncomeRange    { BELOW_10W, 10_20W, 20_30W, 30_50W, ABOVE_50W }
public enum MarriageStatus { SINGLE, DIVORCED, WIDOWED }
public enum PrivacyLevel   { PUBLIC, MATCHED_ONLY, LIKED_ONLY }
public enum MatchAction    { LIKE, SUPER_LIKE, SKIP }
public enum MsgType        { TEXT, IMAGE, VOICE, EMOJI, SYSTEM }
public enum MsgStatus      { SENT, DELIVERED, READ }
public enum AuditStatus    { PENDING, AI_PASSED, AI_REJECTED, MANUAL_PASSED, MANUAL_REJECTED }
public enum RiskLevel      { LOW, MEDIUM, HIGH }
public enum OrderStatus    { PENDING, PAID, REFUNDING, REFUNDED }
public enum PayMethod      { WECHAT, ALIPAY }
```

---

> 本文档描述了系统的核心类结构。具体实现将遵循Spring Boot + JPA/MyBatis + Redis + WebSocket技术栈。
