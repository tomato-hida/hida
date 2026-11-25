"""
measure_v22.py
シャッフル対照と主導交代の比較（v2.2 の本体で実行する版）

測定1: シャッフル対照
  §4.3.12 の時間遅れ相関 r(主導強度t, 追随平均t+1) が両条件で負だった。
  これが「引き込みへの反証」なのか「指標の作りから出る偏り」なのかを切り分ける。
  方法: 同じシードの中で、主導イベント t に対応させる「次のステップ」を
        別の主導イベントの次のステップと入れ替える（時間の対応だけを壊す）。
        主導層の種類・主導強度・活動量の分布はそのまま残る。
        これを N_PERM 回くり返し、時間の対応が無いときの値（本当のゼロ点）を出す。

測定2: 主導交代の比較
  引き込みゲインが直接かからない量（主導層の交代・行動）に
  ON/OFF で差が出るかを、同じシードどうしで比べる。

実行: python3 measure_v22.py A      （地図あり・物あり。省略時も A）
      python3 measure_v22.py B      （地図なし・物なし）
      python3 measure_v22.py C      （地図なし・物あり）
      シナリオの中身は scenario_probe.py を参照。
      v2.1 の決め方での測定は hida_v2_1/measure_v22.py。
依存: Python標準ライブラリのみ（hida_unified_v2_2.py と同じフォルダで実行）
"""

import random
from collections import Counter

import test_entrainment_ablation as ab

N_SEEDS = ab.N_SEEDS
N_PERM = 2000
CONDITIONS = (("OFF", 0.0), ("ON", 0.5))
LAYERS = ("L2", "L3", "L4")


# ---------- 共通 ----------

def events_of(series):
    """主導イベントのステップ番号（次のステップが存在するものだけ）"""
    return [t for t in range(len(series) - 1) if series[t]['leader'] is not None]


def pair_y(series, t, nxt_index):
    """主導イベント t の主導層を除いた、ステップ nxt_index の追随層平均"""
    return ab.follower_mean(series[nxt_index]['activities'], series[t]['leader'])


def rise_of(series, t, nxt_index):
    cur, nxt = series[t], series[nxt_index]
    followers = [k for k in cur['activities'] if k != cur['leader']]
    return sum(max(0.0, nxt['activities'][k] - cur['activities'][k])
               for k in followers) / len(followers)


def mean(xs):
    return sum(xs) / len(xs) if xs else float('nan')


def percentile(sorted_xs, p):
    i = min(len(sorted_xs) - 1, max(0, int(round(p * (len(sorted_xs) - 1)))))
    return sorted_xs[i]


def sign_test_two_sided(wins, losses):
    """符号検定（両側、引き分けは除外）"""
    n = wins + losses
    if n == 0:
        return float('nan')
    from math import comb
    k = max(wins, losses)
    tail = sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return min(1.0, 2 * tail)


# ---------- 測定1: シャッフル対照 ----------

def observed(all_series):
    pairs, rises = [], []
    for series in all_series:
        for t in events_of(series):
            pairs.append((series[t]['strength'], pair_y(series, t, t + 1)))
            rises.append(rise_of(series, t, t + 1))
    return ab.pearson(pairs), mean(rises)


def shuffled_once(all_series, rng):
    pairs, rises = [], []
    for series in all_series:
        ev = events_of(series)
        nxt = [t + 1 for t in ev]
        rng.shuffle(nxt)
        for t, s in zip(ev, nxt):
            pairs.append((series[t]['strength'], pair_y(series, t, s)))
            rises.append(rise_of(series, t, s))
    return ab.pearson(pairs), mean(rises)


def shuffle_control(data):
    print("=" * 68)
    print("測定1: シャッフル対照（時間の対応だけを壊したときの値）")
    print(f"  シード内で入れ替え、{N_PERM} 回")
    print("=" * 68)
    rng = random.Random(12345)
    summary = {}
    for label, _ in CONDITIONS:
        obs_r, obs_rise = observed(data[label])
        null_r, null_rise = [], []
        for _ in range(N_PERM):
            r, ri = shuffled_once(data[label], rng)
            null_r.append(r)
            null_rise.append(ri)
        null_r.sort()
        null_rise.sort()
        p_r = sum(1 for x in null_r if abs(x - mean(null_r)) >= abs(obs_r - mean(null_r))) / N_PERM
        p_rise = sum(1 for x in null_rise if abs(x - mean(null_rise)) >= abs(obs_rise - mean(null_rise))) / N_PERM
        summary[label] = (obs_r, mean(null_r), obs_rise, mean(null_rise))
        print(f"\n[{label}]")
        print(f"  時間遅れ相関 r")
        print(f"    実測                 : {obs_r:+.4f}")
        print(f"    シャッフル平均（ゼロ点）: {mean(null_r):+.4f}"
              f"   95%範囲 [{percentile(null_r, 0.025):+.4f}, {percentile(null_r, 0.975):+.4f}]")
        print(f"    実測 − ゼロ点         : {obs_r - mean(null_r):+.4f}   p = {p_r:.3f}")
        print(f"  追随層の活動上昇")
        print(f"    実測                 : {obs_rise:.4f}")
        print(f"    シャッフル平均（ゼロ点）: {mean(null_rise):.4f}"
              f"   95%範囲 [{percentile(null_rise, 0.025):.4f}, {percentile(null_rise, 0.975):.4f}]")
        print(f"    実測 − ゼロ点         : {obs_rise - mean(null_rise):+.4f}   p = {p_rise:.3f}")

    print("\n[主導層の種類ごとの内訳（実測）]")
    print(f"  {'':<5}{'主導層':<6}{'件数':>5}{'主導強度の平均':>14}{'追随平均(t+1)':>14}{'層内の r':>10}")
    for label, _ in CONDITIONS:
        by = {k: [] for k in LAYERS}
        for series in data[label]:
            for t in events_of(series):
                by[series[t]['leader']].append(
                    (series[t]['strength'], pair_y(series, t, t + 1)))
        for k in LAYERS:
            ps = by[k]
            if not ps:
                continue
            r = ab.pearson(ps)
            print(f"  {label:<5}{k:<6}{len(ps):>5}{mean([p[0] for p in ps]):>14.3f}"
                  f"{mean([p[1] for p in ps]):>14.3f}{r:>10.3f}")
    return summary


# ---------- 測定2: 主導交代の比較 ----------

def switching_stats(series):
    leaders = [s['leader'] for s in series]
    named = [l for l in leaders if l is not None]
    # 主導層が別の層に替わった回数（主導なしのステップは飛ばして数える）
    switches = sum(1 for a, b in zip(named, named[1:]) if a != b)
    # 連続する2ステップで主導層が直接入れ替わった回数
    direct = sum(1 for a, b in zip(leaders, leaders[1:])
                 if a is not None and b is not None and a != b)
    return {
        'steps': len(series),
        'events': len(named),
        'switches': switches,
        'direct': direct,
        'kinds': len(set(named)),
    }


def paired(name, off, on, fmt="{:.2f}"):
    wins = sum(1 for a, b in zip(on, off) if a > b)
    losses = sum(1 for a, b in zip(on, off) if a < b)
    ties = len(on) - wins - losses
    p = sign_test_two_sided(wins, losses)
    print(f"  {name:<28} OFF {fmt.format(mean(off)):>7}  ON {fmt.format(mean(on)):>7}"
          f"   ON>OFF {wins:2d} / ON<OFF {losses:2d} / 同じ {ties:2d}   p = {p:.3f}")


def switching_comparison(data):
    print("\n" + "=" * 68)
    print("測定2: 主導交代の比較（同じシードどうし、30シード）")
    print("=" * 68)
    stats = {label: [switching_stats(s) for s in data[label]] for label, _ in CONDITIONS}
    for key, name in (('steps', '終了までのステップ数'),
                      ('events', '主導イベント数'),
                      ('switches', '主導層の交代回数'),
                      ('direct', '連続ステップでの直接交代'),
                      ('kinds', '主導した層の種類数')):
        paired(name, [s[key] for s in stats['OFF']], [s[key] for s in stats['ON']])

    print("\n  主導層の内訳（全シード合計）")
    for label, _ in CONDITIONS:
        c = Counter(s['leader'] for series in data[label] for s in series
                    if s['leader'] is not None)
        total = sum(c.values())
        parts = "  ".join(f"{k} {c.get(k, 0):3d} ({100 * c.get(k, 0) / total:4.1f}%)" for k in LAYERS)
        print(f"    {label:<4} {parts}")

    print("\n  交代の向き（主導なしを飛ばして数えた、全シード合計）")
    for label, _ in CONDITIONS:
        c = Counter()
        for series in data[label]:
            named = [s['leader'] for s in series if s['leader'] is not None]
            for a, b in zip(named, named[1:]):
                if a != b:
                    c[f"{a}→{b}"] += 1
        parts = "  ".join(f"{k} {v}" for k, v in sorted(c.items()))
        print(f"    {label:<4} {parts if parts else '(なし)'}")

    same = sum(1 for a, b in zip(data['OFF'], data['ON'])
               if [s['leader'] for s in a] == [s['leader'] for s in b])
    print(f"\n  主導層の並びが ON/OFF で完全に同じだったシード: {same} / {N_SEEDS}")


def main():
    import sys
    import scenario_probe as sp
    key = sys.argv[1] if len(sys.argv) > 1 else "A"
    name, gm, go, e, ms = {s[0][0]: s for s in sp.SCENARIOS[:3]}[key]
    print(f"シナリオ: {name}")
    data = {label: [sp.run(seed, k, gm, go, e, ms)[0] for seed in range(N_SEEDS)]
            for label, k in CONDITIONS}
    shuffle_control(data)
    switching_comparison(data)
    ab.clean_persistence()


if __name__ == "__main__":
    main()
