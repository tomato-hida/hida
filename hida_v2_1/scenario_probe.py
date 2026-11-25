"""
scenario_probe.py
4層とも主導しうるシナリオを探すための下調べ。

シナリオごとに、各層の活動量がどこまで上がるか（主導の閾値 0.30 に届くか）と、
どの層が主導したかを数える。引き込み OFF / ON の両方で回す。

  A: 地図あり・物の位置あり（test_entrainment_ablation.py と同じ）
  B: 地図なし・物の位置なし（すべて自分で見つける）
  C: 地図なし・物の位置あり
  *_lowE: 上と同じで、エネルギー 0.3 から開始

実行: python3 scenario_probe.py            （v2.1 の決め方）
      python3 scenario_probe.py relative   （盛り上がりで比べる決め方）
"""
import io, contextlib, random
from collections import Counter

import hida_unified_v2 as h
import test_entrainment_ablation as ab

N_SEEDS = 30
LAYERS = ("L1", "L2", "L3", "L4")
SCENARIOS = (
    # 名前, 地図を与える, 物の位置を与える, 初期エネルギー, 最大ステップ
    ("A 地図あり・物あり",        True,  True,  1.0, 40),
    ("B 地図なし・物なし",        False, False, 1.0, 150),
    ("C 地図なし・物あり",        False, True,  1.0, 40),
    ("A_lowE",                   True,  True,  0.3, 40),
    ("B_lowE",                   False, False, 0.3, 150),
    ("C_lowE",                   False, True,  0.3, 40),
)


def run(seed, k, give_map, give_objects, energy, max_steps, l5_class=None):
    ab.clean_persistence()
    random.seed(seed)
    with contextlib.redirect_stdout(io.StringIO()):
        world = h.create_test_world()
        agent = h.HIDA(color_preference={'red': 1.0, 'blue': 0.3, 'green': 0.3})
    agent.l1.position = [3, 6]
    agent.l1.direction = 'N'
    agent.l1.energy = energy
    if l5_class is not None:
        agent.l5 = l5_class()   # 主導層の決め方を差し替える
    agent.l5.ENTRAIN_K = k
    if give_objects:
        agent.l4.found_objects[(6, 3)] = {'name': 'ball', 'color': 'red'}
        agent.l4.found_objects[(2, 4)] = {'name': 'ball', 'color': 'blue'}
        agent.l4.found_objects[(2, 7)] = {'name': 'ball', 'color': 'green'}
        agent.l4.found_objects[(4, 6)] = {'name': 'ball', 'color': 'yellow', 'rotten': True}
        agent.l4.found_objects[(7, 7)] = {'name': 'goal', 'color': None}
    if give_map:
        for x in range(1, 9):
            for y in range(1, 9):
                agent.l4.internal_map[(x, y)] = \
                    'danger' if world.get_cell(x, y) == 'danger' else 'empty'
    series, actions, end = [], [], 'timeout'
    with contextlib.redirect_stdout(io.StringIO()):
        for _ in range(max_steps):
            r = agent.step(world, verbose=False)
            series.append({'leader': agent.l5.sync_type,
                           'strength': agent.l5.leader_strength,
                           'activities': dict(agent.l5.last_activities),
                           'on': agent.l5.is_conscious})
            actions.append((r['action'], tuple(r['position'])))
            if r['goal_reached']:
                end = 'goal'; break
            if agent.l1.energy <= 0:
                end = 'energy0'; break
    return series, actions, end


def main(l5_class=None):
    for name, gm, go, e, ms in SCENARIOS:
        print("=" * 72)
        print(f"{name}   (初期エネルギー {e}, 最大 {ms} ステップ, {N_SEEDS} シード)")
        runs = {}
        for label, k in (("OFF", 0.0), ("ON", 0.5)):
            runs[label] = [run(s, k, gm, go, e, ms, l5_class) for s in range(N_SEEDS)]
            allsteps = [st for series, _, _ in runs[label] for st in series]
            ends = Counter(end for _, _, end in runs[label])
            lead = Counter(st['leader'] for st in allsteps if st['leader'])
            tot = sum(lead.values()) or 1
            print(f"  [{label}] 総ステップ {len(allsteps)}  終了: " +
                  " ".join(f"{k_}={v}" for k_, v in sorted(ends.items())) +
                  f"  同期ON率 {100*sum(st['on'] for st in allsteps)/len(allsteps):.0f}%")
            print("       活動量の最大値   " +
                  "  ".join(f"{L} {max(st['activities'][L] for st in allsteps):.2f}" for L in LAYERS))
            print("       0.30 以上の回数  " +
                  "  ".join(f"{L} {sum(st['activities'][L] >= 0.3 for st in allsteps):4d}" for L in LAYERS))
            print("       主導した回数     " +
                  "  ".join(f"{L} {lead.get(L,0):4d}" for L in LAYERS) +
                  f"   (主導ありのステップ {100*tot/len(allsteps):.0f}%)")
            sw = []
            for series, _, _ in runs[label]:
                named = [st['leader'] for st in series if st['leader']]
                sw.append(sum(a != b for a, b in zip(named, named[1:])))
            print(f"       交代回数（1シード平均） {sum(sw)/len(sw):.2f}")
        same = sum(a[1] == b[1] for a, b in zip(runs['OFF'], runs['ON']))
        print(f"  行動と位置の並びが ON/OFF で同じ: {same} / {N_SEEDS}")
    ab.clean_persistence()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "relative":
        from hida_l5_relative import L5Relative
        print("主導層の決め方: 盛り上がりで比べる（hida_l5_relative.py）")
        main(L5Relative)
    else:
        print("主導層の決め方: v2.1 のまま")
        main()
