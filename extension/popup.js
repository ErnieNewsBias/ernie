document.getElementById("analyzeBtn").addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = tab.url;
  
    document.getElementById("analyzeBtn").innerText = "Analyzing...";
  
    try {
      const encodedURL = encodeURIComponent(url);
      const response = await fetch(`http://127.0.0.1:5000/scrape?url=${encodedURL}`);
  
      const data = await response.json();
      const analysis = data.analysis;
  
      document.getElementById("result").classList.remove("hidden");
  
      const score = analysis.bias;
      const percent = (score + 10) * 5;
      const fill = document.getElementById("meterFill");
      fill.style.width = `${percent}%`;
      fill.style.backgroundColor = score > 0 ? "#cc0000" : score < 0 ? "#0000cc" : "#888888";
      document.getElementById("biasLabel").innerText = `Score: ${score}`;
  
      const tabContent = document.getElementById("tabContent");
      const tabs = document.querySelectorAll(".tab");
  
      tabs.forEach(tab => {
        tab.addEventListener("click", () => {
          tabs.forEach(t => t.classList.remove("active"));
          tab.classList.add("active");
  
          const type = tab.dataset.tab;
          if (type === "notes") {
            tabContent.innerText = analysis.ai_notes || "No notes available.";
          } else {
            const quotes = analysis.bias_quotes
              ? analysis.bias_quotes.split("\n").map(q => `<p>"${q}"</p>`).join("")
              : "No biased quotes found.";
            tabContent.innerHTML = quotes;
          }
        });
      });
  
      tabs[0].click();
  
    } catch (err) {
      alert("Failed to analyze page.");
      console.error(err);
    } finally {
      document.getElementById("analyzeBtn").innerText = "Analyze Page";
    }
  });
  