# 🎓 EduMind AI
### Your Personal AI-Powered Learning Companion

<p align="center">

  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-RAG-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-Workflows-1C3C3C?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge" />
  <img src="https://img.shields.io/badge/FAISS-Vector_Search-00ADD8?style=for-the-badge" />
  <img src="https://img.shields.io/badge/SQLite-User_Analytics-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />

</p>

<p align="center">
  <strong>EduMind doesn't just generate educational content — it learns how you learn.</strong>
</p>

---

## 🌟 What is EduMind?

**EduMind AI** is an AI-powered personalized learning platform designed to transform traditional studying into an **adaptive, data-driven learning experience**.

Instead of treating every student the same, EduMind analyzes the learner's activity, identifies **weak and strong topics**, monitors learning consistency, and generates personalized study recommendations.

At the same time, students can interact directly with their lecture materials through **RAG-powered PDF conversations**, generate quizzes and flashcards, create assignments, and monitor their progress from a unified dashboard.

### The core idea

> **Learn → Practice → Analyze → Personalize → Improve**

EduMind continuously uses the learner's previous activity to determine **what they should study next**.

---

# 🚀 Key Features

## 🧠 1. AI-Powered Quiz Generator

Generate quizzes based on educational content while controlling:

- 📚 Topic
- 🎯 Student level
- 📈 Difficulty
- 🔢 Number of questions

Quiz activity is stored and later used by the personalization engine to analyze performance.

---

## 🃏 2. Intelligent Flashcards

Turn learning material into flashcards designed for active recall.

The system generates:

- Key concepts
- Definitions
- Important facts
- Concept explanations

Flashcard activity contributes to the learner's overall engagement profile.

---

## ✍️ 3. AI Assignment Generator

EduMind can generate structured assignments based on supplied educational material.

The assignment workflow uses **LangGraph** to create a multi-step generation and review process:

```text
                 ┌──────────────────┐
                 │   Source Material │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │ Generate Draft   │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │   AI Reviewer    │
                 └────────┬─────────┘
                          ↓
                    ┌─────┴─────┐
                    │ Approved? │
                    └─────┬─────┘
                      Yes │ No
                          │  └──────────→ Improve
                          ↓
                     Final Assignment