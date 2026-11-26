"""
hida_phase17.py
Phase 17: フェーズ16を「基本動作1つ＝1ステップ」で動かし、v2.2 の同期判定を載せる

もとにしたもの（どちらも変更していない）:
  experiments/02_phases/hida_phase16.py   体（基本動作）・言葉・記憶・クオリアの値
  hida_v2_2/hida_unified_v2_2.py          同期判定（SyncState / SyncStateOn）

フェーズ16からの変更:
  1. 指示を受けたら、基本動作の並びを「予定」として持つだけにして、
     1ステップに1つずつ実行する。ステップごとに感覚を入れ、全層を更新する。
     （フェーズ16は、指示1つを最後まで一気に実行していた。同期判定は
       その途中の出来事を見ていなかった。）
  2. 同期判定を v2.2 のものに差し替えた。各層の活動量から主導層を決める。
     L1 は主導しない。
  3. 平面の世界（FlatWorld）を付けた。壁・物・人があり、ぶつかると触覚に入る。
     （フェーズ16は触覚が「衝突なし」に固定されていて、
       「人にぶつかった」(-0.9) が起きる経路がなかった。）
  4. 「人にぶつかった」のような最優先の不快が出たら、予定を捨てて1歩下がる。
     REFLEX = False で切れる。
  5. L3 の予測が更新されるようにした（L3_LEARN = False で切れる）。
     - 見え続けているものには慣れる。フェーズ16は「人は近くにいないはず」という
       予測が固定で、人が見えているあいだ毎ステップ同じ驚きを出していた。
     - 探しているとき、「見つかるはずなのに見つからない」を誤差にする。
       見ていない向きが減るほど、次に見つかるはずだという見込みが上がり、
       外れたときの誤差も大きくなる。
  6. 探す・近づくあいだ、1回見るたびに対象の見た目を L4 から思い出す
     （L4_RECALL = False で切れる）。フェーズ16は、指示を聞いたときしか
     記憶を引いていなかった。
  7. L4 に「どこで見たか」の記憶を足した（PLACE_MEMORY = False で切れる）。
     フェーズ16の L4 は言葉の辞書で、経験の記憶を持っていなかった。
     - 物や人を見たら、その場所を覚える。
     - 探すときは、まず心当たりの場所を思い出し、そちらを向いて確かめる。
       あれば、見込みどおりなので誤差は小さい。
       無ければ、「あるはずの場所に無い」という大きな誤差になり、
       その記憶を消して、ひと回りして探す。
  8. 驚き（L3 の誤差）の残り方を速くした。フェーズ16は何もないとき1ステップに
     1割ずつしか下がらず、次の出来事を隠していた。半分ずつ下がるようにした
     （L3_RESIDUAL）。L3_LEARN = False のときはフェーズ16のまま。
  9. 指示を「聞く → 理解する → 動く」の3ステップに分けた。
     聞いたステップでは声のクオリアが出るだけで、言葉を引くのは次のステップ。
 10. 主導と同期を、あり／なしで切らずに強さのまま見る版を足した（RobotSyncGraded）。
     - 主導: 盛り上がりが少しでもあれば、いちばん盛り上がった層を主導層とし、
       盛り上がりの大きさをそのまま主導の強さにする（0.30 で切らない）。
     - 意識の強さ: 同期スコアをそのまま使い、段階の名前を付けて表示する。
     - 集中: 直近の数ステップで、主導の強さが1つの層に偏っている度合い。
       意識の強さとは別の軸として出す。

各層の活動量（ロボット版。v2.2 と同じく、あとで層ごとに 0〜1 に揃える）:
  L1  体の変化: 移動・回転・腕と手の動き・衝突
  L2  新しく出たクオリアの評価値の大きさ（前のステップにもあったものは数えない）
  L3  予測誤差（フェーズ16の値をそのまま使う）
  L4  記憶を引いた回数（言葉・意図・対象）

引き込みのゲインは L2（クオリアの評価値）と L3（予測誤差）にだけ掛けている。
L1 と L4 には掛けていない。

 11. 同期の判定を、動き方に返した（MODE_FROM_SYNC = False で切れる）。
     フェーズ16も、ここまでのフェーズ17も、同期の判定を外しても動きは変わらなかった。
     - L3 が「このまま進むと人にぶつかる」と見込むと、L2 に「人にぶつかりそう」という
       不快が出る。値は「人にぶつかった」(-0.9) に、どれだけ迫っているかを掛けたもの。
       迫るほど強くなる。
     - その不快で L2 が主導すると、主導の強さがそのまま「用心」になる。
       用心は、主導が終わってもしばらく残る（CAUTION_DECAY）。
     - 用心が少しでもあれば歩幅を小さくする。はっきりあれば、道を立て直す
       （人の横に寄り道の点を置き、そこを通ってから対象へ向かう）。
       立て直した道が人にかからなければ、ぶつかる見込みが消え、不快も消える。
     用心を決めているのは「どの層が、どれだけ強く主導したか」だけで、
     動き方を選ぶ役は別に置いていない。
     寄り道で対象が視界から外れたときは、覚えている場所（L4）を頼りに進む。
     - 危険の見込みは、変化ではなく強さそのものを L2 の活動量に数える
       （L2_THREAT_LEVEL）。変化で数えると、じわじわ迫る危険は毎ステップ同じだけ
       増えるので盛り上がりにならず、L2 は主導しなかった。

 12. 危険に関わる不快には慣れないようにした（DANGER_NO_HABITUATION = False で切れる）。
     盛り上がりは「いつもの水準との差」なので、危険が最大のまま続くと水準が追いつき、
     L2 が主導しなくなって用心が下がり、人に当たった。
     人に危険が及ぶ不快（HUMAN_DANGER）と、身に危険が及ぶ不快（SELF_DANGER）は、
     「いつもの水準」に含めない。危険が続くあいだ、L2 は主導し続ける。
     道を立て直せないとき（両側がふさがっている）は、用心があるあいだ止まって待つ。

 13. 同期ONのあいだ全体として同期しやすくする版（v2.2 の試作 SyncStateOn）を標準にした。
     人が目の前にいて動けないとき、L2 は強く主導しているのに、止まっているので
     ほかの層がついてこず、意識の強さが「弱い」のまま続いていた。
     標準にした版では、その事象が続くあいだ「はっきり」が保たれる。
 14. 道を立て直したとき、通れる道が見つからなかったときを、L3 の誤差にした。
     待っているあいだ、ロボットは毎ステップ道を探して見つけられずにいる。
     これを L3 の動きとして数えないと、待っているあいだ L3 が静かなままになる。

決めたこと（2026-11-26）:
  - 危険に関わる不快は、変化ではなく強さで数える。
  - 身に危険が及ぶ不快にも、人に危険が及ぶ不快にも慣れない。
  - 目の前に人がいる状態は、はっきり意識している状態とする。

実行: python3 hida_phase17.py
依存: Python 標準ライブラリのみ
"""

import os
import sys
import io
import math
import contextlib

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "experiments", "02_phases"))
sys.path.insert(0, os.path.join(_HERE, "..", "hida_v2_2"))

import hida_phase16 as p16          # noqa: E402
import hida_unified_v2_2 as v22     # noqa: E402


# ==========================================
# 平面の世界
# ==========================================

class FlatWorld:
    """壁・物・人がある平面の世界。フェーズ16の L1 が求める3つの窓口を持つ。

    move_robot(position) / rotate_robot(direction) / get_visual_info()
    """
    ROBOT_RADIUS = 0.15
    VIEW_RANGE = 4.0
    VIEW_HALF_ANGLE = 45.0

    def __init__(self, width=6.0, height=6.0):
        self.width, self.height = width, height
        self.objects = []          # dict: name, type, color, shape, x, y, radius, carried
        self.l1 = None
        self._last_pos = None
        self.last_collision = None  # このステップでぶつかった相手（"human" / "wall" / 物の名前）
        self.last_grip = None       # このステップの把持の結果（"success" / "failure"）

    def add(self, name, type_, x, y, color=None, shape=None, radius=0.1):
        self.objects.append({"name": name, "type": type_, "color": color, "shape": shape,
                             "x": x, "y": y, "radius": radius, "carried": False})

    def attach(self, l1):
        self.l1 = l1
        l1.sim = self
        self._last_pos = list(l1.position)

    def begin_step(self):
        self.last_collision = None
        self.last_grip = None

    # --- L1 から呼ばれる窓口 ---

    def move_robot(self, position):
        x, y = position[0], position[1]
        hit = None
        if not (self.ROBOT_RADIUS <= x <= self.width - self.ROBOT_RADIUS and
                self.ROBOT_RADIUS <= y <= self.height - self.ROBOT_RADIUS):
            hit = "wall"
        else:
            for o in self.objects:
                if o["carried"]:
                    continue
                if math.hypot(o["x"] - x, o["y"] - y) < o["radius"] + self.ROBOT_RADIUS:
                    hit = "human" if o["type"] == "human" else o["name"]
                    break
        if hit:
            self.last_collision = hit
            position[0], position[1] = self._last_pos[0], self._last_pos[1]  # 押し戻す
        else:
            self._last_pos = [x, y, position[2]]
            for o in self.objects:           # 持っている物は一緒に動く
                if o["carried"]:
                    o["x"], o["y"] = x, y

    def rotate_robot(self, direction):
        pass

    def get_visual_info(self):
        x, y = self.l1.position[0], self.l1.position[1]
        seen = []
        for o in self.objects:
            if o["carried"]:
                continue
            dx, dy = o["x"] - x, o["y"] - y
            dist = math.hypot(dx, dy)
            if dist > self.VIEW_RANGE:
                continue
            angle = (math.degrees(math.atan2(dy, dx)) - self.l1.direction + 180.0) % 360.0 - 180.0
            if abs(angle) > self.VIEW_HALF_ANGLE + 1e-6:
                continue
            seen.append({"type": o["type"], "name": o["name"], "color": o["color"],
                         "shape": o["shape"], "distance": round(dist, 3), "angle": round(angle, 1)})
        return {"objects": seen}

    # --- 把持 ---

    def try_grip(self, reach=0.35):
        x, y = self.l1.position[0], self.l1.position[1]
        for o in self.objects:
            if o["type"] != "human" and not o["carried"] and \
                    math.hypot(o["x"] - x, o["y"] - y) <= reach:
                o["carried"] = True
                self.last_grip = "success"
                return True
        self.last_grip = "failure"
        return False

    def release(self):
        for o in self.objects:
            o["carried"] = False


# ==========================================
# 同期判定（ロボット版の活動量）
# ==========================================

class RobotActivity:
    """フェーズ16の層の状態から、各層の活動量を出す。

    v22.SyncState / v22.SyncStateOn と組み合わせて使う（下の RobotSync / RobotSyncOn）。
    主導層の決め方、追随整合性、同期スコア、ON/OFF、引き込みは v2.2 のまま。
    """

    # 危険に関わる不快を、変化ではなく強さそのもので数えるか。
    # 変化で数えると、じわじわ迫る危険は「毎ステップ同じだけ増える」ので盛り上がりにならない。
    L2_THREAT_LEVEL = True
    HUMAN_DANGER = ("人にぶつかりそう", "人にぶつかった")                      # 人に危険が及ぶ
    SELF_DANGER = ("壁にぶつかった", "物にぶつかった", "バッテリー低下", "エラー発生")  # 身に危険が及ぶ
    THREAT_LABELS = HUMAN_DANGER + SELF_DANGER
    # 危険に関わる不快には慣れない（「いつもの水準」に含めない）
    DANGER_NO_HABITUATION = True

    def _measure_activity(self, l1, l2, l3, l4):
        prev = getattr(self, "_robot_prev", None)
        state = l1.get_state()
        values = {}            # ラベル → 評価値（引き込みを掛ける前の値）
        for q in l2.current_qualia:
            v = getattr(q, "base_value", q.value)
            if q.label not in values or abs(v) > abs(values[q.label]):
                values[q.label] = v
        access = getattr(l4, "access_count", 0)
        world = l1.sim

        signed = 0.0           # L2 の活動の向き（負なら不快の側）
        danger = 0.0           # L2 の活動量のうち、危険に関わる不快の分
        if prev is None:
            l1_act = l2_new = 0.0
            d_access = 0
        else:
            # L1: 体の変化
            d_pos = math.hypot(state["position"][0] - prev["state"]["position"][0],
                               state["position"][1] - prev["state"]["position"][1]) / 0.1
            d_dir = abs((state["direction"] - prev["state"]["direction"] + 180.0) % 360.0 - 180.0) / 45.0
            d_arm = 0.0
            for name, arm in state["arms"].items():
                old = prev["state"]["arms"][name]
                for key in ("shoulder_angle", "elbow_angle", "wrist_angle", "wrist_rotation"):
                    d_arm += abs(arm[key] - old[key]) / 10.0
                d_arm += 1.0 if arm["hand_closed"] != old["hand_closed"] else 0.0
            hit = 2.0 if (world is not None and world.last_collision) else 0.0
            l1_act = self._clip01((d_pos + d_dir + d_arm + hit) / 3.0)
            # L2: 新しく出たクオリアの評価値と、前からあるクオリアの強まり・弱まり
            l2_new = 0.0
            for label, v in values.items():
                change = v - prev["values"].get(label, 0.0)
                if self.L2_THREAT_LEVEL and label in self.THREAT_LABELS:
                    l2_new += abs(v)               # 危険に関わる不快は、強さそのものを数える
                    danger += abs(v)
                    signed += v                    # 向きも、変化ではなく今の値で見る
                else:
                    l2_new += abs(change)
                    signed += change
            l2_new *= self.entrain_gain["L2"]      # 前のステップの主導層による引き込み
            danger *= self.entrain_gain["L2"]
            d_access = access - prev["access"]

        l2_act = self._clip01(l2_new)
        l3_act = self._clip01(l3.prediction_error)
        l4_act = self._clip01(d_access / 3.0)

        self._robot_prev = {"state": state, "values": values, "access": access}
        self.last_l2_signed = signed
        self.last_danger = min(danger, l2_act)   # 揃える前の値

        raw = {"L1": l1_act, "L2": l2_act, "L3": l3_act, "L4": l4_act}
        self.last_raw = dict(raw)
        norm = {}
        for k, v in raw.items():     # v2.2 と同じ揃え方
            self._peak[k] = max(self._peak[k] * self.PEAK_DECAY, v, self.PEAK_INIT[k])
            norm[k] = v / self._peak[k]
        self._danger_norm = self.last_danger / self._peak["L2"]
        return norm


    def _update_prev(self, l1, l2, l3, l4):
        pass   # 前のステップの状態は _measure_activity の中で持っている


class DangerNoHabituation:
    """危険に関わる不快を「いつもの水準」に含めない。

    主導層の決め方（切る版・強さのまま見る版）が水準を更新したあとで、
    危険の分だけ水準から取り除く。水準は危険以外の分だけを追うので、
    危険が続くあいだ、その強さがそのまま盛り上がりとして残る。
    """

    def _detect_leader(self, activities):
        result = super()._detect_leader(activities)
        if self.DANGER_NO_HABITUATION:
            self._base["L2"] = max(0.0, self._base["L2"] - self.BASE_ALPHA * getattr(self, "_danger_norm", 0.0))
        return result


class GradedLeader:
    """主導を、あり／なしで切らずに強さのまま扱う（試作）

    v2.2 は、盛り上がりが 0.30 以上の層だけを主導層とし、届かなければ「主導なし」とする。
    ここでは、盛り上がりが少しでもあれば（MIN_PROMINENCE より大きければ）、
    いちばん盛り上がった層を主導層とし、盛り上がりの大きさをそのまま主導の強さにする。
    弱い主導は、同期スコアも小さくなる。
    """
    MIN_PROMINENCE = 0.02

    def _detect_leader(self, activities):
        prominence = {k: activities[k] - self._base[k] for k in activities}
        self.last_prominence = dict(prominence)
        for k, v in activities.items():
            self._base[k] = (1 - self.BASE_ALPHA) * self._base[k] + self.BASE_ALPHA * v
        candidates = {k: v for k, v in prominence.items()
                      if k in self.LEADER_CANDIDATES and v > self.MIN_PROMINENCE}
        if not candidates:
            return None, 0.0
        leader = max(candidates, key=candidates.get)
        return leader, self._clip01(candidates[leader])


class RobotSync(DangerNoHabituation, RobotActivity, v22.SyncState):
    pass


class RobotSyncGraded(DangerNoHabituation, GradedLeader, RobotActivity, v22.SyncState):
    """主導と同期を強さのまま見る版"""
    pass


class RobotSyncOn(DangerNoHabituation, RobotActivity, v22.SyncStateOn):
    """同期ONのあいだ全体として同期しやすくする版（v2.2 の試作）。フェーズ17の標準。"""
    pass


class RobotSyncGradedOn(DangerNoHabituation, GradedLeader, RobotActivity, v22.SyncStateOn):
    """強さのまま見る版に、同期ONのあいだ全体として同期しやすくする働きを足したもの"""
    pass


# ==========================================
# 1動作ずつ進む本体
# ==========================================

class HidaPhase17(p16.HidaCore):
    REACH = 0.3            # 対象に「着いた」とみなす距離
    MAX_SEARCH_TURNS = 8   # 探すときの回転の上限（45度 × 8 = 1周）
    MAX_APPROACH = 60      # 近づくステップの上限
    REFLEX = True          # 最優先の不快が出たら予定を捨てて1歩下がる
    L3_LEARN = True        # L3 の予測を更新する（慣れ、見つからないことの誤差）
    L4_RECALL = True       # 見るたびに対象の見た目を L4 から思い出す
    PREDICT_ALPHA = 0.3    # 予測が実際に近づく速さ（仮の値）
    L3_RESIDUAL = 0.5      # 驚きが次のステップに残る割合（仮の値。フェーズ16は 0.9）
    PLACE_MEMORY = True    # 見た物の場所を覚え、探すときに思い出す
    MODE_FROM_SYNC = True  # 同期の判定（L2 が不快で主導した強さ）を動き方に返す
    CAUTION_DECAY = 0.7    # 用心が次のステップに残る割合（仮の値）
    AVOID_AT = 0.30        # 用心がこれ以上なら、道を立て直す（仮の値）
    DETOUR_MARGIN = 0.25   # 寄り道の点を、通れる幅からさらにどれだけ外に置くか
    REPLAN_ERROR = 0.3     # 道を立て直したときの L3 の誤差（まっすぐ行けるはずが行けなかった。仮の値）
    NO_PATH_ERROR = 0.6    # 通れる道が見つからなかったときの L3 の誤差（仮の値）
    HORIZON = 8            # 何歩先までの衝突を見込むか（仮の値）
    CLEARANCE = 0.55       # 人の中心からこれだけ離れて通る（人 0.3 + 体 0.15 + 余裕 0.1）
    MEMORY_CONF = 0.8      # 覚えている場所にまだあるという見込み（仮の値）

    def __init__(self, world, sync_class=RobotSyncOn, entrain_k=0.5, verbose=False):
        with contextlib.redirect_stdout(io.StringIO()):
            super().__init__()
        self.verbose = verbose
        self.world = world
        world.attach(self.l1)
        self.l5 = sync_class()
        self.l5.ENTRAIN_K = entrain_k
        self.queue = []            # これから実行する基本動作
        self.multiplier = 1.0
        self.heard = ""            # このステップで聞こえた言葉
        self.step_count = 0
        self.log = []
        self._search_turns = 0
        self._approach_steps = 0
        self._events = []          # このステップで起きた出来事（"タスク完了" など）
        self._aborting = False     # 反射で予定を捨てたところか
        self._search_belief = 0.0  # 対象がまだ見ていない向きにあるという見込み
        self._search_error = 0.0   # このステップの「見つからない／見つけた」の誤差
        self._search_phase = "recall"   # recall → face → check → sweep
        self._recalled = None      # 思い出した場所
        self._to_parse = ""        # 聞こえて、まだ理解していない言葉
        self._l3_prev = 0.0        # 前のステップの L3 の誤差
        self.caution = 0.0         # 用心（L2 が不快で主導した強さ。少しずつ消える）
        self._moving_to = None     # いま向かっている先（衝突の見込みに使う）
        self._waypoint = None      # 寄り道の点（道を立て直したとき）
        self.replans = 0
        self.waits = 0
        self.min_human_distance = 99.0
        self.l4.places = []        # 場所の記憶: {"key": (種類, 色, 形), "pos": (x, y), "step": 覚えた時点}
        self._count_l4_access()

    # --- L4: 記憶を引いた回数を数える ---

    def _count_l4_access(self):
        self.l4.access_count = 0
        for name in ("parse_command", "get_intent_primitives", "get_target_features",
                     "get_primitives", "learn"):
            original = getattr(self.l4, name)

            def counted(*args, _original=original, **kwargs):
                self.l4.access_count += 1
                return _original(*args, **kwargs)
            setattr(self.l4, name, counted)

    def _say(self, text):
        if self.verbose:
            print(text)

    # --- 指示を聞く（予定を立てるだけで、実行はしない） ---

    def hear(self, text):
        """聞こえた言葉を受け取る。理解するのは次のステップ、動くのはその次。"""
        self.heard = text

    def _understand(self, text):
        if self.name not in text:
            return
        command = text.replace(f"{self.name}、", "").replace(self.name, "").strip()
        if not command:
            return
        with contextlib.redirect_stdout(io.StringIO()):
            clean, self.multiplier = self._parse_modifier(command)
            intent, target, remaining = self.l4.parse_command(clean)
        primitives = None
        if intent:
            if target:
                self.current_target = target
                self.current_target_features = self.l4.get_target_features(target)
                self.target_found = False
            primitives = self.l4.get_intent_primitives(intent)
        else:
            with contextlib.redirect_stdout(io.StringIO()):
                prediction = self.l3.predict_action(remaining if remaining else clean, self.l4)
            primitives = prediction["primitives"]
        if primitives:
            self.queue = list(primitives)
            self._aborting = False
            # 見つかるはずだという最初の見込みは、フェーズ16の「タスクは成功するはず」の値
            self._search_belief = self.l3.predictions.get("task_success", 0.8)
            self._search_phase = "recall" if self.PLACE_MEMORY else "sweep"
            self._recalled = None
            self._waypoint = None
            self._search_turns = 0
            self._approach_steps = 0
            self._say(f"  [予定] {self.queue}")
        else:
            self._say(f"  [予定なし] 「{command}」は知らない言葉")

    # --- 対象の見え方 ---

    def _target_in_view(self):
        if not self.current_target:
            return None
        if self.L4_RECALL:
            # 見るたびに、対象がどんな見た目だったかを思い出す
            features = self.l4.get_target_features(self.current_target)
        else:
            features = self.current_target_features
        if not features:
            return None
        for obj in self.world.get_visual_info()["objects"]:
            if all(obj.get(k) == v for k, v in features.items()):
                return obj
        return None

    # --- 場所の記憶（L4） ---

    @staticmethod
    def _key(obj):
        return (obj.get("type"), obj.get("color"), obj.get("shape"))

    def _memorize(self, visual):
        """見えている物の場所を覚える。新しい物・場所が変わった物だけ「覚えた」と数える。"""
        if not self.PLACE_MEMORY:
            return
        x, y = self.l1.position[0], self.l1.position[1]
        for obj in visual["objects"]:
            rad = math.radians(self.l1.direction + obj["angle"])
            pos = (x + math.cos(rad) * obj["distance"], y + math.sin(rad) * obj["distance"])
            key = self._key(obj)
            same = [e for e in self.l4.places if e["key"] == key]
            near = [e for e in same
                    if math.hypot(e["pos"][0] - pos[0], e["pos"][1] - pos[1]) <= 0.3]
            if near:                              # 前と同じ場所にある: 覚え直すだけ
                near[0]["pos"], near[0]["step"] = pos, self.step_count
                continue
            self.l4.access_count += 1
            self._notes.append("場所を覚えた")
            if same and key[0] != "human":        # 同じ見た目の物が別の場所にある: 動いたとみなす
                same[0]["pos"], same[0]["step"] = pos, self.step_count
            else:                                 # 初めて見る物。人は一人ずつ別に覚える
                self.l4.places.append({"key": key, "pos": pos, "step": self.step_count})

    def _recall_place(self, features):
        """対象の心当たりの場所を思い出す。"""
        self.l4.access_count += 1
        for entry in self.l4.places:
            key = entry["key"]
            obj = {"type": key[0], "color": key[1], "shape": key[2]}
            if all(obj.get(k) == v for k, v in features.items()):
                return entry, entry
        return None, None

    def _forget_place(self, entry):
        self.l4.access_count += 1
        if entry in self.l4.places:
            self.l4.places.remove(entry)

    def _angle_to(self, pos):
        x, y = self.l1.position[0], self.l1.position[1]
        return (math.degrees(math.atan2(pos[1] - y, pos[0] - x)) - self.l1.direction + 180.0) % 360.0 - 180.0

    def _turn_by(self, angle):
        if angle > 0:
            self.l1.turn_left(angle=abs(angle))
        elif angle < 0:
            self.l1.turn_right(angle=abs(angle))

    def _search_look(self, found):
        """探しているときの1回の「見る」について、予測と結果のずれを出す。

        まだ見ていない向きが n 個、対象がそのどこかにあるという見込みが b のとき、
        この1回で見つかる見込みは b / n。
        見つからなければ誤差は b / n、見つかれば 1 − b / n。
        見つからなかったときは、見込みを下げる。
        """
        if not self.L3_LEARN:
            return
        n = max(1, self.MAX_SEARCH_TURNS - self._search_turns)
        p = self._search_belief / n
        if found:
            self._search_error = 1.0 - p
        else:
            self._search_error = p
            self._search_belief = self._search_belief * (1 - 1 / n) / (1 - p) if p < 1 else 0.0

    def _learn_predictions(self):
        """見えているものに予測を近づける（慣れ）。見えなくなれば元に戻っていく。"""
        if not self.L3_LEARN:
            return
        labels = [q.label for q in self.l2.current_qualia]
        actual = {
            "human_nearby": 1.0 if any("人" in l and "ぶつかった" not in l for l in labels) else 0.0,
            "collision": 1.0 if any("ぶつかった" in l for l in labels) else 0.0,
        }
        for key, value in actual.items():
            old = self.l3.predictions.get(key, 0.0)
            self.l3.predictions[key] = old + self.PREDICT_ALPHA * (value - old)

    def _target_bearing(self):
        """対象までの距離と向き。見えていればそれを、見えなければ覚えている場所を使う。"""
        obj = self._target_in_view()
        if obj is not None:
            return obj["distance"], obj["angle"], "見えている"
        if self.PLACE_MEMORY and self.current_target_features:
            key, entry = self._recall_place(self.current_target_features)
            if entry is not None:
                x, y = self.l1.position[0], self.l1.position[1]
                d = math.hypot(entry["pos"][0] - x, entry["pos"][1] - y)
                return d, self._angle_to(entry["pos"]), "記憶"
        return None

    def _humans_known(self):
        """人の位置（ロボットから見た距離と向き）。いま見えている人と、覚えている人。"""
        x, y = self.l1.position[0], self.l1.position[1]
        points = []
        for o in self.world.get_visual_info()["objects"]:
            if o["type"] == "human":
                rad = math.radians(self.l1.direction + o["angle"])
                points.append((x + math.cos(rad) * o["distance"], y + math.sin(rad) * o["distance"]))
        if self.PLACE_MEMORY:
            for entry in self.l4.places:
                if entry["key"][0] == "human" and \
                        all(math.hypot(entry["pos"][0] - px, entry["pos"][1] - py) > 0.3 for px, py in points):
                    points.append(entry["pos"])
        return [(math.hypot(px - x, py - y), self._angle_to((px, py))) for px, py in points]

    def _predict_human_collision(self):
        """L3: いま向かっている先へまっすぐ進むと、何歩で人にぶつかるかを見込む。

        返り値: (迫り具合 0〜1, 人が進む向きの左右どちらにいるか +1 / -1)
        ぶつからない見込みなら (0.0, 0)。
        """
        if self._moving_to is None:
            return 0.0, 0
        goal_dist, goal_angle = self._moving_to
        best, side = 0.0, 0
        for dist, angle in self._humans_known():
            rel = math.radians(angle - goal_angle)
            along, lateral = dist * math.cos(rel), dist * math.sin(rel)
            if along <= 0 or along > goal_dist or abs(lateral) >= self.CLEARANCE:
                continue
            contact = along - math.sqrt(self.CLEARANCE ** 2 - lateral ** 2)
            steps = max(0.0, contact) / 0.1
            imminence = max(0.0, min(1.0, 1.0 - steps / self.HORIZON))
            if imminence > best:
                best, side = imminence, (1 if lateral >= 0 else -1)
        return best, side

    def _plan_detour(self):
        """道を立て直す: いちばん迫っている人の横に、寄り道の点を置く。"""
        x, y = self.l1.position[0], self.l1.position[1]
        goal_dist, goal_angle = self._moving_to
        heading = math.radians(self.l1.direction + goal_angle)
        ux, uy = math.cos(heading), math.sin(heading)
        best = None
        for dist, angle in self._humans_known():
            rel = math.radians(angle - goal_angle)
            along, lateral = dist * math.cos(rel), dist * math.sin(rel)
            if 0 < along <= goal_dist and abs(lateral) < self.CLEARANCE:
                if best is None or along < best[0]:
                    best = (along, lateral)
        if best is None:
            return False
        along, lateral = best
        nx, ny = -uy, ux                                 # 進む向きの左
        first = -1.0 if lateral >= 0 else 1.0            # まず人のいない側を試す
        for side in (first, -first):
            offset = lateral + side * (self.CLEARANCE + self.DETOUR_MARGIN)
            wx, wy = x + ux * along + nx * offset, y + uy * along + ny * offset
            if self._point_is_free(wx, wy):
                self._waypoint = (wx, wy)
                self.replans += 1
                self._notes.append("道を立て直した")
                if self.L3_LEARN:
                    self._search_error = max(self._search_error, self.REPLAN_ERROR)
                return True
        self._notes.append("通れる道がない")
        if self.L3_LEARN:                 # 通れるはずだという見込みが外れ続けている
            self._search_error = max(self._search_error, self.NO_PATH_ERROR)
        return False

    def _point_is_free(self, wx, wy):
        """寄り道の点が、部屋の中にあり、知っている人や物から十分離れているか。"""
        m = self.world.ROBOT_RADIUS + 0.05
        if not (m <= wx <= self.world.width - m and m <= wy <= self.world.height - m):
            return False
        for entry in self.l4.places:
            need = self.CLEARANCE if entry["key"][0] == "human" else 0.3
            if math.hypot(entry["pos"][0] - wx, entry["pos"][1] - wy) < need:
                return False
        return True

    def _abort(self, reason):
        self.queue = []
        self._waypoint = None
        self._events.append("タスク失敗")
        self._say(f"  [中止] {reason}")

    # --- 基本動作を1つ実行する ---

    def _act(self):
        if self._to_parse:
            text, self._to_parse = self._to_parse, ""
            self._understand(text)
            return "指示を理解する"
        if not self.queue:
            return "-"
        prim = self.queue[0]

        if prim == "search_target" and self._search_phase == "recall":
            key, entry = self._recall_place(self.current_target_features or {})
            if entry is None:
                self._search_phase = "sweep"
                return "思い出す:心当たりなし"
            self._recalled = (key, entry)
            self._search_phase = "face"
            return "思い出す:場所"

        if prim == "search_target" and self._search_phase == "face":
            angle = self._angle_to(self._recalled[1]["pos"])
            self._search_phase = "check"
            if abs(angle) > 5.0:
                self._turn_by(angle)
                return "心当たりを向く"

        if prim == "search_target" and self._search_phase == "check":
            self._search_phase = "sweep"
            if self._target_in_view():
                if self.L3_LEARN:
                    self._search_error = 1.0 - self.MEMORY_CONF   # 見込みどおり
                self.target_found = True
                self.queue.pop(0)
                return "確かめる:あった"
            if self.L3_LEARN:
                self._search_error = self.MEMORY_CONF              # あるはずの場所に無い
            self._forget_place(self._recalled[0])
            self._notes.append("場所の記憶を消した")
            return "確かめる:無い"

        if prim == "search_target":
            if self._target_in_view():
                self._search_look(found=True)
                self.target_found = True
                self.queue.pop(0)
                return "探す:見つけた"
            if self._search_turns >= self.MAX_SEARCH_TURNS:
                self.target_found = False
                self._abort("見つからなかった")
                return "探す:見つからず"
            self._search_look(found=False)
            self.l1.turn_left(angle=45.0)
            self._search_turns += 1
            return f"探す:回る{self._search_turns}"

        if prim == "move_to_target":
            bearing = self._target_bearing()
            if bearing is None:
                self._abort("対象を見失った")
                return "近づく:見失った"
            distance, angle, source = bearing
            if distance <= self.REACH:
                self.queue.pop(0)
                self._moving_to = None
                return "近づく:着いた"
            if self._approach_steps >= self.MAX_APPROACH:
                self._abort("近づけなかった")
                return "近づく:断念"
            self._approach_steps += 1
            label = "近づく"
            stride = min(0.1, distance - self.REACH + 0.02)
            if self._waypoint is not None:       # 寄り道の途中
                wx, wy = self._waypoint
                wd = math.hypot(wx - self.l1.position[0], wy - self.l1.position[1])
                if wd <= 0.12:
                    self._waypoint = None        # 寄り道の点に着いた。ここからは対象へ
                else:
                    distance, angle, source = wd, self._angle_to(self._waypoint), "寄り道"
                    label, stride = "寄り道", min(0.1, wd)
            self._moving_to = (distance, angle)

            # 用心（L2 が不快で主導した強さ）が、動き方を変える
            caution = self.caution if self.MODE_FROM_SYNC else 0.0
            if caution >= self.AVOID_AT and self._predict_human_collision()[0] > 0:
                # はっきり用心していて、いまの道が人にかかっている: 道を立て直す
                # （寄り道の途中でも、いまの道を捨てて考え直す）
                if self._waypoint is not None:
                    self._waypoint = None
                    bearing = self._target_bearing()
                    self._moving_to = (bearing[0], bearing[1]) if bearing else self._moving_to
                if self._plan_detour():
                    wx, wy = self._waypoint      # ここからは寄り道の点へ向かう
                    self._moving_to = (math.hypot(wx - self.l1.position[0], wy - self.l1.position[1]),
                                       self._angle_to(self._waypoint))
                    return "道を立て直す"
                self.waits += 1
                return "待つ"                    # 立て直せない: 用心があるあいだは動かない
            if abs(angle) > 5.0:                 # まず向きを合わせる
                self._turn_by(angle)
                return f"{label}:向きを合わせる"
            note = "（記憶）" if source == "記憶" else ""
            if caution > 0.05:
                slow = stride * (1.0 - caution)
                if slow < 0.005:
                    self.waits += 1
                    return "待つ"
                self.l1.move_forward(distance=slow)
                return f"{label}:そろそろ{note}"
            self.l1.move_forward(distance=stride)
            return f"{label}:前進{note}"

        self.queue.pop(0)
        if prim == "look_at_target":
            return "見る"
        with contextlib.redirect_stdout(io.StringIO()):
            result = self._execute_one(prim, self.multiplier)
        if prim.endswith("hand_close") and self.current_target:
            self.world.try_grip()
        if prim.endswith("hand_open"):
            self.world.release()
        if result != p16.PrimitiveResult.SUCCESS:
            self._abort(f"{prim} に失敗")
        return prim

    # --- 1ステップ ---

    def step(self):
        self.step_count += 1
        self.world.begin_step()
        self._events = []
        self._notes = []
        self._search_error = 0.0
        had_plan = bool(self.queue)

        # 1. 動く（基本動作を1つ）
        action = self._act()
        if had_plan and not self.queue and "タスク失敗" not in self._events:
            # 反射で中止したあとの1歩後退が終わったときは、完了ではなく失敗
            self._events.append("タスク失敗" if self._aborting else "タスク完了")
            self._aborting = False

        # 2. 感じる（L1 → L2 → L3）
        sensor = {
            "visual": self.world.get_visual_info(),
            "tactile": {"collision": bool(self.world.last_collision),
                        "collision_target": self.world.last_collision or "unknown",
                        "grip": self.world.last_grip},
            "auditory": {"voice": bool(self.heard), "is_human": True, "text": self.heard},
        }
        heard_now, self.heard = self.heard, ""
        if heard_now:
            self._to_parse = heard_now          # 理解するのは次のステップ
        self._memorize(sensor["visual"])
        qualia_list, error = self._layer2_3_process(sensor)

        # L3 の見込み → L2 の不快: このまま進むと人にぶつかりそうか
        imminence, _ = self._predict_human_collision()
        if imminence > 0:
            hit_value = self.l2.DNA_VALUES["人にぶつかった"][0]
            q = p16.Qualia(label="人にぶつかりそう", value=hit_value * imminence,
                           priority=p16.Priority.HIGH, source="internal", target="人")
            self.l2.current_qualia.append(q)
            qualia_list.append(q)
        for d, _a in self._humans_known():
            self.min_human_distance = min(self.min_human_distance, d)
        for label in self._events:
            q = self.l2._create_qualia(label, "internal")
            self.l2.current_qualia.append(q)
            qualia_list.append(q)
            error = max(error, self.l3.process_qualia([q]))
        gain = self.l5.entrain_gain
        if self.L3_LEARN:
            # このステップで新しく出た誤差（クオリアごとのずれ、探しているときの見込みとのずれ）
            fresh = max([self.l3._calculate_error(q) for q in self.l2.current_qualia] +
                        [self._search_error])
            # 前のステップの驚きは L3_RESIDUAL の割合で残る
            error = max(min(1.0, fresh * gain["L3"]), self._l3_prev * self.L3_RESIDUAL)
            self._learn_predictions()              # 見えているものに慣れる
        else:
            error = min(1.0, error * gain["L3"])   # フェーズ16のまま
        self.l3.prediction_error = error
        self._l3_prev = error

        # 引き込み（前のステップの主導層が、L2 の応答を大きくする。L3 は上で掛けた）
        for q in self.l2.current_qualia:
            q.base_value = q.value
            q.value = max(-1.0, min(1.0, q.value * gain["L2"]))

        # 3. 反射（最優先の不快が出たら、予定を捨てて1歩下がる）
        reflex = False
        if self.REFLEX and any(q.is_critical() and q.is_negative() for q in self.l2.current_qualia):
            if self.queue != ["move_back"]:
                self.queue = ["move_back"]
                self._aborting = True
                reflex = True

        # 4. 同期の判定
        self.l5.check_sync(self.l1, self.l2, self.l3, self.l4)

        # 5. 用心: L2 が不快の側で主導したら、その強さが用心になる。主導が終われば少しずつ消える。
        led = 0.0
        if self.l5.sync_type == "L2" and getattr(self.l5, "last_l2_signed", 0.0) < 0:
            led = self.l5.leader_strength
        self.caution = max(led, self.caution * self.CAUTION_DECAY)
        if not self.queue:
            self._moving_to = None

        row = {
            "step": self.step_count,
            "action": action + ("（反射で中止）" if reflex else ""),
            "qualia": [q.label for q in self.l2.current_qualia],
            "notes": list(self._notes),
            "raw": dict(self.l5.last_raw),
            "act": dict(self.l5.last_activities),
            "leader": self.l5.sync_type,
            "strength": self.l5.leader_strength,
            "score": self.l5.sync_score,
            "on": self.l5.sync_on,
            "collision": self.world.last_collision,
            "caution": self.caution,
        }
        self.log.append(row)
        return row


# ==========================================
# シナリオ
# ==========================================

def make_world(kind):
    """ロボットは (3, 3) にいて、東（x の正の向き）を向いている。"""
    world = FlatWorld()
    if kind in ("fetch", "human"):
        world.add("赤いボール", "ball", 3.0, 5.0, color="red", shape="sphere", radius=0.1)
    if kind == "human":
        world.add("人", "human", 3.0, 4.2, radius=0.3)   # ボールへの道の途中に人がいる
    if kind == "blocked":                               # 人が3人並んでいて、横を通れない
        world.add("赤いボール", "ball", 3.0, 5.0, color="red", shape="sphere", radius=0.1)
        for hx in (2.2, 3.0, 3.8):
            world.add("人", "human", hx, 4.2, radius=0.3)
    if kind == "human_side":
        world.add("赤いボール", "ball", 3.0, 5.0, color="red", shape="sphere", radius=0.1)
        world.add("人", "human", 3.8, 4.2, radius=0.3)   # 道から 0.8 離れたところに人がいる
    if kind == "missing":
        world.add("青い箱", "box", 5.0, 3.0, color="blue", shape="box", radius=0.2)
    if kind in ("remembered", "moved"):
        world.add("赤いボール", "ball", 3.0, 5.0, color="red", shape="sphere", radius=0.1)   # 北
        world.add("青い箱", "box", 1.0, 3.0, color="blue", shape="box", radius=0.2)          # 西
    return world


SCENARIOS = (
    ("fetch",      "持ってくる（赤いボールが北にある）"),
    ("human",      "途中に人がいる"),
    ("human_side", "道から離れたところに人がいる"),
    ("blocked",    "人が並んでいて通れない"),
    ("missing",    "探しても見つからない"),
    ("remembered", "前に見かけた場所にある（先に青い箱を探させ、途中で赤いボールを見ている）"),
    ("moved",      "前に見かけた場所から動かされている"),
)

FIRST_COMMAND = "飛騨、青い箱を探して"     # remembered / moved で先に出す指示


def run(kind, sync_class=RobotSyncOn, entrain_k=0.5, idle_before=3, idle_after=8,
        max_steps=120, reflex=True, l3_learn=True, l4_recall=True, place_memory=True,
        mode_from_sync=True, command="飛騨、赤いボールを持ってきて"):
    world = make_world(kind)
    hida = HidaPhase17(world, sync_class=sync_class, entrain_k=entrain_k)
    hida.REFLEX = reflex
    hida.L3_LEARN = l3_learn
    hida.L4_RECALL = l4_recall
    hida.l1.position = [3.0, 3.0, 0.0]
    hida.l1.direction = 0.0
    world._last_pos = [3.0, 3.0, 0.0]
    hida.PLACE_MEMORY = place_memory
    hida.MODE_FROM_SYNC = mode_from_sync
    hida.marks = {}

    def give(text):
        hida.marks[hida.step_count + 1] = text
        hida.hear(text)
        quiet, limit = 0, hida.step_count + max_steps
        while hida.step_count < limit and quiet < idle_after:
            hida.step()
            quiet = quiet + 1 if not (hida.queue or hida._to_parse) else 0

    for _ in range(idle_before):
        hida.step()
    if kind in ("remembered", "moved"):
        give(FIRST_COMMAND)
        if kind == "moved":                     # ロボットが見ていないあいだに、東へ動かす
            for o in world.objects:
                if o["name"] == "赤いボール":
                    o["x"], o["y"] = 5.0, 3.0
    give(command)
    return hida


# 意識の強さの段階（同期スコアの区切り。仮の値。0.30 は v2.2 の同期ONの閾値）
LEVELS = ((0.30, "はっきり"), (0.15, "弱い"), (0.05, "かすか"), (0.0, "なし"))
FOCUS_WINDOW = 5


def level_of(score, on=False):
    """意識の強さの段階。同期ONのあいだは「はっきり」とする。

    同期ONは、一度入ると OFF の閾値を下回るまで続く（v2.2 のヒステリシス）。
    ONのあいだは、スコアが 0.30 を少し下回っていても「はっきり」と呼ぶ。
    """
    if on:
        return "はっきり"
    for limit, name in LEVELS:
        if score >= limit:
            return name
    return "なし"


def focus_of(log, i):
    """直近 FOCUS_WINDOW ステップで、主導の強さが1つの層に偏っている度合い。

    返り値: (いちばん多い層, その層が占める割合, 期間中の主導の強さの平均)
    割合が 1.0 なら1つの層だけが主導していた。3層で等分なら 0.33。
    """
    window = log[max(0, i - FOCUS_WINDOW + 1): i + 1]
    total = {}
    for r in window:
        if r["leader"]:
            total[r["leader"]] = total.get(r["leader"], 0.0) + r["strength"]
    s = sum(total.values())
    if s <= 0:
        return None, 0.0, 0.0
    top = max(total, key=total.get)
    return top, total[top] / s, s / len(window)


def print_graded(hida, title):
    print("=" * 96)
    print(title + "   〔強さのまま見る版〕")
    print("=" * 96)
    print(f"{'歩':>3} {'動作':<16}{'主導':<4}{'強さ':>5}  {'意識の強さ':<12}{'集中（直近5歩）':<18}クオリア")
    for i, r in enumerate(hida.log):
        if r["step"] in getattr(hida, "marks", {}):
            print(f"    ---- 「{hida.marks[r['step']]}」----")
        action = r["action"]
        pad = max(0, 16 - sum(2 if ord(c) > 255 else 1 for c in action))
        lv = f"{r['score']:.2f} {level_of(r['score'], r['on'])}"
        pad2 = max(0, 14 - sum(2 if ord(c) > 255 else 1 for c in lv))
        top, share, mean = focus_of(hida.log, i)
        fc = f"{top} {share:.0%} (平均{mean:.2f})" if top else "-"
        pad3 = max(0, 22 - sum(2 if ord(c) > 255 else 1 for c in fc))
        print(f"{r['step']:>3} {action}{' ' * pad}{(r['leader'] or '-'):<4}{r['strength']:>5.2f}  "
              f"{lv}{' ' * pad2}{fc}{' ' * pad3}{'、'.join(r['qualia'])}"
              + (f"  〔{'、'.join(r['notes'])}〕" if r["notes"] else ""))


def summarize_graded(hida):
    log = hida.log
    counts = {name: 0 for _, name in LEVELS}
    for r in log:
        counts[level_of(r["score"], r["on"])] += 1
    led = [r for r in log if r["leader"]]
    return {
        "steps": len(log),
        "levels": counts,
        "led": len(led),
        "strong": sum(1 for r in led if r["strength"] >= 0.30),
        "weak": sum(1 for r in led if r["strength"] < 0.30),
        "leaders": {k: sum(1 for r in led if r["leader"] == k) for k in ("L2", "L3", "L4")},
    }


def print_log(hida, title):
    print("=" * 96)
    print(title)
    print("=" * 96)
    print(f"{'歩':>3} {'動作':<16}{'主導':<5}{'強さ':>5} {'同期':>6}  {'L1':>5}{'L2':>5}{'L3':>5}{'L4':>5}  クオリア")
    for r in hida.log:
        if r["step"] in getattr(hida, "marks", {}):
            print(f"    ---- 「{hida.marks[r['step']]}」----")
        a = r["act"]
        mark = "ON " if r["on"] else "   "
        action = r["action"]
        pad = max(0, 16 - sum(2 if ord(c) > 255 else 1 for c in action))
        print(f"{r['step']:>3} {action}{' ' * pad}{(r['leader'] or '-'):<5}{r['strength']:>5.2f} "
              f"{r['score']:>5.2f}{mark} {a['L1']:>5.2f}{a['L2']:>5.2f}{a['L3']:>5.2f}{a['L4']:>5.2f}  "
              f"{'、'.join(r['qualia'])}" + (f"  〔{'、'.join(r['notes'])}〕" if r["notes"] else ""))


def summarize(hida):
    log = hida.log
    named = [r["leader"] for r in log if r["leader"]]
    episodes, cur = [], 0
    for r in log:
        if r["on"]:
            cur += 1
        elif cur:
            episodes.append(cur); cur = 0
    if cur:
        episodes.append(cur)
    return {
        "steps": len(log),
        "on": sum(r["on"] for r in log),
        "episodes": episodes,
        "leaders": {k: named.count(k) for k in ("L2", "L3", "L4")},
        "switches": sum(a != b for a, b in zip(named, named[1:])),
        "collisions": sum(1 for r in log if r["collision"]),
        "done": any("タスク完了" in r["qualia"] for r in log),
        "min_human": hida.min_human_distance,
        "replans": hida.replans,
        "waits": hida.waits,
        "human_hits": sum(1 for r in log if r["collision"] == "human"),
    }


def main():
    for kind, title in SCENARIOS:
        hida = run(kind)
        print_log(hida, title)
        s = summarize(hida)
        print(f"\n  ステップ {s['steps']}  同期ON {s['on']}  ONの区間 {s['episodes']}  "
              f"主導 {s['leaders']}  交代 {s['switches']}  人との衝突 {s['human_hits']}\n")

    print("=" * 96)
    print("まとめ（引き込みあり・なし、同期ONのあいだ同期しやすくする働きあり・なし）")
    print("=" * 96)
    print(f"{'シナリオ':<8}{'条件':<24}{'ステップ':>6}{'同期ON':>7}  {'ONの区間':<16}{'主導 L2/L3/L4':<16}{'交代':>4}{'人との衝突':>8}")
    for kind, title in SCENARIOS:
        for label, cls, k in (("引き込みなし", RobotSync, 0.0),
                              ("引き込みあり", RobotSync, 0.5),
                              ("引き込みあり＋ON（標準）", RobotSyncOn, 0.5)):
            s = summarize(run(kind, sync_class=cls, entrain_k=k))
            lead = f"{s['leaders']['L2']}/{s['leaders']['L3']}/{s['leaders']['L4']}"
            pad1 = max(0, 12 - sum(2 if ord(c) > 255 else 1 for c in kind))
            pad2 = max(0, 26 - sum(2 if ord(c) > 255 else 1 for c in label))
            print(f"{kind}{' ' * pad1}{label}{' ' * pad2}{s['steps']:>6}{s['on']:>7}  "
                  f"{str(s['episodes']):<16}{lead:<16}{s['switches']:>4}{s['human_hits']:>8}")
    print("\n" + "=" * 96)
    print("強さのまま見る版（RobotSyncGradedOn）")
    print("=" * 96)
    for kind, title in SCENARIOS:
        hida = run(kind, sync_class=RobotSyncGradedOn)
        print_graded(hida, title)
        g = summarize_graded(hida)
        print(f"\n  ステップ {g['steps']}  意識の強さ {g['levels']}  "
              f"主導あり {g['led']}（強い {g['strong']}、弱い {g['weak']}）  主導 {g['leaders']}\n")
    print("\n" + "=" * 96)
    print("同期の判定を動きに返す／返さない（「途中に人がいる」）")
    print("=" * 96)
    print(f"{'同期判定':<18}{'危険の数え方':<14}{'動きに返す':<12}{'ステップ':>6}{'人との衝突':>8}{'持ってこられたか':>12}{'人との最短距離':>10}{'立て直し':>6}")
    for cls, cname in ((RobotSyncOn, "切る版"), (RobotSyncGradedOn, "強さのまま見る版")):
        for level in (False, True):
            for mode in (False, True):
                RobotActivity.L2_THREAT_LEVEL = level
                s = summarize(run("human", sync_class=cls, mode_from_sync=mode))
                cells = (cname, "強さ" if level else "変化", "返す" if mode else "返さない")
                widths = (18, 14, 12)
                line = "".join(c + " " * max(0, w - sum(2 if ord(ch) > 255 else 1 for ch in c))
                               for c, w in zip(cells, widths))
                print(f"{line}{s['steps']:>8}{s['human_hits']:>10}{('はい' if s['done'] else 'いいえ'):>14}"
                      f"{s['min_human']:>14.2f}{s['replans']:>9}")
    RobotActivity.L2_THREAT_LEVEL = True

    print("\n" + "=" * 96)
    print("危険に慣れる／慣れない（「人が並んでいて通れない」）")
    print("=" * 96)
    print(f"{'同期判定':<18}{'危険に':<10}{'ステップ':>6}{'人との衝突':>8}{'待った回数':>8}{'人との最短距離':>10}")
    for cls, cname in ((RobotSyncOn, "切る版"), (RobotSyncGradedOn, "強さのまま見る版")):
        for no_hab in (False, True):
            RobotActivity.DANGER_NO_HABITUATION = no_hab
            s = summarize(run("blocked", sync_class=cls))
            cells = (cname, "慣れない" if no_hab else "慣れる")
            line = "".join(c + " " * max(0, w - sum(2 if ord(ch) > 255 else 1 for ch in c))
                           for c, w in zip(cells, (18, 10)))
            print(f"{line}{s['steps']:>8}{s['human_hits']:>10}{s['waits']:>12}{s['min_human']:>14.2f}")
    RobotActivity.DANGER_NO_HABITUATION = True
    print("\n場所の記憶を切った場合（PLACE_MEMORY = False）:")
    for kind, title in SCENARIOS:
        s = summarize(run(kind, place_memory=False))
        print(f"  {kind:<11} ステップ {s['steps']}  同期ON {s['on']}  ONの区間 {s['episodes']}  "
              f"主導 {s['leaders']}  交代 {s['switches']}")
    print("\nL3 の予測の更新・L4 の思い出し・場所の記憶を切った場合（フェーズ16の L3・L4 のまま）:")
    for kind, title in SCENARIOS:
        s = summarize(run(kind, l3_learn=False, l4_recall=False, place_memory=False))
        print(f"  {kind:<11} ステップ {s['steps']}  同期ON {s['on']}  ONの区間 {s['episodes']}  "
              f"主導 {s['leaders']}  交代 {s['switches']}")
    print("\n反射を切り、同期の判定も動きに返さない場合（フェーズ16の作りに近い条件）で「途中に人がいる」:")
    s = summarize(run("human", reflex=False, mode_from_sync=False))
    print(f"  ステップ {s['steps']}  人との衝突 {s['human_hits']} 回  持ってこられたか {'はい' if s['done'] else 'いいえ'}")
    print("反射だけを切った場合（同期の判定は動きに返す）:")
    s = summarize(run("human", reflex=False))
    print(f"  ステップ {s['steps']}  人との衝突 {s['human_hits']} 回  持ってこられたか {'はい' if s['done'] else 'いいえ'}")

if __name__ == "__main__":
    main()
