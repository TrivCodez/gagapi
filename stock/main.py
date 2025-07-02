from flask import Flask, Response

app = Flask(__name__)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Grow a Garden - Live Stock Viewer</title>

  <!-- Tailwind CDN -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- Google Fonts: Inter -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet" />

  <style>
    body {
      font-family: 'Inter', sans-serif;
    }
    .glass {
      background-color: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 1rem;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    }
  </style>

  <script>
    const API_BASE = 'https://gagapi.onrender.com';
    let previousStock = {};

    function slugify(name) {
      return name.toLowerCase().replace(/ /g, '_');
    }

    function requestNotificationPermission() {
      if (!('Notification' in window)) {
        alert('This browser does not support desktop notifications.');
        return;
      }
      if (Notification.permission === 'granted') {
        alert('Notifications are already enabled!');
        document.getElementById('notifyBtn').disabled = true;
      } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            alert('Notifications enabled! You will get updates.');
            document.getElementById('notifyBtn').disabled = true;
          } else {
            alert('Notifications permission was denied.');
          }
        });
      } else {
        alert('Notifications are blocked. Please enable them in your browser settings.');
      }
    }

    function checkStockChanges(category, newItems) {
      const prevItems = previousStock[category] || [];
      const prevMap = new Map(prevItems.map(i => [i.name, i.quantity]));
      for (const item of newItems) {
        const prevQty = prevMap.get(item.name) || 0;
        if (item.quantity > prevQty) {
          return item;
        }
      }
      return null;
    }

    function playNotificationSound() {
      const audio = document.getElementById('notifSound');
      if (audio) {
        audio.currentTime = 0;
        audio.play().catch(e => {
          // autoplay might be blocked, ignore error
          console.warn('Sound play blocked:', e);
        });
      }
    }

    function notifyStockChange(item, category) {
      if (Notification.permission === 'granted') {
        const notif = new Notification('🌱 Grow a Garden Update', {
          body: `New stock in ${category}: ${item.name} increased to ${item.quantity}!`,
          icon: 'https://api.joshlei.com/v2/growagarden/image/' + slugify(item.name),
        });
        notif.onclick = () => window.focus();
      }
      // Play sound regardless of notification permission
      playNotificationSound();
    }

    async function fetchAndRender() {
      try {
        const res = await fetch(`${API_BASE}/alldata`);
        if (!res.ok) throw new Error('API fetch failed');
        const data = await res.json();

        const categories = ['gear', 'seeds', 'cosmetics', 'eggs'];
        categories.forEach(cat => {
          renderCategory(cat, data[cat]);
          const changedItem = checkStockChanges(cat, data[cat] || []);
          if (changedItem) notifyStockChange(changedItem, cat);
        });

        renderCategory('honey', data.honey);
        const honeyChanged = checkStockChanges('honey', data.honey || []);
        if (honeyChanged) notifyStockChange(honeyChanged, 'honey');

        renderWeather(data.weather);

        previousStock = {};
        ['gear', 'seeds', 'cosmetics', 'eggs', 'honey'].forEach(cat => {
          previousStock[cat] = data[cat] ? JSON.parse(JSON.stringify(data[cat])) : [];
        });

      } catch (e) {
        console.error(e);
        alert('Failed to fetch data from API.');
      }
    }

    function renderCategory(id, items) {
      const container = document.getElementById(id);
      container.innerHTML = '';
      (items || []).forEach(item => {
        const imgSlug = slugify(item.name);
        const imgUrl = `https://api.joshlei.com/v2/growagarden/image/${imgSlug}`;

        const div = document.createElement('div');
        div.className = 'glass p-4 flex flex-col items-center transition-transform transform hover:-translate-y-1 hover:shadow-2xl rounded-xl cursor-default';
        div.innerHTML = `
          <img src="${imgUrl}" alt="${item.name}" class="w-16 h-16 object-contain mb-2 rounded-md" loading="lazy" />
          <p class="text-white font-medium text-center">${item.name}</p>
          <p class="text-green-300 font-bold text-xl mt-1">x${item.quantity}</p>
        `;
        container.appendChild(div);
      });

      if (!items || items.length === 0) {
        container.innerHTML = '<p class="italic text-gray-400 text-center w-full">No data</p>';
      }
    }

    function renderWeather(w) {
      const weatherEl = document.getElementById('weather');
      const type = w?.type || 'Unknown';
      const active = w?.active ? 'Yes' : 'No';
      const effects = (w?.effects || []).join(', ') || 'None';
      const lastUpdated = w?.lastUpdated ? new Date(w.lastUpdated).toLocaleString() : 'Unknown';

      weatherEl.innerHTML = `
        <h2 class="text-2xl font-semibold text-center text-purple-200 mb-4">🌦️ Current Weather</h2>
        <div class="text-center space-y-2 text-purple-100">
          <p><strong>Type:</strong> ${type}</p>
          <p><strong>Active:</strong> ${active}</p>
          <p><strong>Effects:</strong> ${effects}</p>
          <p class="text-xs text-purple-300"><em>Last Updated: ${lastUpdated}</em></p>
        </div>
      `;
    }

    window.onload = () => {
      fetchAndRender();
      setInterval(fetchAndRender, 15000);
    }
  </script>
</head>
<body class="bg-gradient-to-br from-purple-950 to-purple-900 min-h-screen text-white p-6">
  <h1 class="text-4xl font-extrabold text-center text-purple-200 mb-10">🌱 Grow a Garden - Live Stock Viewer</h1>

  <div class="flex justify-center mb-8 space-x-4">
    <button onclick="fetchAndRender()" class="glass px-6 py-2 text-white font-semibold hover:bg-white/20 transition rounded-lg shadow-lg">
      🔄 Refresh Now
    </button>
    <button id="notifyBtn" onclick="requestNotificationPermission()" class="glass px-6 py-2 text-white font-semibold hover:bg-white/20 transition rounded-lg shadow-lg">
      🔔 Notify Me
    </button>
  </div>

  <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
    <section id="weather" class="glass p-6 rounded-xl border border-purple-700 shadow-xl backdrop-blur-lg"></section>

    <section>
      <h2 class="text-2xl font-semibold text-center text-purple-300 mb-6">🍯 Honey</h2>
      <div id="honey" class="grid grid-cols-2 gap-4"></div>
    </section>
  </div>

  <main class="max-w-7xl mx-auto grid gap-8 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">

    <section>
      <h2 class="text-2xl font-semibold text-center text-purple-300 mb-3">Gear</h2>
      <div id="gear" class="grid grid-cols-2 gap-4"></div>
    </section>

    <section>
      <h2 class="text-2xl font-semibold text-center text-purple-300 mb-3">Seeds</h2>
      <div id="seeds" class="grid grid-cols-2 gap-4"></div>
    </section>

    <section>
      <h2 class="text-2xl font-semibold text-center text-purple-300 mb-3">Cosmetics</h2>
      <div id="cosmetics" class="grid grid-cols-2 gap-4"></div>
    </section>

    <section>
      <h2 class="text-2xl font-semibold text-center text-purple-300 mb-3">Eggs</h2>
      <div id="eggs" class="grid grid-cols-2 gap-4"></div>
    </section>

  </main>

  <!-- Notification Sound -->
  <audio id="notifSound" src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" preload="auto"></audio>
</body>
</html>
"""

@app.route('/')
def index():
    return Response(HTML_CONTENT, mimetype='text/html')

if __name__ == '__main__':
    app.run(port=3000, debug=True)
