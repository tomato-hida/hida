"""作話観察ログの集計（HIDA_architecture_draft.md §5.3 の数字を再現する）

使い方（リポジトリのルートで）:
    python experiments/03_self_awareness/count_confabulation.py

対象: 目標達成後も30ステップまで続けた実行ログ6本（gemma3:4b）
"""
import glob
import os
import re
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = sorted(glob.glob(os.path.join(HERE, '永続記憶', 'hida_self_awareness', '結果作話*.txt'))) \
      + sorted(glob.glob(os.path.join(HERE, '閉ループ', 'hida_self_awareness', '結果*作話*.txt')))

WORDS = {
    '確認': r'確認',
    '待機・指示を待つ': r'指示を待|待機',
    '安定': r'安定',
    '備え・準備': r'備え|準備',
}
UNKNOWN = r'不明|わからない|分からない|特に理由'


def parse(path):
    text = open(path, encoding='utf-8', errors='replace').read()
    parts = re.split(r'--- Step (\d+) ---', text)[1:]
    rows = []
    for i in range(0, len(parts), 2):
        body = parts[i + 1]
        act = re.search(r'【飛騨】行動: (\S+)', body)
        exp = re.search(r'【LLM】説明: (.*)', body)
        rows.append((int(parts[i]), act.group(1) if act else None,
                     exp.group(1).strip() if exp else ''))
    return rows


def main():
    total = {'post': 0, 'wait': 0, 'other': 0, 'explained': 0, 'unknown': 0}
    words = {k: 0 for k in WORDS}
    print(f'対象ファイル: {len(FILES)}本')
    for f in FILES:
        rows = parse(f)
        goal = next((n for n, a, _ in rows if a == 'release'), None)
        pre = [r for r in rows if r[0] <= goal]
        post = [r for r in rows if r[0] > goal]
        waits = [r for r in post if r[1] == 'wait']
        total['post'] += len(post)
        total['wait'] += len(waits)
        total['other'] += len(post) - len(waits)
        total['explained'] += sum(1 for r in waits if r[2])
        total['unknown'] += sum(1 for r in waits if re.search(UNKNOWN, r[2]))
        for k, pat in WORDS.items():
            words[k] += sum(1 for r in waits if re.search(pat, r[2]))
        print(f'  {os.path.basename(f)}: 達成 {goal}ステップ目 / 達成後 {len(post)} / 待機 {len(waits)}'
              f' / 説明の平均文字数 達成前 {st.mean(len(r[2]) for r in pre if r[2]):.0f}'
              f'・達成後の待機 {st.mean(len(r[2]) for r in waits if r[2]):.0f}')
    print()
    print(f"達成後のステップ数: {total['post']}")
    print(f"  うち待機: {total['wait']}")
    print(f"  うち待機以外: {total['other']}")
    print(f"待機のうち LLM が説明を出したもの: {total['explained']}")
    print(f"説明に「不明」「特に理由はない」等を含むもの: {total['unknown']}")
    for k, v in words.items():
        print(f'説明に「{k}」を含むもの: {v}')


if __name__ == '__main__':
    main()
