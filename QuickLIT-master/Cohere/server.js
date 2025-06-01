const express = require("express");
const cors = require("cors");
const axios = require("axios");
const path = require("path");
require("dotenv").config();

const app = express();

// CORS ve JSON middleware'leri
app.use(cors());
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" }));

// Statik dosyalar için middleware
app.use(express.static(path.join(__dirname)));

// API anahtarı
const COHERE_API_KEY = process.env.COHERE_API_KEY;

// API istek sayacı ve hız sınırlama
const requestCounts = new Map();
const RATE_LIMIT = 10; // 1 dakikada maksimum istek sayısı
const RATE_WINDOW = 60000; // 1 dakika (milisaniye)

// Hız sınırlama middleware'i
function rateLimiter(req, res, next) {
  const ip = req.ip;
  const now = Date.now();

  if (!requestCounts.has(ip)) {
    requestCounts.set(ip, { count: 1, timestamp: now });
  } else {
    const data = requestCounts.get(ip);
    if (now - data.timestamp > RATE_WINDOW) {
      data.count = 1;
      data.timestamp = now;
    } else if (data.count >= RATE_LIMIT) {
      return res
        .status(429)
        .json({ error: "Çok fazla istek. Lütfen biraz bekleyin." });
    } else {
      data.count++;
    }
  }
  next();
}

// Ana sayfa route'u - HTML dosyasını gönder
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "index.html"));
});

// Özetleme API endpoint'i
app.post("/summarize", rateLimiter, async (req, res) => {
  try {
    const { text, length, format, model, prompt } = req.body;

    // Girdi doğrulama
    if (!text?.trim()) {
      return res.status(400).json({ error: "Metin boş olamaz" });
    }

    if (text.length > 100000) {
      return res
        .status(400)
        .json({ error: "Metin çok uzun (max: 100,000 karakter)" });
    }

    // API key kontrolü
    if (!COHERE_API_KEY) {
      return res.status(500).json({ error: "Cohere API anahtarı bulunamadı" });
    }

    // Cohere API isteği
    const response = await axios.post(
      "https://api.cohere.ai/v1/summarize",
      {
        text,
        length: length || "medium",
        format: format || "paragraph",
        model: model || "summarize-xlarge",
        prompt,
        temperature: 0.7,
        additional_command: prompt ? `Focus on: ${prompt}` : undefined,
      },
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${COHERE_API_KEY}`,
          Accept: "application/json",
        },
        timeout: 30000, // 30 saniye timeout
      }
    );

    res.json(response.data);
  } catch (error) {
    console.error("API Hatası:", error.response?.data || error.message);

    if (error.code === "ECONNABORTED" || error.message.includes("timeout")) {
      return res.status(408).json({
        error: "Zaman aşımı: API yanıt vermedi. Lütfen tekrar deneyin.",
      });
    }

    if (error.response?.status === 429) {
      return res
        .status(429)
        .json({ error: "API hız sınırı aşıldı. Lütfen biraz bekleyin." });
    }

    const errorMessage = error.response?.data?.message || error.message;
    res.status(error.response?.status || 500).json({
      error: errorMessage,
    });
  }
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: "Sayfa bulunamadı" });
});

// Global hata handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: "Sunucu hatası",
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server çalışıyor: http://localhost:${PORT}`);
});
