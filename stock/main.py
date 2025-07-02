from flask import Flask, Response, jsonify
import requests

app = Flask(__name__)

API_URL = "https://gagapi.onrender.com/alldata"

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Grow a Garden - Live Stock Viewer</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; }
  </style>
</head>
<body class="bg-gradient-to-tr from-purple-950 to-purple-900 text-white min-h-screen">
  <header class="py-10 text-center">
    <h1 class="text-4xl sm:text-5xl font-extrabold text-purple-200 drop-shadow-xl">🌱 Grow a Garden</h1>
    <p class="text-purple-400 text-lg mt-2">Live Stock & Weather Overview</p>
  </header>

  <div class="max-w-7xl mx-auto px-6">
    <div class="flex justify-center mb-10">
      <button onclick="fetchAndRender()" class="bg-purple-700 hover:bg-purple-800 text-white font-semibold px-6 py-2 rounded-lg shadow-lg transition">
        🔄 Refresh Data
      </button>
    </div>

    <div class="grid md:grid-cols-2 gap-8 mb-12">
      <section id="weather" class="rounded-xl p-6 bg-purple-800/50 border border-purple-700 shadow-xl backdrop-blur-lg"></section>

      <section>
        <h2 class="text-2xl font-bold text-center text-purple-200 mb-4">🍯 Honey</h2>
        <div id="honey" class="grid grid-cols-2 sm:grid-cols-3 gap-4"></div>
      </section>
    </div>

    <div class="grid md:grid-cols-2 gap-10">
      <section>
        <h2 class="text-2xl font-bold text-center text-purple-200 mb-4">🧰 Gear</h2>
        <div id="gear" class="grid grid-cols-2 sm:grid-cols-3 gap-4"></div>
      </section>

      <section>
        <h2 class="text-2xl font-bold text-center text-purple-200 mb-4">🌱 Seeds</h2>
        <div id="seeds" class="grid grid-cols-2 sm:grid-cols-3 gap-4"></div>
      </section>

      <section>
        <h2 class="text-2xl font-bold text-center text-purple-200 mb-4">🥚 Eggs</h2>
        <div id="eggs" class="grid grid-cols-2 sm:grid-cols-3 gap-4"></div>
      </section>

      <section>
        <h2 class="text-2xl font-bold text-center text-purple-200 mb-4">🎨 Cosmetics</h2>
        <div id="cosmetics" class="grid grid-cols-2 sm:grid-cols-3 gap-4"></div>
      </section>
    </div>
  </div>

  <script>
    // Now fetch from our Flask server proxy route
    const API_BASE = '';

    function slugify(name) {
      return name.toLowerCase().replace(/ /g, '_');
    }

    async function fetchAndRender() {
      try {
        const res = await fetch(`${API_BASE}/api/alldata`);
        if (!res.ok) throw new Error('API fetch failed');
        const data = await res.json();

        renderCategory('honey', data.honey);
        renderCategory('gear', data.gear);
        renderCategory('seeds', data.seeds);
        renderCategory('eggs', data.eggs);
        renderCategory('cosmetics', data.cosmetics);
        renderWeather(data.weather);
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
        div.className = 'bg-purple-800/40 backdrop-blur p-4 rounded-xl shadow-lg flex flex-col items-center hover:scale-105 transition transform';
        div.innerHTML = `
          <img src="${imgUrl}" alt="${item.name}" class="w-16 h-16 object-contain mb-2 rounded-md" loading="lazy" />
          <p class="text-white font-medium text-center text-sm">${item.name}</p>
          <p class="text-green-300 font-bold text-lg mt-1">x${item.quantity}</p>
        `;
        container.appendChild(div);
      });
    }

    function renderWeather(w) {
      const weatherEl = document.getElementById('weather');
      const type = w?.type || 'Unknown';
      const active = w?.active ? 'Yes' : 'No';
      const effects = (w?.effects || []).join(', ') || 'None';
      const lastUpdated = w?.lastUpdated ? new Date(w.lastUpdated).toLocaleString() : 'Unknown';

      weatherEl.innerHTML = `
        <h2 class="text-2xl font-bold text-center text-purple-200 mb-4">🌦️ Current Weather</h2>
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
      setInterval(fetchAndRender, 15000); // Auto-refresh every 15 seconds
    }
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return Response(HTML_CONTENT, mimetype='text/html')

@app.route('/api/alldata')
def proxy_alldata():
    try:
        resp = requests.get(API_URL, timeout=5)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": "Failed to fetch data from external API", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
