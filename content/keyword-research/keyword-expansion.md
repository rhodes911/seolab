---
title: "🔎 Keyword Expansion"
description: "Grow from seeds to a comprehensive set of related queries using autosuggest, People Also Ask, SERP mining, and tool-based expansions."
category: "keyword research & search intent"
order: 2.2
toc: true
updated: "2025-09-20"
canonical: "/keyword-research/keyword-expansion"
quizzes:
  - id: kw-expansion-quiz-1
    question: Which technique directly surfaces user phrasing from Google’s interface?
    type: single
    options:
      - text: Keyword difficulty scoring
        correct: false
      - text: People Also Ask and autosuggest
        correct: true
        explain: These reflect real queries and related questions.
      - text: Backlink analysis
        correct: false
---

# 🔎 Keyword Expansion

> 📌 **TL;DR:** Expand each seed using autosuggest, People Also Ask (PAA), related searches, and SERP mining. Normalize and tag results to prepare for clustering.

---

## 🧰 Expansion Inputs & Outputs

```
Seeds ──► Autosuggest ──► PAA ──► Related Searches ──► SERP Titles ──► Expanded List
```

### Common Modifier Buckets

| Intent | Modifiers |
|-------|-----------|
| Informational | how, what, guide, tutorial, examples |
| Transactional | buy, pricing, cost, plans, compare |
| Commercial | best, top, vs, review, alternatives |
| Local | near me, in [city], [service] [city] |

> [!TIP] Keep modifiers as structured tags. They help with both clustering and intent mapping later.

---

## 🔬 Methods That Scale

- Autosuggest sweep: Append A–Z letters to seeds and collect suggestions
- PAA chain: Click questions to reveal more related questions
- Related searches: Capture bottom-of-SERP suggestions
- SERP mining: Scrape titles/H1s of ranking pages for phrasing patterns
- Tool assists: Use research tools to accelerate, then validate in SERPs

---

## 🧹 Normalize and De-duplicate

1. Lowercase and trim
2. Singular/plural unify
3. American/British spellings map
4. Remove exact duplicates and near-duplicates (Levenshtein/TF-IDF)

> [!WARNING] Over-aggressive normalization can merge distinct intents (e.g., "apple watch" vs. "watch apple event"). Manually review edge cases.

---

## 🏷️ Tagging for Context

Add columns: seed, modifier, location, audience, product line. These tags multiply value in clustering and prioritization.

---

## ✅ Expansion Checklist

- [ ] Prepare 30–100 cleaned seed keywords
- [ ] Collect autosuggest variants per seed
- [ ] Extract People Also Ask questions
- [ ] Mine related searches and SERP titles
- [ ] Deduplicate and unify plural/singular, UK/US variants
- [ ] Tag by modifier type (how, best, near me, cost)
- [ ] Spot-check SERPs to ensure topical relevance

---

## 📚 Resources

- Google autosuggest and People Also Ask
- Related searches and SERP titles
- Third-party tools (keep as assist, not truth)

