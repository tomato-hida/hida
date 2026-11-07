# HIDA Unified - 5層統合版

## 概要

5層意識モデルを1ファイルに統合した実装。

## 構造

```
L1（身体）→ position, energy, fatigue
    ↓
L2（クオリア）→ valence, arousal, fear, desire, urgency
    ↓
L3（予測）→ 予測誤差検出
    ↓
L4（記憶）→ 内部マップ、ラベル辞書
    ↓
L5（意識）→ 同期検知、自認、言語化
    ↓
LLM → 自然言語での自己表現
```

## 使い方

```bash
# 基本テスト
python hida_unified.py

# ollama使用
ollama pull gemma3:4b
python hida_unified.py

# Claude API使用
export ANTHROPIC_API_KEY=your-api-key-here
python hida_unified.py
```

## テスト結果例

**通常エネルギー（赤好き）:**
```
red=2.0 > green=2.0 > blue=1.5
→ 赤（好き）を選択
```

**低エネルギー（赤好き）:**
```
green=2.0 > blue=1.5 > red=-1.5
→ 緑（近い）を選択
→ エネルギーペナルティで赤がマイナスに
```

## ライセンス

MIT
