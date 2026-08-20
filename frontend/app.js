const API = "http://localhost:8000/api/v1";

async function getJson(path) {
  const response = await fetch(`${API}${path}`);
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

function renderAudits(audits) {
  document.querySelector("#audit-count").textContent = audits.length;
  document.querySelector("#audits").innerHTML = audits.length ? audits.map((audit) => `
    <div class="event"><div class="event-top"><span class="event-type">${audit.event_type} · ${audit.risk_level}</span><span class="muted">${new Date(audit.timestamp).toLocaleTimeString()}</span></div>
    <p class="event-detail">${audit.train_id}: ${audit.details}</p></div>`).join("") : '<p class="muted">No events recorded.</p>';
}

async function loadDashboard() {
  const [network, fleet, audits] = await Promise.all([getJson("/data/network"), getJson("/data/fleet"), getJson("/audits?limit=8")]);
  const corridor = network.corridors[0];
  document.querySelector("#corridor").textContent = corridor.name;
  document.querySelector("#corridor-meta").textContent = `${corridor.total_length_km} km corridor · maximum ${corridor.max_speed_kmh} km/h`;
  document.querySelector("#fleet-count").textContent = fleet.length;
  document.querySelector("#fleet").innerHTML = fleet.map((train) => `<div class="fleet-item"><span>${train.name}</span><span class="muted">${train.total_mass_tonnes}t</span></div>`).join("");
  renderAudits(audits);
  document.querySelector("#status").textContent = "Safety core online";
  document.querySelector("#status").classList.remove("pending");
}

async function refresh() {
  try { await loadDashboard(); } catch (error) { document.querySelector("#status").textContent = `Backend unavailable: ${error.message}`; document.querySelector("#status").classList.add("pending"); }
}

document.querySelector("#refresh").addEventListener("click", refresh);
refresh();