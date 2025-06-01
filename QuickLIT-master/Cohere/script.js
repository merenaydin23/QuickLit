// API anahtarı
const COHERE_API_KEY = "8vfnLLHDdh4bLc9c5NjkUOuYjsaZJXI15KBV9BrF";

// Özetleme seviyesi
let selectedDetailLevel = null;

// Özetleme promptları
const PROMPTS = {
  detailed: `Read the following text carefully and create a comprehensive summary that includes the main theme, supporting ideas, examples provided by the author, and any subtopics. Your summary should be 4-5 paragraphs long, with each paragraph focusing on a different aspect of the text. Use an informative and academic style. Include all important details while maintaining a clear logical flow. Each paragraph should be 3-4 sentences long.`,
  medium: `Read the following text and create a concise summary in 2-3 paragraphs. Include the main idea and key supporting points. Each paragraph should be 2-3 sentences long. Use clear and accessible language. Focus on the most important aspects while maintaining a balanced overview.`,
  basic: `Read the following text and create an extremely brief summary in exactly 1 line. Focus ONLY on the main theme/topic. Use the simplest possible language. Do not include any details, examples, or supporting points. The summary must be extremely concise and should not exceed 1 line under any circumstances.`,
};

// Önbellek ve durum yönetimi
const state = {
  cache: new Map(),
  isProcessing: false,
  lastError: null,
  retryCount: 0,
  maxRetries: 3,
  processedSummaries: new Map(),
  textChunks: new Map(), // Metin parçalarını önbellekleme
  lastProcessedText: null, // Son işlenen metni takip etme
};

// İlerleme çubuğu animasyonu
function updateProgress(percent) {
  const bar = document.querySelector(".progress-bar");
  if (bar) {
    bar.style.width = percent + "%";
    bar.parentElement.style.display = percent > 0 ? "block" : "none";

    // Animasyon efekti
    if (percent === 100) {
      bar.classList.add("progress-bar-animated");
      setTimeout(() => {
        bar.classList.remove("progress-bar-animated");
      }, 1000);
    }
  }
}

// Metin parçalama ve temizleme - Optimize edilmiş versiyon
function splitText(text) {
  if (!text?.trim()) return [];

  // Eğer aynı metin daha önce parçalandıysa, önbellekten al
  if (state.textChunks.has(text)) {
    return state.textChunks.get(text);
  }

  // Metni daha hızlı temizleme
  const cleaned = text
    .replace(/\s+/g, " ")
    .replace(/[^\w\s.,!?-]/g, "")
    .trim();

  // Büyük metinleri daha akıllı parçalama
  const chunks = [];
  if (cleaned.length > 100000) {
    const sentences = cleaned.match(/[^.!?]+[.!?]+/g) || [];
    let currentChunk = "";

    for (const sentence of sentences) {
      if ((currentChunk + sentence).length > 100000) {
        chunks.push(currentChunk.trim());
        currentChunk = sentence;
      } else {
        currentChunk += sentence;
      }
    }
    if (currentChunk) chunks.push(currentChunk.trim());
  } else {
    chunks.push(cleaned);
  }

  // Parçaları önbellekle
  state.textChunks.set(text, chunks);
  return chunks;
}

// Hata yönetimi
function handleError(error, output) {
  state.lastError = error;
  state.retryCount++;

  if (state.retryCount <= state.maxRetries) {
    output.value = `Hata: ${error.message}\nYeniden deneniyor... (${state.retryCount}/${state.maxRetries})`;
    return true;
  }

  output.value = `Hata: ${error.message}\nLütfen daha sonra tekrar deneyin.`;
  return false;
}

// Özetleme - Optimize edilmiş versiyon
async function summarizeText() {
  if (state.isProcessing) return;

  const input = document.getElementById("inputText");
  const output = document.getElementById("outputText");
  const button = document.querySelector('button[onclick="summarizeText()"]');

  if (!selectedDetailLevel) {
    alert("Lütfen bir özetleme seviyesi seçin.");
    return;
  }

  const text = input.value;
  if (!text?.trim()) {
    alert("Lütfen metin girin.");
    return;
  }

  // Aynı metin ve seviye kontrolü
  const summaryKey = text + selectedDetailLevel;
  if (state.processedSummaries.has(summaryKey)) {
    const existingSummary = state.processedSummaries.get(summaryKey);
    output.value = existingSummary;
    return;
  }

  try {
    state.isProcessing = true;
    state.retryCount = 0;
    button.disabled = true;
    button.innerHTML =
      '<i class="fas fa-spinner fa-spin me-2"></i>Özetleniyor...';
    output.value = "Özetleniyor...";
    updateProgress(0);

    const chunks = splitText(text);
    const summaries = [];
    const maxConcurrentRequests = 3; // Aynı anda en fazla 3 istek

    // Parçaları gruplar halinde işle
    for (let i = 0; i < chunks.length; i += maxConcurrentRequests) {
      const chunkGroup = chunks.slice(i, i + maxConcurrentRequests);
      const chunkPromises = chunkGroup.map(async (chunk) => {
        const cacheKey = chunk + selectedDetailLevel;
        if (state.cache.has(cacheKey)) {
          return state.cache.get(cacheKey);
        }

        const response = await fetch("http://localhost:3000/summarize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: chunk,
            length:
              selectedDetailLevel === "detailed"
                ? "long"
                : selectedDetailLevel === "medium"
                ? "medium"
                : "short",
            format: "paragraph",
            model: "summarize-xlarge",
            prompt: PROMPTS[selectedDetailLevel],
            temperature: 0.7,
            max_tokens:
              selectedDetailLevel === "detailed"
                ? 2200
                : selectedDetailLevel === "medium"
                ? 180
                : 60,
          }),
        });

        if (!response.ok) {
          if (response.status === 408) {
            throw new Error(
              "Zaman aşımı: API yanıt vermedi. Lütfen tekrar deneyin."
            );
          }
          throw new Error(`API hatası: ${response.status}`);
        }

        const data = await response.json();
        if (!data.summary?.trim()) throw new Error("Boş özet");

        state.cache.set(cacheKey, data.summary);
        return data.summary;
      });

      const chunkResults = await Promise.all(chunkPromises);
      summaries.push(...chunkResults);
      updateProgress(((i + chunkGroup.length) / chunks.length) * 100);
    }

    const finalSummary = summaries.join("\n\n").trim();
    output.value = finalSummary;
    state.processedSummaries.set(summaryKey, finalSummary);
    state.lastError = null;
  } catch (error) {
    if (handleError(error, output)) {
      setTimeout(summarizeText, 2000);
      return;
    }
  } finally {
    state.isProcessing = false;
    button.disabled = false;
    button.innerHTML = `<i class="fas fa-magic me-2"></i>${
      selectedDetailLevel === "detailed"
        ? "Ayrıntılı"
        : selectedDetailLevel === "medium"
        ? "Orta"
        : "Yüzeysel"
    } Özetle`;
    setTimeout(() => updateProgress(0), 1000);
  }
}

// PDF dönüştürme
async function convertPDF() {
  if (state.isProcessing) return;

  const fileInput = document.getElementById("pdfFile");
  const file = fileInput.files[0];

  if (!file) {
    alert("Lütfen bir PDF dosyası seçin.");
    return;
  }

  if (file.type !== "application/pdf") {
    alert("Lütfen geçerli bir PDF dosyası seçin.");
    return;
  }

  try {
    state.isProcessing = true;
    updateProgress(0);

    // PDF dosyasını oku
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let text = "";
    const totalPages = pdf.numPages;

    // Her sayfayı işle
    for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
      const page = await pdf.getPage(pageNum);
      const textContent = await page.getTextContent();

      // Sayfa metnini birleştir
      const pageText = textContent.items
        .map((item) => item.str)
        .join(" ")
        .replace(/\s+/g, " ")
        .trim();

      text += pageText + "\n\n";
      updateProgress((pageNum / totalPages) * 100);
    }

    // Metni text area'ya yerleştir
    const inputText = document.getElementById("inputText");
    inputText.value = text.trim();

    // Başarı mesajı
    const successMessage = `PDF başarıyla dönüştürüldü! (${totalPages} sayfa)`;
    alert(successMessage);
  } catch (error) {
    console.error("PDF dönüştürme hatası:", error);
    alert("PDF dönüştürülürken bir hata oluştu: " + error.message);
  } finally {
    state.isProcessing = false;
    fileInput.value = ""; // Dosya seçimini sıfırla
    setTimeout(() => updateProgress(0), 1000);
  }
}

// Yardımcı fonksiyonlar
function clearInput() {
  document.getElementById("inputText").value = "";
  document.getElementById("outputText").value = "";
  document.getElementById("keywordInput").value = "";
  updateProgress(0);
  state.cache.clear();
  state.processedSummaries.clear();
  state.textChunks.clear();
  state.lastProcessedText = null;
  state.lastError = null;
  state.retryCount = 0;
}

function copyOutput() {
  const output = document.getElementById("outputText");
  output.select();
  document.execCommand("copy");

  const button = document.querySelector('[onclick="copyOutput()"]');
  const icon = button.innerHTML;
  button.innerHTML = '<i class="fas fa-check"></i>';
  setTimeout(() => (button.innerHTML = icon), 2000);
}

// Kelimeye göre özetleme
async function summarizeByKeyword() {
  if (state.isProcessing) return;

  const input = document.getElementById("inputText");
  const output = document.getElementById("outputText");
  const keywordInput = document.getElementById("keywordInput");
  const button = document.querySelector(
    'button[onclick="summarizeByKeyword()"]'
  );

  const text = input.value;
  const keyword = keywordInput.value;

  if (!text?.trim()) {
    alert("Lütfen metin girin.");
    return;
  }

  if (!keyword?.trim()) {
    alert("Lütfen bir anahtar kelime girin.");
    return;
  }

  try {
    state.isProcessing = true;
    state.retryCount = 0;
    button.disabled = true;
    button.innerHTML =
      '<i class="fas fa-spinner fa-spin me-2"></i>Özetleniyor...';
    output.value = "Özetleniyor...";
    updateProgress(0);

    const response = await fetch("http://localhost:3000/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: text,
        length: "medium",
        format: "paragraph",
        model: "summarize-xlarge",
        prompt: `Analyze the following text with a specific focus on the keyword "${keyword}". Create a targeted summary that:
1. Emphasizes all information directly related to "${keyword}"
2. Includes relevant context and examples about "${keyword}"
3. Highlights the most important aspects and implications regarding "${keyword}"
4. Maintains a clear connection between different mentions of "${keyword}"

The summary should be 2-3 paragraphs long. Use clear and accessible language while maintaining technical accuracy. If the keyword appears multiple times, show how these instances are connected.`,
        temperature: 0.7,
        max_tokens: 300,
      }),
    });

    if (!response.ok) {
      if (response.status === 408) {
        throw new Error(
          "Zaman aşımı: API yanıt vermedi. Lütfen tekrar deneyin."
        );
      }
      throw new Error(`API hatası: ${response.status}`);
    }

    const data = await response.json();
    if (!data.summary?.trim()) throw new Error("Boş özet");

    const finalSummary = data.summary.trim();
    output.value = finalSummary;
    state.processedSummaries.set(text + keyword, finalSummary);
    state.lastError = null;
  } catch (error) {
    if (error.name === "AbortError") {
      output.value = "İstek zaman aşımına uğradı. Lütfen tekrar deneyin.";
    } else if (handleError(error, output)) {
      setTimeout(summarizeByKeyword, 2000);
      return;
    }
  } finally {
    state.isProcessing = false;
    button.disabled = false;
    button.innerHTML = '<i class="fas fa-search me-2"></i>Özetle';
    setTimeout(() => updateProgress(0), 1000);
  }
}

// Sayfa yüklendiğinde
document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".btn-group .btn");

  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      buttons.forEach((btn) => {
        btn.classList.remove("active", "btn-primary");
        btn.classList.add("btn-outline-primary");
      });

      this.classList.add("active", "btn-primary");
      this.classList.remove("btn-outline-primary");
      selectedDetailLevel = this.getAttribute("data-level");

      const summarizeBtn = document.querySelector(
        'button[onclick="summarizeText()"]'
      );
      if (summarizeBtn) {
        summarizeBtn.innerHTML = `<i class="fas fa-magic me-2"></i>${this.textContent.trim()} Özetle`;
      }
    });
  });

  selectedDetailLevel = null;
  state.cache.clear();
});

// Header scroll efekti
function handleHeaderScroll() {
  const header = document.querySelector(".header");
  const scrollPosition = window.scrollY;

  if (scrollPosition > 50) {
    header.classList.add("header-scrolled");
  } else {
    header.classList.remove("header-scrolled");
  }
}

// Scroll event listener
window.addEventListener("scroll", handleHeaderScroll);
window.addEventListener("load", handleHeaderScroll);
