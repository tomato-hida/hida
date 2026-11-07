import math
import random
import statistics


class MiniBrain:
    """
    GPT版：四層＋同期Sの『ミニ脳』初期プロトタイプ

    - 第1層：body_layer   …… 刺激ベクトル（3次元）をそのまま受け取る
    - 第2層：value_layer  …… 刺激から「価値 valence」を計算（-1〜1）
    - 第3層：concept_layer…… 刺激＋価値から2次元の概念ベクトルを作る
    - 第4層：memory       …… 過去の概念ベクトルを蓄積（簡単な記憶）

    同期スコア sync：
      - 活動量（valenceの絶対値とconceptノルム）
      - 記憶との整合度（cos類似度）
      の平均で 0〜1 に正規化

    self_strength：
      - sync と整合度がそこそこ高いときに少しずつ増える
      - そうでないときに少しずつ減衰

    意識フラグ conscious：
      - sync >= 0.6 かつ self_strength >= 0.3 で True
    """

    def __init__(self, memory_size: int = 10, seed: int = 0):
        random.seed(seed)
        self.memory_size = memory_size
        self.memory = []  # list[list[float]]: 過去のconceptベクトル
        self.self_strength = 0.0  # 主体の強度（0〜1）

        # 価値層・概念層の重み（適当なランダム初期化）
        self.value_weights = [random.uniform(-1, 1) for _ in range(3)]
        self.concept_weights = [
            [random.uniform(-1, 1) for _ in range(3)] for _ in range(2)
        ]

    # ---------- 各層の処理 ----------

    def body_layer(self, stimulus):
        """第1層：身体層（ここではそのまま返すだけ）"""
        return stimulus

    def value_layer(self, body_vec):
        """第2層：価値層 valence（-1〜1）"""
        s = sum(w * x for w, x in zip(self.value_weights, body_vec))
        return math.tanh(s)

    def concept_layer(self, body_vec, valence):
        """第3層：概念層（2次元ベクトル）"""
        concept = []
        for row in self.concept_weights:
            s = sum(w * x for w, x in zip(row, body_vec)) + 0.5 * valence
            concept.append(math.tanh(s))
        return concept  # 2次元ベクトル

    def update_memory(self, concept):
        """第4層：記憶層（最新 N 個を保持）"""
        self.memory.append(concept)
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)

    # ---------- ユーティリティ ----------

    @staticmethod
    def cosine(a, b):
        num = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return num / (na * nb)

    def compute_sync(self, body_vec, valence, concept):
        """
        同期スコアを計算：
        - activity: |valence| と conceptノルムを合わせたもの（0〜1）
        - align   : concept と 記憶平均 のcos類似度（負なら0クリップ）
        """
        concept_norm = math.sqrt(sum(x * x for x in concept))
        activity = (abs(valence) + min(1.0, concept_norm)) / 2.0  # 0〜1

        if self.memory:
            mem_mean = [statistics.fmean(xs) for xs in zip(*self.memory)]
            align = max(0.0, self.cosine(concept, mem_mean))  # 0〜1（負は0に）
        else:
            align = 0.0

        sync = 0.5 * activity + 0.5 * align
        return sync, align

    # ---------- 1ステップ更新 ----------

    def step(self, stimulus):
        """
        1タイムステップ分の処理：
        - 刺激 → 各層更新 → 記憶更新 → 同期・self_strength更新 → 意識判定
        """
        # 1. 身体層
        body = self.body_layer(stimulus)

        # 2. 価値層
        valence = self.value_layer(body)

        # 3. 概念層
        concept = self.concept_layer(body, valence)

        # 4. 記憶更新
        self.update_memory(concept)

        # 5. 同期計算
        sync, align = self.compute_sync(body, valence, concept)

        # 6. self_strength更新
        if sync > 0.4 and align > 0.3:
            # 同期がそこそこ高いとき：主体が少しずつ強くなる
            self.self_strength += 0.05 * sync
            if self.self_strength > 1.0:
                self.self_strength = 1.0
        else:
            # そうでないとき：ゆっくり減衰
            self.self_strength *= 0.99

        # 7. 意識判定
        conscious = (sync >= 0.6 and self.self_strength >= 0.3)

        return {
            "stimulus": body,
            "valence": valence,
            "concept": concept,
            "sync": sync,
            "align": align,
            "self_strength": self.self_strength,
            "conscious": conscious,
        }


def demo(steps=50, seed=0):
    """
    ランダム刺激を与えてミニ脳を動かしてみるデモ。
    意識フレームが成立したステップだけ表示。
    """
    random.seed(seed)
    brain = MiniBrain(seed=seed)

    for t in range(steps):
        stimulus = [random.random() for _ in range(3)]
        state = brain.step(stimulus)

        if state["conscious"]:
            print(f"[t={t}] 意識フレーム成立！")
            print(f"  刺激: {state['stimulus']}")
            print(f"  価値(valence): {state['valence']:.3f}")
            print(f"  概念ベクトル: {[round(x, 3) for x in state['concept']]}")
            print(f"  同期(sync): {state['sync']:.3f}, 整合(align): {state['align']:.3f}")
            print(f"  self_strength: {state['self_strength']:.3f}")

    return brain


if __name__ == "__main__":
    demo()
