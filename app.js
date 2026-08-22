document.addEventListener('DOMContentLoaded', () => {
    // 註冊 Service Worker (PWA 功能)
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('./sw.js')
            .then(reg => console.log('SW 註冊成功!'))
            .catch(err => console.log('SW 註冊失敗!', err));
    }

    // 建立分頁切換邏輯
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // 移除所有 active class
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(sec => sec.classList.remove('active'));

            // 加入 active class 到點擊的目標
            item.classList.add('active');
            const targetId = item.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // 啟動遠端資料連線！
    fetchData();
});

// 負責去讀取 data.json 的新功能
async function fetchData() {
    try {
        // 加上時間參數避免手機快取抓到舊資料
        const response = await fetch('data.json?t=' + new Date().getTime());
        const data = await response.json();

        // 1. 更新金句
        if (data.quotes && data.quotes.length > 0) {
            const quoteContent = document.querySelector('#today .card-content');
            quoteContent.innerHTML = `
                <p class="quote-text">${data.quotes[0].text}</p>
                <p class="quote-author">— ${data.quotes[0].author}</p>
            `;
        }

        // 2. 更新重大事件
        if (data.financeEvents) {
            const eventList = document.querySelector('#events .event-list');
            eventList.innerHTML = data.financeEvents.map(event => `
                <div class="event-item">
                    <div class="event-header">
                        <span class="tag tag-high">${event.impact}</span>
                        <span class="tag tag-market">${event.market}</span>
                        <h3>${event.title}</h3>
                    </div>
                    <div class="event-details">
                        <p>日期：${event.date}</p>
                    </div>
                </div>
            `).join('');
            
            // 更新儀表板數字
            document.getElementById('event-count').innerText = data.financeEvents.length;
        }

        // 3. 更新理財活動 (這裡就是過濾完詐騙的乾淨資料！)
        if (data.activities) {
            const activityList = document.querySelector('#activities .event-list');
            activityList.innerHTML = data.activities.map(act => `
                <div class="event-item">
                    <div class="event-header">
                        <span class="tag tag-high">${act.price}</span>
                        <span class="tag tag-market">${act.city}</span>
                        <h3>${act.title}</h3>
                    </div>
                    <div class="event-details">
                        <p>時間：${act.time}</p>
                        <p>主辦：${act.organizer}</p>
                    </div>
                </div>
            `).join('');

            // 更新儀表板數字
            document.getElementById('activity-count').innerText = data.activities.length;
        }

    } catch (error) {
        console.error("載入資料失敗:", error);
    }
}
