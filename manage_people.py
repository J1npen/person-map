import json
import os

DB_FILE = 'people.json'

def load_data():
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        return []
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_person():
    print("\n--- 添加人物信息 ---")
    name = input("姓名: ").strip()
    if not name:
        print("姓名不能为空！")
        return
    
    age = input("年龄: ").strip()
    gender = input("性别: ").strip()
    shoe_size = input("鞋码: ").strip()
    gifts = input("可以送的礼物 (多个请用逗号分隔): ").strip()
    other = input("其他备注: ").strip()

    person = {
        "name": name,
        "age": int(age) if age.isdigit() else age,
        "gender": gender,
        "shoe_size": float(shoe_size) if shoe_size.replace('.', '', 1).isdigit() else shoe_size,
        "gifts": [g.strip() for g in gifts.split(',')] if gifts else [],
        "other": other
    }
    
    # 允许添加自定义字段
    while True:
        extra_key = input("是否添加额外字段？(输入字段名，直接回车结束): ").strip()
        if not extra_key:
            break
        extra_val = input(f"请输入 {extra_key} 的值: ").strip()
        person[extra_key] = extra_val

    data = load_data()
    data.append(person)
    save_data(data)
    print(f"成功添加: {name}")

def list_people():
    data = load_data()
    if not data:
        print("目前没有任何记录。")
        return
    print("\n--- 人物列表 ---")
    for idx, p in enumerate(data):
        print(f"{idx + 1}. {p.get('name')} (性别: {p.get('gender')}, 年龄: {p.get('age')})")

def main():
    while True:
        print("\n=== 人物信息管理系统 ===")
        print("1. 添加人物")
        print("2. 查看列表")
        print("3. 退出")
        choice = input("请选择 (1-3): ").strip()
        
        if choice == '1':
            add_person()
        elif choice == '2':
            list_people()
        elif choice == '3':
            break
        else:
            print("无效选择。")

if __name__ == "__main__":
    main()
