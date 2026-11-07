# HIDA Unified - 5層意識モデル統合版

## 概要

「人間の内面運動理論」に基づく5層意識モデルを1ファイルに統合した実装。
**脚本なし、数値の力学だけで行動と性格が決まる。**

## アーキテクチャ

```
L1（身体）→ position, energy, fatigue
    ↓
L2（クオリア）→ valence, arousal, fear, desire, urgency
    ↓
L3（予測）→ 予測誤差検出
    ↓
L4（記憶）→ 内部マップ、LTM、変調値
    ↓
L5（意識）→ 同期検知、自認、言語化
    ↓
LLM → 自然言語での自己表現
```

## 核心的発見

### 1. L5（意識）は判断しない

```
❌ L5が判断する主体
✅ L5は同期検知 + 言語系への橋渡し

行動決定: L2/L3/L4の数値計算から自然に決まる
言語化: LLMが状態を言葉に変換
```

### 2. 記憶 → 数値変調 → 行動変化 → 性格形成

```
経験の蓄積（LTM）
    ↓
変調値（hida_modulation.json）
  - fear_weight: 恐怖感度
  - safe_preference: 安全志向度
  - energy_caution: エネルギー慎重さ
    ↓
L2クオリアに適用
    ↓
スコア計算が変わる
    ↓
行動が変わる
```

**脚本テキストなし。数値だけで性格が決まる。**

### 3. 環境が変われば性格も変わる

```
低エネルギー続き → 緑（安全）を選ぶ → safe_pref上昇 → 慎重派
高エネルギー続き → 赤（好き）を選ぶ → safe_pref低下 → 冒険派

環境 → 行動 → 記憶 → 変調値 → 行動（ループ）
```

### 4. 痛い目に遭うと怖がりになる

```
危険ゾーン内で33%でダメージ
    ↓
danger_damageとして記憶
    ↓
fear_weight上昇（1.0 → 1.1 → 1.2...）
    ↓
danger_penaltyが大きくなる
    ↓
高エネルギーでも赤を避けるようになる
```

**数値例：**
```
fear_weight=1.0: red=4.0 → 赤を選ぶ
fear_weight=2.0: red=1.0 → 緑を選ぶ（赤を避ける）
```

## 使い方

```bash
# 通常テスト（高E→低Eの2回）
python hida_unified.py

# 低エネルギー5回（慎重派になる）
python hida_unified.py loop

# 高エネルギー5回（冒険派になる）
python hida_unified.py loop_high

# 記憶と変調値をリセット
python hida_unified.py reset
```

### ollama使用

```bash
ollama pull gemma3:4b
python hida_unified.py
```

### Claude API使用

```bash
# Windows
set ANTHROPIC_API_KEY=your-api-key-here

# Mac/Linux
export ANTHROPIC_API_KEY=your-api-key-here

python hida_unified.py
```

## テスト結果例

### 性格変化の実験

```
Step 1: 低エネルギー5回
  safe_pref: 0.00 → 0.30（慎重派）

Step 2: 高エネルギー5回
  safe_pref: 0.30 → 0.17（冒険派）

Step 3: また低エネルギー5回
  safe_pref: 0.17 → 0.19（また慎重派に）
```

経験が蓄積するほど変化は緩やかになる（人間と同じ）

### スコア計算式

```python
score = preference × 10 
      - distance × (0.5 + urgency)
      - danger_penalty × fear_weight
      + safe_bonus
      - energy_penalty × (1 + energy_caution)
```

## ファイル構成

| ファイル | 説明 |
|---------|------|
| `hida_unified.py` | 全層統合コード（L1〜L5 + LLM） |
| `hida_ltm.json` | 長期記憶（自動生成） |
| `hida_modulation.json` | 変調値（自動生成） |

## 理論的意義

### 意識の役割

```
L5（意識）= L1〜L4の状態を自認 + 言語化 + コミュニケーション
         = 内部状態の「外部出力インターフェース」
         ≠ 判断する主体
```

### 性格形成のメカニズム

```
DNA由来: color_preference（好み）
身体: energy, fatigue
記憶: LTM → 変調値

これらの数値の力学で行動が決まる
LLMは数値を見て「慎重派だから」と言語化するだけ
```

### Confabulation（作話）

```
同じ情報を渡しても:
  低能力LLM: confabulationする（後付け説明）
  高能力LLM: 正確に自己認識する

LLMの能力 = 自己認識の精度
```

## ライセンス

MIT License

## 関連

- [人間の内面運動理論](https://github.com/tomato-and-mozzarella/human-inner-movement-theory)
