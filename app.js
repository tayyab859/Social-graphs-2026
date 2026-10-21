const DATA_BASE = "../../data/";
const state = { characters: [], byName: new Map(), scale: "linear", selected: null };

function parseTSV(text, hasHeader = true) {
  const rows = text.split(/\r?\n/).filter(line => line.trim() && !line.startsWith("#"));
  if (!rows.length) return [];
  if (!hasHeader) return rows.map(line => line.split("\t"));
  const headers = rows.shift().split("\t");
  return rows.map(line => {
    const fields = line.split("\t");
    return Object.fromEntries(headers.map((header, index) => [header, fields[index] || ""]));
  });
}

function classify(character) {
  const difference = character.inDegree - character.outDegree;
  if (difference >= 4) return "magnet";
  if (difference <= -4) return "broadcaster";
  return "balanced";
}

function typeLabel(character) {
  const type = classify(character);
  return type === "magnet" ? "Attention magnet" : type === "broadcaster" ? "Broadcaster" : "Balanced linker";
}

async function loadData() {
  const status = document.getElementById("plot-status");
  try {
    const [nodeResponse, edgeResponse] = await Promise.all([
      fetch(`${DATA_BASE}week1_nodes.tsv`),
      fetch(`${DATA_BASE}week1_edges.tsv`)
    ]);
    if (!nodeResponse.ok || !edgeResponse.ok) throw new Error("The course data could not be downloaded.");

    const nodes = parseTSV(await nodeResponse.text());
    const edgeRows = parseTSV(await edgeResponse.text(), false);
    const edgeSet = new Set(edgeRows.map(([source, target]) => `${source}\u0000${target}`));
    const byId = new Map(nodes.map(node => [node.node_id, { ...node, incoming: new Set(), outgoing: new Set() }]));

    edgeRows.forEach(([source, target]) => {
      byId.get(source)?.outgoing.add(target);
      byId.get(target)?.incoming.add(source);
    });

    state.characters = [...byId.values()].map(character => {
      const mutual = [...character.outgoing].filter(id => character.incoming.has(id));
      return {
        ...character,
        inDegree: character.incoming.size,
        outDegree: character.outgoing.size,
        mutual,
        incomingOnly: [...character.incoming].filter(id => !character.outgoing.has(id)),
        outgoingOnly: [...character.outgoing].filter(id => !character.incoming.has(id))
      };
    });
    state.byName = new Map(state.characters.map(character => [character.name.toLowerCase(), character]));
    state.byId = byId;

    const mutualPairs = [...edgeSet].filter(key => {
      const [source, target] = key.split("\u0000");
      return edgeSet.has(`${target}\u0000${source}`);
    }).length / 2;

    updateMetrics(nodes.length, edgeRows.length, mutualPairs);
    populateSearch();
    drawScatter();
    drawRankings();
    validate(nodes.length, edgeRows.length, mutualPairs);
    selectCharacter(state.byName.get("spider-man"));
    status.hidden = true;
  } catch (error) {
    status.textContent = `${error.message} Please reload the page.`;
    status.classList.add("error");
  }
}

function updateMetrics(nodes, edges, mutualPairs) {
  document.getElementById("metric-nodes").textContent = nodes.toLocaleString();
  document.getElementById("metric-edges").textContent = edges.toLocaleString();
  document.getElementById("metric-mutual").textContent = mutualPairs.toLocaleString();
  document.getElementById("metric-reciprocity").textContent = `${(mutualPairs * 2 / edges * 100).toFixed(1)}%`;
}

function validate(nodes, edges, mutualPairs) {
  const checks = [
    ["check-nodes", nodes === 303, `${nodes} found · expected 303`],
    ["check-edges", edges === 1784, `${edges.toLocaleString()} found · expected 1,784`],
    ["check-pairs", mutualPairs === 350, `${mutualPairs} mutual pairs · 700 reciprocal arrows`]
  ];
  checks.forEach(([id, pass, text]) => {
    const element = document.getElementById(id);
    element.textContent = `${pass ? "✓" : "!"} ${text}`;
    element.className = pass ? "pass" : "fail";
  });
}

function populateSearch() {
  document.getElementById("character-options").innerHTML = state.characters
    .slice()
    .sort((a, b) => a.name.localeCompare(b.name))
    .map(character => `<option value="${escapeHTML(character.name)}"></option>`)
    .join("");
}

function escapeHTML(value) {
  return String(value).replace(/[&<>"]/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[character]));
}

function selectCharacter(character) {
  if (!character) return;
  state.selected = character;
  document.getElementById("character-search").value = character.name;
  document.getElementById("character-empty").hidden = true;
  document.getElementById("character-detail").hidden = false;
  document.getElementById("character-type").textContent = typeLabel(character);
  document.getElementById("character-name").textContent = character.name;
  document.getElementById("character-wiki").href = character.url;
  document.getElementById("char-in").textContent = character.inDegree;
  document.getElementById("char-out").textContent = character.outDegree;
  document.getElementById("char-mutual").textContent = character.mutual.length;
  setList("mutual", character.mutual);
  setList("incoming", character.incomingOnly);
  setList("outgoing", character.outgoingOnly);
  document.querySelectorAll(".plot-dot").forEach(dot => dot.classList.toggle("selected", dot.dataset.id === character.node_id));
}

function setList(kind, ids) {
  const names = ids.map(id => state.byId.get(id)?.name || id).sort((a, b) => a.localeCompare(b));
  document.getElementById(`count-${kind}`).textContent = names.length;
  document.getElementById(`list-${kind}`).textContent = names.length ? names.join(" · ") : "None";
}

function drawScatter() {
  const svg = document.getElementById("scatter");
  const width = 760, height = 520;
  const margin = { top: 26, right: 24, bottom: 64, left: 70 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;
  const transform = value => state.scale === "log" ? Math.log10(value + 1) : value;
  const maxX = Math.max(...state.characters.map(character => transform(character.outDegree)));
  const maxY = Math.max(...state.characters.map(character => transform(character.inDegree)));
  const x = value => margin.left + transform(value) / maxX * innerWidth;
  const y = value => margin.top + innerHeight - transform(value) / maxY * innerHeight;
  const ticksX = state.scale === "log" ? [0, 1, 3, 9, 19] : [0, 7, 14, 21, 28];
  const ticksY = state.scale === "log" ? [0, 1, 3, 9, 31, 99] : [0, 25, 50, 75, 100];

  svg.innerHTML = `
    ${ticksY.map(value => `<line class="grid-line" x1="${margin.left}" x2="${width-margin.right}" y1="${y(value)}" y2="${y(value)}"></line><text class="tick-label" x="${margin.left-12}" y="${y(value)+4}" text-anchor="end">${state.scale === "log" ? value+1 : value}</text>`).join("")}
    ${ticksX.map(value => `<line class="grid-line" x1="${x(value)}" x2="${x(value)}" y1="${margin.top}" y2="${height-margin.bottom}"></line><text class="tick-label" x="${x(value)}" y="${height-margin.bottom+23}" text-anchor="middle">${state.scale === "log" ? value+1 : value}</text>`).join("")}
    <line class="axis-line" x1="${margin.left}" x2="${width-margin.right}" y1="${height-margin.bottom}" y2="${height-margin.bottom}"></line>
    <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height-margin.bottom}"></line>
    <text class="axis-label" x="${margin.left + innerWidth/2}" y="${height-15}" text-anchor="middle">${state.scale === "log" ? "out-degree (k + 1)" : "out-degree"}</text>
    <text class="axis-label" transform="translate(17 ${margin.top + innerHeight/2}) rotate(-90)" text-anchor="middle">${state.scale === "log" ? "in-degree (k + 1)" : "in-degree"}</text>
    ${state.characters.map(character => `<circle class="plot-dot ${classify(character)}" data-id="${escapeHTML(character.node_id)}" cx="${x(character.outDegree)}" cy="${y(character.inDegree)}" r="4" fill="${classify(character) === "magnet" ? "#ff8a5b" : classify(character) === "broadcaster" ? "#41d9d0" : "#a996ff"}" opacity=".72"></circle>`).join("")}
  `;

  svg.querySelectorAll(".plot-dot").forEach(dot => {
    const character = state.characters.find(item => item.node_id === dot.dataset.id);
    dot.addEventListener("click", () => selectCharacter(character));
    dot.addEventListener("mouseenter", event => showTooltip(event, character));
    dot.addEventListener("mousemove", moveTooltip);
    dot.addEventListener("mouseleave", hideTooltip);
  });
  document.getElementById("axis-note").textContent = state.scale === "log"
    ? "Log–log view plots k + 1 on both axes so zero-degree characters remain visible."
    : "Linear axes show the original degree values.";
}

function showTooltip(event, character) {
  const tooltip = document.getElementById("tooltip");
  tooltip.innerHTML = `<strong>${escapeHTML(character.name)}</strong><br>in ${character.inDegree} · out ${character.outDegree} · mutual ${character.mutual.length}`;
  tooltip.hidden = false;
  moveTooltip(event);
}
function moveTooltip(event) {
  const tooltip = document.getElementById("tooltip");
  tooltip.style.left = `${Math.min(event.clientX + 14, window.innerWidth - 210)}px`;
  tooltip.style.top = `${event.clientY + 14}px`;
}
function hideTooltip() { document.getElementById("tooltip").hidden = true; }

function drawRankings() {
  const attention = state.characters.slice().sort((a, b) => b.incomingOnly.length - a.incomingOnly.length).slice(0, 7);
  const broadcast = state.characters.slice().sort((a, b) => b.outgoingOnly.length - a.outgoingOnly.length).slice(0, 7);
  renderBars("attention-bars", attention, character => character.incomingOnly.length, "attention");
  renderBars("broadcast-bars", broadcast, character => character.outgoingOnly.length, "broadcast");
}

function renderBars(id, rows, getValue, kind) {
  const max = Math.max(...rows.map(getValue));
  document.getElementById(id).innerHTML = rows.map(character => `
    <button class="bar-row ${kind}" type="button" data-name="${escapeHTML(character.name)}" title="Inspect ${escapeHTML(character.name)}">
      <span class="bar-label">${escapeHTML(character.name.replace(/ \(.*\)$/, ""))}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${getValue(character)/max*100}%"></span></span>
      <span class="bar-value">${getValue(character)}</span>
    </button>`).join("");
  document.querySelectorAll(`#${id} .bar-row`).forEach(button => {
    button.addEventListener("click", () => {
      selectCharacter(state.byName.get(button.dataset.name.toLowerCase()));
      document.getElementById("explorer").scrollIntoView({ behavior: "smooth" });
    });
  });
}

document.querySelectorAll("[data-scale]").forEach(button => {
  button.addEventListener("click", () => {
    state.scale = button.dataset.scale;
    document.querySelectorAll("[data-scale]").forEach(item => item.classList.toggle("active", item === button));
    drawScatter();
    if (state.selected) selectCharacter(state.selected);
  });
});

document.getElementById("character-search").addEventListener("change", event => {
  selectCharacter(state.byName.get(event.target.value.trim().toLowerCase()));
});

loadData();
