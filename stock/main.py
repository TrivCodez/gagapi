from flask import Flask, Response

app = Flask(__name__)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en" >
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Grow a Garden - Live Stock Viewer</title>

  <!-- Tailwind CDN -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- Google Fonts: Inter -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">

  <style>
    body {
      font-family: 'Inter', sans-serif;
      background-color: #f0fdf4;
      margin: 0;
      min-height: 100vh;
    }
    /* Card hover effect */
    .stock-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 20px rgba(72, 187, 120, 0.25);
    }
    .stock-card {
      transition: all 0.3s ease;
    }
  </style>

  <script>
    const API_BASE = 'http://';

    function slugify(name) {
      return name.toLowerCase().replace(/ /g, '_');
    }

    async function fetchAndRender() {
      try {
        const res = await fetch(`${API_BASE}/alldata`);
        if (!res.ok) throw new Error('API fetch failed');
        const data = await res.json();

        const categories = ['gear', 'seeds', 'eggs', 'cosmetics', 'honey'];
        categories.forEach(cat => {
          const container = document.getElementById(cat);
          container.innerHTML = '';
          const items = data[cat] || [];
          if (items.length === 0) {
            container.innerHTML = '<p class="italic text-gray-400 text-center w-full">No data</p>';
            return;
          }
          items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'stock-card bg-white rounded-lg p-4 flex flex-col items-center shadow-md';

            const imgSlug = slugify(item.name);
            const imgUrl = `https://api.joshlei.com/v2/growagarden/image/${imgSlug}`;

            div.innerHTML = `
              <img src="${imgUrl}" alt="${item.name}" class="w-20 h-20 object-contain mb-3 rounded-md" loading="lazy" />
              <p class="text-gray-800 font-semibold text-center">${item.name}</p>
              <p class="text-green-600 font-bold text-xl mt-1">${item.quantity}</p>
            `;
            container.appendChild(div);
          });
        });

        // Weather card
        const weatherEl = document.getElementById('weather');
        const w = data.weather || {};
        const type = w.type || 'Unknown';
        const active = w.active ? 'Yes' : 'No';
        const effects = (w.effects && w.effects.length > 0) ? w.effects.join(', ') : 'None';
        const lastUpdated = w.lastUpdated ? new Date(w.lastUpdated).toLocaleString() : 'Unknown';

        weatherEl.innerHTML = `
          <h3 class="text-xl font-semibold mb-2 text-green-700">Weather</h3>
          <div class="text-gray-700 text-center space-y-1">
            <p><strong>Type:</strong> ${type}</p>
            <p><strong>Active:</strong> ${active}</p>
            <p><strong>Effects:</strong> ${effects}</p>
            <p class="text-sm text-gray-500"><em>Last Updated: ${lastUpdated}</em></p>
          </div>
        `;

      } catch (e) {
        console.error(e);
        alert('Failed to fetch data from API.');
      }
    }

    window.onload = fetchAndRender;
  </script>
</head>
<body class="p-6">
  <h1 class="text-4xl font-extrabold text-green-700 mb-8 text-center">Grow a Garden - Live Stock Viewer</h1>

  <div class="flex justify-center mb-8">
    <button id="refreshBtn" onclick="fetchAndRender()" class="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-6 rounded shadow">
      🔄 Refresh Now
    </button>
  </div>

  <main class="max-w-7xl mx-auto grid gap-8 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">

    <section>
      <h2 class="text-2xl font-bold text-green-700 mb-4 text-center">Gear</h2>
      <div id="gear" class="grid grid-cols-2 gap-4"></div>
    </section>

    <section>
      <h2 class="text-2xl font-bold text-green-700 mb-4 text-center">Seeds</h2>
      <div id="seeds" class="grid grid-cols-2 gap-4"></div>
    </section>

    <section>
      <h2 class="text-2xl font-bold text-green-700 mb-4 text-center">Eggs</h2>
      <div id="eggs" class="grid grid-cols-2 gap-4"></div>
    </section>

    <section>
      <h2 class="text-2xl font-bold text-green-700 mb-4 text-center">Cosmetics</h2>
      <div id="cosmetics" class="grid grid-cols-2 gap-4"></div>
    </section>

    <section>
      <h2 class="text-2xl font-bold text-green-700 mb-4 text-center">Honey</h2>
      <div id="honey" class="grid grid-cols-2 gap-4"></div>
    </section>

    <section class="col-span-full max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <div id="weather"></div>
    </section>

  </main>
</body>
</html>
"""

@app.route('/')
def index():
    return Response(HTML_CONTENT, mimetype='text/html')


if __name__ == '__main__':
    app.run(port=3000)
