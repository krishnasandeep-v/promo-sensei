# 🤖 Promo Sensei

**Promo Sensei** is a smart Slack-based assistant (or chatbot UI) that helps users discover real-time promotional offers from top e-commerce and brand websites. Powered by dynamic scraping, vector search, and RAG (Retrieval-Augmented Generation), Promo Sensei delivers accurate, cost-efficient, and user-friendly responses to deal-related queries.

## 🔍 Overview

This project demonstrates:  
- Automated web scraping from promotional deal pages  
- Efficient vector-based retrieval using FAISS  
- RAG-based query pipeline using OpenAI GPT  
- Slack bot interface for seamless interaction (or optional local chatbot UI)

---

## 📸 Demo Screenshots

### 🎯 Example Query  
> **User**: *"Any flat 50% off deals today?"*

![Flat 50% Query](screenshots/flat_50_off.png)

---

### 🧴 Example Brand Summary  
> **User**: *"/promosensei brand Nykaa"*

![Nykaa Deals](screenshots/nykaa_brand_summary.png)

---

### 🛍️ Output Format (as returned by the bot)

```json
[
  {
    "Title": "Flat 50% Off on Skincare Combos",
    "Description": "Buy Nykaa skincare combos and get 50% off for a limited time.",
    "Products": ["Face Wash", "Moisturizers", "Serums"],
    "Offer": "Flat 50% off on selected combos",
    "Expiry": "2025-05-31",
    "Brand": "Nykaa",
    "Link": "https://www.nykaa.com/offers/skincare-combo"
  },
  {
    "Title": "Puma End of Season Sale",
    "Description": "Up to 60% off on footwear, apparel, and accessories.",
    "Products": ["Running Shoes", "Track Pants", "T-Shirts"],
    "Offer": "Upto 60% off",
    "Expiry": "2025-06-15",
    "Brand": "Puma",
    "Link": "https://www.puma.com/in/en/deals/eoss"
  }
]
