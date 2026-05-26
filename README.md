# 人物信息管理系统 (Pro版)

这是一个支持自然语言交互、多用户隔离的人物信息管理系统。

## 核心特性
- **自然语言控制**：无需固定命令，AI 自动识别“增、删、改、查”意图。
- **智能数据映射**：AI 自动决定 JSON 的 Key（如“鞋码”映射为 `shoe_size`）和格式转换。
- **多用户隔离**：基于 Telegram User ID 自动创建独立的数据文件，确保隐私。
- **极简创建**：只需提供名字即可创建人物。

## 运行步骤

### 1. 安装依赖
```bash
pip install fastapi uvicorn openai requests python-telegram-bot
```

### 2. 设置 OpenAI API Key
确保环境变量中已设置 `OPENAI_API_KEY`。

### 3. 启动 API 服务
```bash
python api_service.py
```

### 4. 启动 Telegram Bot
在 `telegram_bot.py` 中填入你的 Token 后运行：
```bash
python telegram_bot.py
```

## 自然语言示例
- **创建**: "帮我记录一个叫陈依凡的朋友"
- **更新**: "陈依凡的鞋码是37，她喜欢喝奶茶"
- **查询**: "陈依凡多大了？" 或 "陈依凡的所有信息"
- **删除**: "把陈依凡删了吧"
