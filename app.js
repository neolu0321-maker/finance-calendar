document.addEventListener("DOMContentLoaded", () => {
  initApp();
});

function initApp() {
  // 這裡先寫入測試用的乾淨資料，確認 App 能正常運作
  // 未來我們會將這裡改成讀取 GitHub Actions 自動生成的 JSON 檔案
  const mockData = {
    quotes: [{ text: "風險來自於你不知道自己在做什麼。", author: "華倫·巴菲特" }],
    financeEvents: [
      { title: "美國 CPI 消費者物價指數", date: "2026-08-10", impact: "高", market: "全球" },
      { title: "台灣央行理監事會", date: "2026-09-19", impact: "高", market: "台股" }
    ],
    activities: [
      { title: "ETF 投資入門講座", city: "台北", price: "免費", time: "8/26 19:00" },
      { title: "城市閱讀與生活講座", city: "高雄", price: "免費", time: "8/28 14:00" }
    ]
  };

  renderData(mockData);
}

function renderData(data) {
  // 1. 渲染金句
  document.getElementById('todayQuoteText').innerText = `${data.quotes[0].text} \n— ${data.quotes[0].author}`;
  
  // 2. 渲染金融事件
  const financeHtml = data.financeEvents.map(e => `
    <div class="item">
      <span class="pill pill-red">${e.impact}</span>
      <span class="pill pill-gold">${e.market}</span>
      <strong>${e.title}</strong>
      <div style="font-size:12px; color:#666; margin-top:4px;">日期：${e.date}</div>
    </div>
  `).join('');
  document.getElementById('financeList').innerHTML = financeHtml;
  document.getElementById('todayFinanceList').innerHTML = financeHtml; // 示範：今日事件同步顯示
  
  // 3. 渲染活動
  const activityHtml = data.activities.map(a => `
    <div class="item">
      <span class="pill pill-gold">${a.city}</span>
      <strong>${a.title}</strong>
      <div style="font-size:12px; color:#666; margin-top:4px;">時間：${a.time} | 費用：${a.price}</div>
    </div>
  `).join('');
  document.getElementById('activityList').innerHTML = activityHtml;

  // 4. 更新頂部數量
  document.getElementById('financeCount').innerText = data.financeEvents.length;
  document.getElementById('activityCount').innerText = data.activities.length;
}

// 底部導覽列切換邏輯
window.showPage = function(pageId) {
  document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
  
  document.getElementById(`page-${pageId}`).classList.add('active');
  document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
}
