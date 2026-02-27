:root {
  color-scheme: light;
  --bg: #f4f7fb;
  --card: #ffffff;
  --text: #1f2937;
  --muted: #6b7280;
  --primary: #2563eb;
  --primary-soft: #dbeafe;
  --border: #e5e7eb;
  --success: #047857;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  color: var(--text);
  background: var(--bg);
}

.container {
  max-width: 980px;
  margin: 0 auto;
  padding: 1.25rem;
}

header {
  margin-bottom: 1rem;
}

h1,
h2 {
  margin: 0 0 0.5rem;
}

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.85rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-weight: 600;
  font-size: 0.92rem;
}

input,
select,
button {
  font: inherit;
}

input,
select {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.52rem 0.65rem;
}

button {
  margin-top: 0.9rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 10px;
  padding: 0.65rem 0.9rem;
  font-weight: 700;
  cursor: pointer;
}

.hint {
  color: var(--muted);
  font-size: 0.88rem;
  margin: 0.8rem 0 0;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

#daily-total {
  color: var(--success);
  font-size: 1.25rem;
}

.entries {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.8rem;
}

.entry {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.6rem;
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 0.75rem;
  align-items: center;
}

.entry img {
  width: 90px;
  height: 90px;
  object-fit: cover;
  border-radius: 10px;
}

.entry-meta {
  display: grid;
  gap: 0.2rem;
  font-size: 0.9rem;
}

.entry-meta strong {
  font-size: 0.98rem;
}

#chart {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
}
