#!/usr/bin/env python3
"""Claude.ai に貼る本文だけを prompts/paste/ へ切り出す。

指示欄もタスク文も、元ファイルには「どこに貼るか」の説明が前後に付いている。
スマホや別端末から貼るときに、その説明を目で除きながら選択するのは事故のもと。
raw URL を開いて全選択すればそのまま貼れる形を用意する。

prompts/ を編集したら、このスクリプトを実行して一緒にコミットすること。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTE = os.path.join(ROOT, "prompts", "paste")

HEADER = "# このファイルは自動生成です（scripts/build_paste.py）。全選択してそのまま貼ってください。\n\n"


def write(name, body):
    os.makedirs(PASTE, exist_ok=True)
    path = os.path.join(PASTE, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body.strip() + "\n")
    print(f"{os.path.relpath(path, ROOT)}  {len(body):,} bytes")


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def main():
    # 指示欄: 最初の単独 `---` から下がすべて貼付対象
    src = read("prompts/project-instructions.md")
    lines = src.splitlines()
    try:
        cut = next(i for i, l in enumerate(lines) if l.strip() == "---")
    except StopIteration:
        sys.exit("project-instructions.md に区切りの --- が見つからない")
    write("project-instructions.txt", "\n".join(lines[cut + 1:]))

    # 定期タスク: ```text ... ``` のコードブロックが上から順にタスク1・タスク2
    blocks = re.findall(r"^```text\n(.*?)^```", read("prompts/claude-tasks.md"),
                        re.S | re.M)
    if len(blocks) != 2:
        sys.exit(f"claude-tasks.md のコードブロックが2つでない（{len(blocks)}個）")
    write("task-1-daily.txt", blocks[0])
    write("task-2-weekly.txt", blocks[1])


if __name__ == "__main__":
    main()
