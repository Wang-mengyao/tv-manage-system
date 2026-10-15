"""
电视剧收藏管理软件
==================
一个简单的控制台程序，用来记录和管理你的追剧清单。

功能：
  1. 添加电视剧
  2. 查看全部电视剧
  3. 按剧名搜索
  4. 按类型筛选
  5. 修改电视剧信息
  6. 删除电视剧记录

数据保存在同目录下的 data.json 文件中，可以用记事本打开查看。
"""

import json
import os
import unicodedata

# 数据文件路径（和本脚本放在同一个文件夹里）
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


# ---------------------------------------------------------------
# 数据读写
# ---------------------------------------------------------------

def load_data():
    """从 data.json 读取所有电视剧记录，返回一个列表。文件不存在时返回空列表。"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        print("  数据文件读取失败，将从一个空列表开始。")
        return []


def save_data(data):
    """把电视剧记录列表保存到 data.json 文件。"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------
# 显示辅助函数（用于让中文表格对齐）
# ---------------------------------------------------------------

def display_width(text):
    """计算字符串在终端里实际占用的宽度：中文等全角字符算 2 格，其余算 1 格。"""
    width = 0
    for ch in str(text):
        if unicodedata.east_asian_width(ch) in ("F", "W"):
            width += 2
        else:
            width += 1
    return width


def pad(text, width):
    """把文本补成指定显示宽度（不够的地方用空格补齐），用于表格对齐。"""
    text = str(text)
    return text + " " * (width - display_width(text))


def print_table(dramas):
    """以表格形式打印电视剧列表。"""
    if not dramas:
        print("  暂无记录")
        return

    headers = ["编号", "剧名", "类型", "集数", "年份", "评分", "是否看完"]
    rows = []
    for i, d in enumerate(dramas, start=1):
        rows.append([
            str(i),
            str(d.get("剧名", "")),
            str(d.get("类型", "")),
            str(d.get("集数", "")),
            str(d.get("年份", "")),
            str(d.get("评分", "")),
            "已看完" if d.get("已看完") else "未看完",
        ])

    # 计算每一列的最大显示宽度
    col_widths = []
    for c in range(len(headers)):
        col_widths.append(max(display_width(row[c]) for row in [headers] + rows))

    # 打印表头和分隔线
    print("  " + "  ".join(pad(headers[c], col_widths[c]) for c in range(len(headers))))
    print("  " + "-" * (sum(col_widths) + 2 * (len(headers) - 1)))

    # 打印每一行数据
    for row in rows:
        print("  " + "  ".join(pad(row[c], col_widths[c]) for c in range(len(headers))))


# ---------------------------------------------------------------
# 输入辅助函数（带校验，输错会一直提示重新输入）
# ---------------------------------------------------------------

def input_nonempty(prompt):
    """循环提示输入，直到输入非空字符串为止。"""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  输入不能为空，请重新输入。")


def input_int(prompt):
    """循环提示输入，直到输入一个正整数为止。"""
    while True:
        value = input(prompt).strip()
        if value.isdigit() and int(value) > 0:
            return int(value)
        print("  请输入一个正整数。")


def input_year(prompt):
    """循环提示输入，直到输入一个 4 位年份为止。"""
    while True:
        value = input(prompt).strip()
        if value.isdigit() and len(value) == 4:
            return int(value)
        print("  请输入 4 位数字的年份，例如 2020。")


def input_score(prompt):
    """循环提示输入，直到输入 0-10 之间的数字为止。"""
    while True:
        value = input(prompt).strip()
        try:
            score = float(value)
        except ValueError:
            print("  请输入数字，例如 8.5。")
            continue
        if 0 <= score <= 10:
            return score
        print("  评分应在 0 到 10 之间。")


def input_watched(prompt):
    """循环提示输入，y/n 表示是否看完。"""
    while True:
        value = input(prompt).strip().lower()
        if value in ("y", "yes", "是"):
            return True
        if value in ("n", "no", "否"):
            return False
        print("  请输入 y（是）或 n（否）。")


# ---------------------------------------------------------------
# 各项功能
# ---------------------------------------------------------------

def add_drama(data):
    """添加一部电视剧。"""
    print("\n  ---- 添加电视剧 ----")
    drama = {
        "剧名": input_nonempty("  剧名："),
        "类型": input_nonempty("  类型："),
        "集数": input_int("  集数："),
        "年份": input_year("  播出年份："),
        "评分": input_score("  评分（0-10）："),
        "已看完": input_watched("  是否看完（y/n）："),
    }
    data.append(drama)
    save_data(data)
    print("  已添加：《{}》".format(drama["剧名"]))


def search_by_name(data):
    """按剧名搜索（剧名中包含关键字即匹配）。"""
    print("\n  ---- 按剧名搜索 ----")
    keyword = input("  请输入剧名关键字：").strip()
    if not keyword:
        print("  关键字不能为空。")
        return
    results = [d for d in data if keyword.lower() in str(d.get("剧名", "")).lower()]
    print("  匹配到 {} 条记录：".format(len(results)))
    print_table(results)


def filter_by_genre(data):
    """按类型筛选（类型中包含关键字即匹配）。"""
    print("\n  ---- 按类型筛选 ----")
    genre = input("  请输入类型：").strip()
    if not genre:
        print("  类型不能为空。")
        return
    results = [d for d in data if genre in str(d.get("类型", ""))]
    print("  筛选到 {} 条记录：".format(len(results)))
    print_table(results)


def choose_drama(data, action):
    """打印列表，让用户输入编号选择一条记录，返回其索引；没有记录时返回 None。"""
    if not data:
        print("  暂无记录。")
        return None
    print_table(data)
    while True:
        value = input("  请输入要{}的记录编号（输入 0 取消）：".format(action)).strip()
        if value == "0":
            return None
        if value.isdigit():
            idx = int(value) - 1
            if 0 <= idx < len(data):
                return idx
        print("  编号无效，请重新输入。")


def edit_drama(data):
    """修改一部电视剧的信息（留空表示保持不变）。"""
    print("\n  ---- 修改电视剧信息 ----")
    idx = choose_drama(data, "修改")
    if idx is None:
        return
    d = data[idx]
    print("  正在修改：《{}》（留空表示保持不变）".format(d.get("剧名", "")))

    new_name = input("  新剧名 [{}]：".format(d.get("剧名", ""))).strip()
    if new_name:
        d["剧名"] = new_name

    new_genre = input("  新类型 [{}]：".format(d.get("类型", ""))).strip()
    if new_genre:
        d["类型"] = new_genre

    new_eps = input("  新集数 [{}]：".format(d.get("集数", ""))).strip()
    if new_eps:
        if new_eps.isdigit() and int(new_eps) > 0:
            d["集数"] = int(new_eps)
        else:
            print("  集数格式不正确，已跳过。")

    new_year = input("  新播出年份 [{}]：".format(d.get("年份", ""))).strip()
    if new_year:
        if new_year.isdigit() and len(new_year) == 4:
            d["年份"] = int(new_year)
        else:
            print("  年份格式不正确，已跳过。")

    new_score = input("  新评分 [{}]：".format(d.get("评分", ""))).strip()
    if new_score:
        try:
            s = float(new_score)
            if 0 <= s <= 10:
                d["评分"] = s
            else:
                print("  评分应在 0 到 10 之间，已跳过。")
        except ValueError:
            print("  评分格式不正确，已跳过。")

    new_watched = input("  是否看完（y/n）[{}]：".format("是" if d.get("已看完") else "否")).strip().lower()
    if new_watched in ("y", "yes", "是"):
        d["已看完"] = True
    elif new_watched in ("n", "no", "否"):
        d["已看完"] = False

    save_data(data)
    print("  已保存修改。")


def delete_drama(data):
    """删除一部电视剧记录（删除前会再次确认）。"""
    print("\n  ---- 删除电视剧记录 ----")
    idx = choose_drama(data, "删除")
    if idx is None:
        return
    d = data[idx]
    confirm = input("  确定要删除《{}》吗？（y/n）：".format(d.get("剧名", ""))).strip().lower()
    if confirm in ("y", "yes", "是"):
        removed = data.pop(idx)
        save_data(data)
        print("  已删除：《{}》".format(removed.get("剧名", "")))
    else:
        print("  已取消删除。")


# ---------------------------------------------------------------
# 主程序
# ---------------------------------------------------------------

MENU = """\n======== 电视剧收藏管理 ========
1. 添加电视剧
2. 查看全部电视剧
3. 按剧名搜索
4. 按类型筛选
5. 修改电视剧信息
6. 删除电视剧记录
7. 退出
==============================="""


def main():
    data = load_data()
    try:
        while True:
            print(MENU)
            choice = input("  请输入数字选择功能：").strip()
            if choice == "1":
                add_drama(data)
            elif choice == "2":
                print("\n  ---- 全部电视剧 ----")
                print_table(data)
            elif choice == "3":
                search_by_name(data)
            elif choice == "4":
                filter_by_genre(data)
            elif choice == "5":
                edit_drama(data)
            elif choice == "6":
                delete_drama(data)
            elif choice == "7":
                print("  再见！")
                break
            else:
                print("  输入有误，请输入 1-7 之间的数字。")
    except (KeyboardInterrupt, EOFError):
        print("\n  再见！")


if __name__ == "__main__":
    main()
