"""
hida_l5_relative.py
主導層の決め方を差し替える実験用のL5（本体 hida_unified_v2.py は変更しない）。

v2.1 の決め方:
  各層の活動量（層ごとに別の定数で割った値）をそのまま比べ、
  0.30 以上でいちばん大きい層を主導とする。
  → 層ごとの目盛りの違いで主導が決まってしまう
    （L1 は届かず、地図なしでは L4 が常に主導）。

このファイルの決め方（盛り上がりで比べる）:
  1. 各層の活動量を、その層自身がこれまでに出した最大値で割って 0〜1 に揃える。
     最大値はゆっくり下がる（PEAK_DECAY）。最初の値は初期DNA（PEAK_INIT）。
  2. 揃えた値から、その層の直近の平均（BASE_ALPHA の移動平均）を引く。
     これが「いつもの水準からの盛り上がり」。
  3. 盛り上がりが PROMINENCE_THRESHOLD 以上でいちばん大きい層を主導とする。
     主導強度は、その盛り上がりの大きさ。
  ずっと高いだけの層は平均も高くなるので、主導にならない。

L1 は主導の候補に入れない（2026-11-25 決定）:
  L1 は身体の信号を L2 に渡す側で、主導するのは L2 以降。
  指を切ったとき、切れたという信号を出すのが L1、痛みとして主導するのが L2。
  L1 は追随層としては残る（引き込みゲインを受け、追随整合性にも数える）。

使い方:
  agent = h.HIDA(...)
  agent.l5 = L5Relative()
"""
import hida_unified_v2 as h


class L5Relative(h.L5Consciousness):
    # 初期DNA（実験用の仮の値）
    PEAK_INIT = {'L1': 0.05, 'L2': 0.30, 'L3': 0.30, 'L4': 0.30}
    PEAK_DECAY = 0.995            # 最大値が1ステップごとに下がる割合
    BASE_ALPHA = 0.2              # 「いつもの水準」の移動平均の係数
    PROMINENCE_THRESHOLD = 0.30   # 盛り上がりの主導判定の閾値
    LEADER_CANDIDATES = ('L2', 'L3', 'L4')   # L1 は主導しない

    # 同期ON/OFFの閾値（2026-11-25 仮決め）
    # 揃えた活動量は v2.1 より値が大きく出るので、0.08/0.05 のままだと
    # ほぼ常時ONになる。v2.1 のときと同じ基準（地図あり・物ありのシナリオで、
    # 引き込みON時の同期ON頻度を前の版と同程度 = 約15% に保つ）で決め直した。
    # OFF は v2.1 と同じ比率（ON の 0.625 倍）。
    ON_THRESHOLD = 0.30
    OFF_THRESHOLD = 0.19

    def __init__(self, threshold=None):
        super().__init__(threshold)
        self._peak = dict(self.PEAK_INIT)
        self._base = {k: 0.0 for k in self.PEAK_INIT}
        self.last_prominence = {k: 0.0 for k in self.PEAK_INIT}
        self.last_raw = {}
        self._first = True

    def _measure_activity(self, l1, l2, l3, l4):
        if self._first:
            # v2.1 では「前ステップのエネルギー」が 1.0 固定で始まるため、
            # 低エネルギー開始の1歩目に L1 が大きく変化したように見える。
            # 開始時点の実際の値に合わせる。
            self._prev['l1_energy'] = l1.energy
            self._prev['l1_fatigue'] = l1.fatigue
            self._first = False
        raw = super()._measure_activity(l1, l2, l3, l4)
        self.last_raw = dict(raw)
        norm = {}
        for k, v in raw.items():
            self._peak[k] = max(self._peak[k] * self.PEAK_DECAY, v, self.PEAK_INIT[k])
            norm[k] = v / self._peak[k]
        return norm

    def _detect_leader(self, activities):
        prom = {k: activities[k] - self._base[k] for k in activities}
        self.last_prominence = dict(prom)
        for k, v in activities.items():
            self._base[k] = (1 - self.BASE_ALPHA) * self._base[k] + self.BASE_ALPHA * v
        cands = {k: v for k, v in prom.items()
                 if k in self.LEADER_CANDIDATES and v >= self.PROMINENCE_THRESHOLD}
        if not cands:
            return None, 0.0
        leader = max(cands, key=cands.get)
        return leader, self._clip01(cands[leader])


class L5RelativeOn(L5Relative):
    """同期ONのあいだ、全体として同期しやすくする版（2026-11-25 試作）

    考え方:
      同期ONのときは、その事象について意識的になっている。
      一度ONになると、事象が続いているあいだは全体として同期しやすい。
      主導層が続きやすくなるのではない。主導層は入れ替わってよい。

    実装（同期ONのあいだだけ）:
      1. 引き込みを強める（ENTRAIN_K を ON_K_MULT 倍）。
         主導がどの層でも、追随層の応答が大きくなる。
      2. 主導になる敷居を下げる（ON_PROMINENCE_THRESHOLD）。
         次の層が主導を引き継ぎやすくなる。
    何も起きなくなれば活動量が下がり、同期は自然に切れる。

    L5Relative との違いはこの2点だけ。値は仮のもの。
    """
    ON_K_MULT = 2.0
    ON_PROMINENCE_THRESHOLD = 0.20

    def _detect_leader(self, activities):
        normal = self.PROMINENCE_THRESHOLD
        if self.is_conscious:          # 前ステップの判定結果
            self.PROMINENCE_THRESHOLD = self.ON_PROMINENCE_THRESHOLD
        try:
            return super()._detect_leader(activities)
        finally:
            self.PROMINENCE_THRESHOLD = normal

    def check_sync(self, l1, l2, l3, l4):
        result = super().check_sync(l1, l2, l3, l4)
        if self.is_conscious and self.sync_type is not None:
            boost = 1.0 + self.ENTRAIN_K * self.ON_K_MULT * self.leader_strength
            for k in self.entrain_gain:
                if k != self.sync_type:
                    self.entrain_gain[k] = boost
        return result
