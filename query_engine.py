import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 默认使用环境变量中的配置
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

DATA_DIR = 'user_data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_user_db_path(user_id):
    return os.path.join(DATA_DIR, f'people_{user_id}.json')

def load_user_data(user_id):
    db_path = get_user_db_path(user_id)
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        return []
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_user_data(user_id, data):
    db_path = get_user_db_path(user_id)
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def process_user_request(user_id, user_query):
    data = load_user_data(user_id)
    context = json.dumps(data, ensure_ascii=False, indent=2)
    
    system_prompt = """
你是一个高级人物信息管理系统的 AI 核心。你负责解析用户的自然语言指令，并决定如何操作底层的 JSON 数据。

### 当前用户数据：
{context}

### 你的任务：
1. **识别意图**：用户是想“查询”、“添加”、“删除”还是“修改”信息？
2. **处理逻辑**：
   - **查询**：直接给出自然语言回答。
   - **添加**：如果用户说“添加陈依凡”，你需要在数据中新增一个 {"name": "陈依凡"}。
   - **删除**：如果用户说“删掉张三”，你需要从列表中移除该对象。
   - **修改**：如果用户说“把陈依凡的鞋码改成38”，你需要找到“陈依凡”，更新或添加 "shoe_size": 38 字段。
3. **输出格式**：
   你必须返回一个 JSON 格式的对象，包含两个字段：
   - "new_data": (list) 操作后的完整数据列表。如果是纯查询，则返回原列表。
   - "reply": (string) 你对用户的自然语言回复（确认操作成功或给出查询结果）。
4. **额外信息**：
   - 今年是2026年。请根据这个时间信息合理推断用户的查询内容（例如年龄计算等）。

### 约束：
- 只要用户提到一个名字，如果不存在就创建它。
- 自动转换数值（如“38码”转为数字 38）。
- 保持 JSON 结构的整洁。
"""

    prompt = f"用户 ID: {user_id}\n用户指令: \"{user_query}\"\n\n请处理并返回 JSON。"

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt.replace("{context}", context)},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        new_data = result.get("new_data")
        reply = result.get("reply", "操作完成。")
        
        # 如果数据发生了变化，保存它
        if new_data is not None:
            save_user_data(user_id, new_data)
            
        return reply
    except Exception as e:
        return f"处理请求时出错: {str(e)}"

if __name__ == "__main__":
    # 测试代码
    test_user = "test_123"
    print(process_user_request(test_user, "添加一个叫陈依凡的人"))
    print(process_user_request(test_user, "陈依凡的鞋码是37"))
    print(process_user_request(test_user, "陈依凡喜欢什么？"))
    print(process_user_request(test_user, "删掉陈依凡"))
