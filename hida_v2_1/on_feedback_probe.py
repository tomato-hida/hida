"""
on_feedback_probe.py
同期ONのあいだ全体として同期しやすくする版（L5RelativeOn）を、
足す前（L5Relative）と比べる。引き込みは両方とも ENTRAIN_K = 0.5。

見るもの:
  同期ONの頻度、ONが続く長さ、ONのあいだの主導層の交代、行動とゴール到達。

実行: python3 on_feedback_probe.py
"""
import scenario_probe as sp
import test_entrainment_ablation as ab
from hida_l5_relative import L5Relative, L5RelativeOn

N = 30
LAYERS = ("L2", "L3", "L4")


def episodes(series):
    """同期ONが続いた区間ごとに (長さ, 区間内の主導層の交代回数, 区間内で主導した層の種類数)"""
    out, cur = [], None
    for st in series:
        if st['on']:
            if cur is None:
                cur = []
            cur.append(st['leader'])
        elif cur is not None:
            out.append(cur); cur = None
    if cur is not None:
        out.append(cur)
    res = []
    for ep in out:
        named = [l for l in ep if l]
        res.append((len(ep), sum(a != b for a, b in zip(named, named[1:])), len(set(named))))
    return res


def summarize(runs):
    steps = [st for s, _, _ in runs for st in s]
    eps = [e for s, _, _ in runs for e in episodes(s)]
    lead = {L: sum(st['leader'] == L for st in steps) for L in LAYERS}
    sw = []
    for s, _, _ in runs:
        named = [st['leader'] for st in s if st['leader']]
        sw.append(sum(a != b for a, b in zip(named, named[1:])))
    return {
        'steps': len(steps),
        'on': 100 * sum(st['on'] for st in steps) / len(steps),
        'n_ep': len(eps),
        'len': sum(e[0] for e in eps) / len(eps) if eps else 0.0,
        'maxlen': max((e[0] for e in eps), default=0),
        'multi': sum(e[2] >= 2 for e in eps),
        'lead': lead,
        'sw': sum(sw) / len(sw),
        'goal': sum(end == 'goal' for _, _, end in runs),
    }


def main():
    for name, gm, go, e, ms in sp.SCENARIOS:
        print("=" * 76)
        print(f"{name}   (初期エネルギー {e}, 最大 {ms} ステップ, {N} シード, ENTRAIN_K=0.5)")
        runs = {}
        for label, cls in (("足す前", L5Relative), ("足した後", L5RelativeOn)):
            runs[label] = [sp.run(s, 0.5, gm, go, e, ms, cls) for s in range(N)]
            r = summarize(runs[label])
            print(f"  [{label}] 同期ON {r['on']:.0f}%  ONの区間 {r['n_ep']}個  "
                  f"平均 {r['len']:.1f}ステップ  最長 {r['maxlen']}  "
                  f"区間内で2層以上が主導 {r['multi']}個")
            print("         主導した回数 " + "  ".join(f"{L} {r['lead'][L]:3d}" for L in LAYERS) +
                  f"   交代(1シード平均) {r['sw']:.2f}   ゴール {r['goal']}/{N}   総ステップ {r['steps']}")
        same = sum(a[1] == b[1] for a, b in zip(runs["足す前"], runs["足した後"]))
        print(f"  行動と位置の並びが同じ: {same} / {N}")
    ab.clean_persistence()


if __name__ == "__main__":
    main()
