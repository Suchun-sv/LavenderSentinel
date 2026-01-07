# LavenderSentinel Frontend

Streamlit 前端应用，提供论文浏览、搜索和 AI 对话界面。

## 📁 目录结构

```
frontend/
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 镜像配置
├── README.md               # 本文件
│
├── .streamlit/
│   └── config.toml         # Streamlit 配置 (主题、服务器)
│
├── app.py                  # 主入口，侧边栏导航
├── api_client.py           # 后端 API 客户端封装
│
├── components/             # 可复用 UI 组件
│   ├── __init__.py         # 组件导出
│   ├── paper_card.py       # 论文卡片组件
│   ├── search_bar.py       # 搜索栏组件
│   └── chat_message.py     # 对话消息组件
│
└── pages/                  # Streamlit 多页面
    ├── 1_🏠_Home.py        # 首页
    ├── 2_🔍_Search.py      # 搜索页
    ├── 3_📚_Papers.py      # 论文列表页
    └── 4_💬_Chat.py        # AI 对话页
```

## 📄 文件说明

### 根目录

| 文件 | 说明 |
|------|------|
| `requirements.txt` | Python 依赖列表 |
| `Dockerfile` | Docker 镜像构建配置 |
| `app.py` | **主入口**，配置页面设置和侧边栏导航 |
| `api_client.py` | **API 客户端**，封装所有后端 HTTP 调用 |

### .streamlit/ 目录

| 文件 | 说明 |
|------|------|
| `config.toml` | Streamlit 配置: 主题颜色、服务器端口等 |

### components/ 目录

| 文件 | 说明 |
|------|------|
| `paper_card.py` | **论文卡片**: 显示标题、作者、摘要、分类标签 |
| `search_bar.py` | **搜索栏**: 搜索输入框 + 过滤选项 |
| `chat_message.py` | **消息气泡**: 用户/AI 消息样式、来源引用 |

### pages/ 目录

Streamlit 会自动读取此目录，生成多页面导航。文件名格式: `序号_emoji_名称.py`

| 文件 | 说明 |
|------|------|
| `1_🏠_Home.py` | **首页**: 欢迎信息、统计数据、最近论文 |
| `2_🔍_Search.py` | **搜索页**: 语义搜索、过滤、结果展示 |
| `3_📚_Papers.py` | **论文列表**: 浏览、管理、查看详情/摘要 |
| `4_💬_Chat.py` | **对话页**: AI 聊天、论文上下文、来源引用 |

## 🚀 快速开始

```bash
# 安装依赖
cd frontend
pip install -r requirements.txt

# 运行 (确保后端已启动)
streamlit run app.py
```

打开 http://localhost:8501

## 🎨 页面功能

### 🏠 首页 (Home)
- 系统介绍和欢迎信息
- 论文数量、摘要数量等统计
- 最近添加的论文预览
- 快捷跳转按钮

### 🔍 搜索页 (Search)
- 自然语言搜索框
- 过滤选项 (来源、数量)
- 搜索结果 + 相似度分数
- 点击添加到对话上下文

### 📚 论文列表 (Papers)
- 分页浏览所有论文
- 查看论文详情和摘要
- 查找相似论文
- 生成 AI 摘要
- 添加到对话上下文

### 💬 对话页 (Chat)
- 与 AI 讨论论文内容
- 选择论文作为上下文 (RAG)
- 显示来源引用
- 推荐后续问题

## 🔧 配置

编辑 `.streamlit/config.toml` 自定义:
- 主题颜色
- 服务器端口
- 其他 Streamlit 设置

