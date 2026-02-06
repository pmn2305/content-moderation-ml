# 🛡️ Multi-Modal Content Moderation System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react)](https://react.dev/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker)]
[![Deployed](https://img.shields.io/badge/Status-Live-success)]

A **production-style multi-modal content moderation system** that evaluates **text and images concurrently**, applies **rate limiting and caching**, and returns a unified moderation decision with model-level scores.

Built with **FastAPI, React (Vite), Redis**, and deployed on **Railway + Vercel**.

---

## 🚀 Live Demo
**Frontend (Vercel):**  
👉 https://content-moderation-ml.vercel.app/

> Backend is deployed on Railway and consumed by the frontend.

---

## 🧠 What This System Does
- Moderates **text + image content** in a single request
- Runs **parallel inference** using async execution
- Applies **rate limiting per IP**
- Uses **Redis caching** for repeated inputs
- Gracefully degrades if a model or cache is unavailable
- Returns **decision + confidence scores + model versions**

---

## 🏗️ System Architecture

```

Client (React)
↓
API Gateway (FastAPI)
├── Redis (rate limit + cache)
└── Inference Service
├── Text Model (toxic-bert)
└── Image Model (nsfw-vit)

````

---

## 🧪 Example API Response
```json
{
  "decision": "REJECT",
  "scores": {
    "text": 0.979,
    "image": 0.004
  },
  "model_versions": {
    "text": "toxic-bert-v1",
    "image": "nsfw-vit-v1"
  }
}
````

---

## ⚙️ Tech Stack

**Frontend**

* React + Vite
* Tailwind CSS
* Fetch API

**Backend**

* FastAPI
* Async HTTPX
* Redis (rate limiting + caching)
* Structured logging & metrics

**Deployment**

* Frontend: **Vercel**
* Backend & Inference: **Railway**

---

## 📈 Key Engineering Highlights

* Async `asyncio.gather` for parallel inference
* Hash-based cache keys for text + image
* Redis-backed sliding rate limit
* Fault-tolerant inference (`safe_infer`)
* Metrics for latency, cache hits, degraded responses

---

## 🛠️ Running Locally (Optional)

```bash
# Backend
uvicorn src.serving.main:app --reload --port 8000

# Inference service
uvicorn src.inference.main:app --reload --port 8001

# Frontend
npm install
npm run dev
```

Redis must be running on `localhost:6379`.

---

## 📌 Status

✅ Fully functional
✅ Deployed
🚧 Future work: auth, persistent metrics, real model weights

---

## 👩‍💻 Author

**Prerana M N**
AI / ML • Systems • Backend Engineering


