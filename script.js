const STORAGE_KEY = 'calorie_journal_entries_v1';
const DEFAULT_CALORIES = {
  plat: 550,
  boisson: 120,
};

const form = document.getElementById('entry-form');
const photoInput = document.getElementById('photo');
const dateInput = document.getElementById('entry-date');
const typeInput = document.getElementById('type');
const nameInput = document.getElementById('name');
const quantityInput = document.getElementById('quantity');
const caloriesInput = document.getElementById('calories');
const selectedDateInput = document.getElementById('selected-date');
const dailyTotalEl = document.getElementById('daily-total');
const entriesEl = document.getElementById('entries');
const chartEl = document.getElementById('chart');

const today = new Date().toISOString().split('T')[0];
dateInput.value = today;
selectedDateInput.value = today;

let entries = loadEntries();
render();

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  if (!photoInput.files || !photoInput.files[0]) {
    return;
  }

  const file = photoInput.files[0];
  const imageDataUrl = await fileToDataUrl(file);

  const type = typeInput.value;
  const quantity = Number(quantityInput.value);
  const customCalories = Number(caloriesInput.value);
  const caloriesPerPortion =
    Number.isFinite(customCalories) && customCalories > 0
      ? customCalories
      : DEFAULT_CALORIES[type];

  const totalCalories = Math.round(caloriesPerPortion * quantity);

  const entry = {
    id: crypto.randomUUID(),
    date: dateInput.value,
    type,
    name: nameInput.value.trim() || `${capitalize(type)} sans nom`,
    quantity,
    caloriesPerPortion,
    totalCalories,
    imageDataUrl,
    createdAt: new Date().toISOString(),
  };

  entries.push(entry);
  saveEntries(entries);

  form.reset();
  dateInput.value = today;
  selectedDateInput.value = entry.date;
  render();
});

selectedDateInput.addEventListener('change', updateDailyTotal);

function loadEntries() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (error) {
    console.error('Impossible de lire le stockage local', error);
    return [];
  }
}

function saveEntries(nextEntries) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(nextEntries));
}

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function updateDailyTotal() {
  const selectedDate = selectedDateInput.value;
  const total = entries
    .filter((entry) => entry.date === selectedDate)
    .reduce((sum, entry) => sum + entry.totalCalories, 0);
  dailyTotalEl.textContent = `${total} kcal`;
}

function renderEntries() {
  entriesEl.innerHTML = '';

  const sorted = [...entries].sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  for (const entry of sorted) {
    const item = document.createElement('li');
    item.className = 'entry';
    item.innerHTML = `
      <img src="${entry.imageDataUrl}" alt="${entry.name}" />
      <div class="entry-meta">
        <strong>${entry.name}</strong>
        <span>${entry.date} • ${capitalize(entry.type)}</span>
        <span>Quantité: ${entry.quantity}</span>
        <span>${entry.caloriesPerPortion} kcal / portion</span>
        <strong>Total: ${entry.totalCalories} kcal</strong>
      </div>
    `;
    entriesEl.appendChild(item);
  }
}

function renderChart() {
  const totalsByDate = entries.reduce((acc, entry) => {
    acc[entry.date] = (acc[entry.date] || 0) + entry.totalCalories;
    return acc;
  }, {});

  const dates = Object.keys(totalsByDate).sort();
  const values = dates.map((date) => totalsByDate[date]);

  const width = 860;
  const height = 280;
  const padding = { top: 18, right: 20, bottom: 45, left: 45 };

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const maxValue = Math.max(...values, 100);

  const bars = dates
    .map((date, index) => {
      const value = totalsByDate[date];
      const barWidth = chartWidth / Math.max(dates.length, 1) - 18;
      const x = padding.left + index * (chartWidth / Math.max(dates.length, 1)) + 9;
      const barHeight = (value / maxValue) * (chartHeight - 10);
      const y = padding.top + chartHeight - barHeight;

      return `
        <rect x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" fill="#2563eb" rx="6"></rect>
        <text x="${x + barWidth / 2}" y="${y - 6}" text-anchor="middle" font-size="11" fill="#1f2937">${value}</text>
        <text x="${x + barWidth / 2}" y="${height - 16}" text-anchor="middle" font-size="11" fill="#6b7280">${formatDate(date)}</text>
      `;
    })
    .join('');

  const yTicks = [0, 0.25, 0.5, 0.75, 1]
    .map((ratio) => {
      const value = Math.round(maxValue * ratio);
      const y = padding.top + chartHeight - ratio * chartHeight;
      return `
        <line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="#e5e7eb" />
        <text x="${padding.left - 8}" y="${y + 4}" text-anchor="end" font-size="11" fill="#6b7280">${value}</text>
      `;
    })
    .join('');

  const empty =
    dates.length === 0
      ? `<text x="${width / 2}" y="${height / 2}" text-anchor="middle" fill="#6b7280">Ajoute des entrées pour afficher le graphique.</text>`
      : '';

  chartEl.innerHTML = `
    <rect x="0" y="0" width="${width}" height="${height}" fill="transparent"></rect>
    ${yTicks}
    <line x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${width - padding.right}" y2="${padding.top + chartHeight}" stroke="#9ca3af" />
    ${bars}
    ${empty}
  `;
}

function formatDate(date) {
  const [year, month, day] = date.split('-');
  return `${day}/${month}`;
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function render() {
  renderEntries();
  updateDailyTotal();
  renderChart();
}
