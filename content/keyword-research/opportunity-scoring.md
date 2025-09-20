---
title: "📊 Opportunity Scoring"
description: "Prioritize keywords by combining demand, difficulty, and business value into a simple, transparent score."
category: "keyword research & search intent"
order: 2.8
toc: true
updated: "2025-09-20"
canonical: "/keyword-research/opportunity-scoring"
quizzes:
  - id: opp-quiz-1
    question: Which factor is LEAST appropriate for opportunity scoring?
    type: single
    options:
      - text: Content–intent fit
        correct: false
      - text: Business value (LTV/ACV potential)
        correct: false
      - text: Website color scheme
        correct: true
        explain: Visual theme doesn’t affect keyword opportunity.
---

# 📊 Opportunity Scoring

> 📌 **TL;DR:** Build a lightweight model: prioritize terms with strong demand, high value, and achievable difficulty.

---

## 🧮 A Simple Model

Let: V = normalized volume, D = normalized difficulty (invert: 1−KD), B = business value (0–1), I = intent fit (0–1)

```
Score = 0.35·V + 0.25·(1−KD) + 0.25·B + 0.15·I
```

Adjust weights to emphasize pipeline vs. traffic goals.

---

## 📋 Example Table

| Keyword | V | KD | 1−KD | B | I | Score |
|---------|---|----|------|---|---|-------|
| crm for freelancers | 0.3 | 0.4 | 0.6 | 0.7 | 0.8 | 0.53 |
| best crm for smb | 0.6 | 0.7 | 0.3 | 0.8 | 0.9 | 0.51 |
| what is crm | 0.8 | 0.6 | 0.4 | 0.2 | 0.9 | 0.49 |

> [!TIP] A lower-volume, high-value, achievable term can outrank a high-volume but hard, low-value one in your roadmap.

---

## ⚠️ Pitfalls

- Garbage in, garbage out: validate data sources
- Double-counting correlated metrics
- Static models in changing markets

---

## ✅ Opportunity Checklist

- [ ] Define scoring inputs (volume, difficulty, intent fit, value)
- [ ] Normalize inputs to 0–1 scales
- [ ] Assign weights reflecting your strategy
- [ ] Review top 20 outputs manually for sanity
- [ ] Recalculate quarterly as markets shift

---

## 📚 Resources

- Scoring spreadsheet templates
- Your CRM and analytics for value mapping

