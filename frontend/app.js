// State
let traces = [];
let selectedRunId = null;
let activeMemTab = 'semantic';

// Mock data for demo
const mockTraces = [
  {
    run_id: "9f3a1c2d-8e4b-4f71-a1b2-c3d4e5f67890",
    agent_name: "research_agent",
    task: "What caused the 2008 financial crisis?",
    plan: [
      { step_id: "s1", description: "Search for background on 2008 financial crisis", status: "success" },
      { step_id: "s2", description: "Read top 3 results and extract key facts", status: "success" },
      { step_id: "s3", description: "Remember key facts to semantic memory", status: "success" },
      { step_id: "s4", description: "Synthesize cited answer", status: "success" }
    ],
    steps: [
      {
        step_id: "s1",
        tool_calls: [{ tool: "web_search", input: { query: "2008 financial crisis causes subprime mortgage" }, output: { results: 8 } }],
        quality_check: { rule_check: "pass", llm_rubric_check: null },
        retries: 0,
        duration_ms: 142
      },
      {
        step_id: "s2",
        tool_calls: [
          { tool: "read_url", input: { url: "https://example.com/crisis-1" }, output: { facts: 4 } },
          { tool: "read_url", input: { url: "https://example.com/crisis-2" }, output: { facts: 5 } },
          { tool: "read_url", input: { url: "https://example.com/crisis-3" }, output: { facts: 3 } }
        ],
        quality_check: { rule_check: "pass", llm_rubric_check: null },
        retries: 0,
        duration_ms: 890
      },
      {
        step_id: "s3",
        tool_calls: [{ tool: "memory_remember", input: { collection: "semantic", entries: 3 }, output: { written: 3 } }],
        quality_check: { rule_check: "pass", llm_rubric_check: null },
        retries: 0,
        duration_ms: 45
      },
      {
        step_id: "s4",
        tool_calls: [{ tool: "llm_generate", input: { prompt: "Synthesize answer...", model: "llama-3.3-70b-versatile" }, output: { text: "The 2008 financial crisis was triggered by a collapse in the subprime mortgage market..." } }],
        quality_check: { rule_check: "pass", llm_rubric_check: "pass" },
        retries: 0,
        duration_ms: 2400
      }
    ],
    final_status: "success",
    started_at: "2026-07-18T13:42:00Z",
    ended_at: "2026-07-18T13:44:14Z",
    memory: {
      semantic: [
        { text: "Subprime mortgages were loans given to borrowers with low credit scores, often with adjustable rates that reset higher after an initial period.", promoted_from_run_id: "9f3a1c2d", timestamp: "2026-07-18T13:43:00Z", tags: ["finance", "2008"] },
        { text: "Lehman Brothers bankruptcy (Sept 15, 2008) was the largest bankruptcy filing in US history at $639 billion in assets.", promoted_from_run_id: "9f3a1c2d", timestamp: "2026-07-18T13:43:01Z", tags: ["finance", "2008"] },
        { text: "Credit default swaps (CDS) are financial derivatives that function like insurance against bond default, but were largely unregulated before 2008.", promoted_from_run_id: "9f3a1c2d", timestamp: "2026-07-18T13:43:02Z", tags: ["finance", "2008"] }
      ],
      episodic: [
        { text: "Step 1: web_search returned 8 results for '2008 financial crisis causes subprime mortgage'", run_id: "9f3a1c2d", step_id: "s1", timestamp: "2026-07-18T13:42:01Z" },
        { text: "Step 2: read_url extracted 12 facts from 3 sources", run_id: "9f3a1c2d", step_id: "s2", timestamp: "2026-07-18T13:42:15Z" },
        { text: "Step 3: memory.remember wrote 3 entries to semantic collection", run_id: "9f3a1c2d", step_id: "s3", timestamp: "2026-07-18T13:43:00Z" }
      ]
    }
  },
  {
    run_id: "7b2e9d1a-3c4f-5a6b-b7c8-d9e0f1a23456",
    agent_name: "research_agent",
    task: "Explain quantum computing in simple terms",
    plan: [
      { step_id: "s1", description: "Search for quantum computing basics", status: "success" },
      { step_id: "s2", description: "Read beginner-friendly sources", status: "success" },
      { step_id: "s3", description: "Simplify and synthesize answer", status: "success" }
    ],
    steps: [
      { step_id: "s1", tool_calls: [{ tool: "web_search", input: { query: "quantum computing explained simply" }, output: { results: 6 } }], quality_check: { rule_check: "pass", llm_rubric_check: null }, retries: 0, duration_ms: 128 },
      { step_id: "s2", tool_calls: [{ tool: "read_url", input: { url: "https://example.com/quantum" }, output: { facts: 5 } }], quality_check: { rule_check: "pass", llm_rubric_check: null }, retries: 0, duration_ms: 560 },
      { step_id: "s3", tool_calls: [{ tool: "llm_generate", input: { prompt: "Explain quantum computing simply..." }, output: { text: "Quantum computing uses qubits..." } }], quality_check: { rule_check: "pass", llm_rubric_check: "pass" }, retries: 0, duration_ms: 1800 }
    ],
    final_status: "success",
    started_at: "2026-07-18T11:30:00Z",
    ended_at: "2026-07-18T11:31:48Z",
    memory: {
      semantic: [
        { text: "Quantum computing uses qubits that exploit superposition and entanglement to perform calculations exponentially faster than classical bits for certain problems.", promoted_from_run_id: "7b2e9d1a", timestamp: "2026-07-18T11:31:00Z", tags: ["physics", "computing"] }
      ],
      episodic: []
    }
  },
  {
    run_id: "a1b2c3d4-e5f6-4a5b-b6c7-d8e9f0a1b2c3",
    agent_name: "scaffold_agent",
    task: "Build a Flask API with auth and /health",
    plan: [
      { step_id: "s1", description: "Plan file structure", status: "success" },
      { step_id: "s2", description: "Write app.py with Flask and /health", status: "failed" },
      { step_id: "s2-r1", description: "Write app.py with Flask and /health (retry)", status: "success" },
      { step_id: "s3", description: "Write requirements.txt", status: "success" },
      { step_id: "s4", description: "Quality check: files exist and syntax valid", status: "success" }
    ],
    steps: [
      { step_id: "s1", tool_calls: [{ tool: "plan_structure", input: {}, output: { files: ["app.py", "requirements.txt"] } }], quality_check: { rule_check: "pass", llm_rubric_check: null }, retries: 0, duration_ms: 320 },
      { step_id: "s2", tool_calls: [{ tool: "write_file", input: { path: "app.py", content: "..." }, output: { error: "SyntaxError: invalid syntax" } }], quality_check: { rule_check: "fail", llm_rubric_check: null }, retries: 0, duration_ms: 450 },
      { step_id: "s2-r1", tool_calls: [{ tool: "write_file", input: { path: "app.py", content: "from flask import Flask..." }, output: { written: true } }], quality_check: { rule_check: "pass", llm_rubric_check: null }, retries: 1, duration_ms: 520 },
      { step_id: "s3", tool_calls: [{ tool: "write_file", input: { path: "requirements.txt", content: "flask==3.0.0" }, output: { written: true } }], quality_check: { rule_check: "pass", llm_rubric_check: null }, retries: 0, duration_ms: 80 },
      { step_id: "s4", tool_calls: [{ tool: "check_syntax", input: { path: "app.py" }, output: { valid: true } }], quality_check: { rule_check: "pass", llm_rubric_check: null }, retries: 0, duration_ms: 210 }
    ],
    final_status: "success",
    started_at: "2026-07-17T09:15:00Z",
    ended_at: "2026-07-17T09:18:02Z",
    memory: { semantic: [], episodic: [] }
  }
];

function init() {
  traces = [...mockTraces];
  renderOverview();
  renderRuns();
  
  // Expose global functions for HTML inline handlers
  window.showPanel = showPanel;
  window.handleDrop = handleDrop;
  window.handleFiles = handleFiles;
  window.selectRun = selectRun;
  window.switchMemTab = switchMemTab;
  window.toggleExpand = toggleExpand;
}

function showPanel(id) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  event.target.closest('.nav-item').classList.add('active');
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('panel-' + id).classList.add('active');
  const titles = { overview: 'Dashboard', runs: 'Runs', plan: 'Plan & Trace', memory: 'Memory', arch: 'Architecture' };
  document.getElementById('page-title').textContent = titles[id];
}

function showPanelDirect(id) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('panel-' + id).classList.add('active');
  const map = { plan: 2, memory: 3, arch: 4, runs: 1, overview: 0 };
  document.querySelectorAll('.nav-item')[map[id]].classList.add('active');
  const titles = { overview: 'Dashboard', runs: 'Runs', plan: 'Plan & Trace', memory: 'Memory', arch: 'Architecture' };
  document.getElementById('page-title').textContent = titles[id];
}

function handleDrop(e) {
  e.preventDefault();
  e.currentTarget.classList.remove('dragover');
  handleFiles(e.dataTransfer.files);
}

function handleFiles(files) {
  Array.from(files).forEach(file => {
    if (!file.name.endsWith('.json')) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        if (data.run_id && data.steps) {
          traces.unshift(data);
          renderOverview();
          renderRuns();
        }
      } catch (err) {
        alert('Invalid trace file: ' + file.name);
      }
    };
    reader.readAsText(file);
  });
}

function renderOverview() {
  const success = traces.filter(t => t.final_status === 'success').length;
  const heals = traces.reduce((sum, t) => sum + t.steps.filter(s => s.retries > 0).length, 0);
  const tools = traces.reduce((sum, t) => sum + t.steps.reduce((s2, st) => s2 + (st.tool_calls ? st.tool_calls.length : 0), 0), 0);
  const mems = traces.reduce((sum, t) => sum + (t.memory ? (t.memory.semantic?.length || 0) + (t.memory.episodic?.length || 0) : 0), 0);

  const grid = document.getElementById('statsGrid');
  grid.innerHTML = `
    <div class="stat-card"><div class="stat-value" style="color:var(--green)">${success}</div><div class="stat-label">Successful Runs</div></div>
    <div class="stat-card"><div class="stat-value" style="color:var(--yellow)">${heals}</div><div class="stat-label">Self-Heals</div></div>
    <div class="stat-card"><div class="stat-value" style="color:var(--magenta)">${tools}</div><div class="stat-label">Tool Calls</div></div>
    <div class="stat-card"><div class="stat-value" style="color:var(--cyan)">${mems}</div><div class="stat-label">Memory Entries</div></div>
  `;

  if (traces.length > 0) {
    document.getElementById('emptyState').style.display = 'none';
    const latest = traces[0];
    document.getElementById('latestRunCard').style.display = 'block';
    document.getElementById('agent-badge').style.display = 'inline-flex';
    document.getElementById('agent-name').textContent = latest.agent_name;
    document.getElementById('latestStatus').textContent = latest.final_status;
    document.getElementById('latestStatus').className = 'tag tag-quality-' + (latest.final_status === 'success' ? 'pass' : 'fail');
    document.getElementById('latestRunContent').innerHTML = `
      <div style="font-size:16px;color:var(--text-primary);margin-bottom:8px;font-weight:500;">${escapeHtml(latest.task)}</div>
      <div style="font-size:13px;color:var(--text-secondary);">${latest.plan.length} steps · ${latest.steps.reduce((s,st) => s + (st.tool_calls?.length||0), 0)} tool calls · ${latest.steps.filter(s=>s.retries>0).length} retries</div>
    `;
    document.getElementById('latestTracePath').textContent = `.anvil/runs/${latest.run_id}.json`;
  }
}

function renderRuns() {
  document.getElementById('runCount').textContent = traces.length + ' run' + (traces.length !== 1 ? 's' : '');
  const list = document.getElementById('runList');
  list.innerHTML = traces.map(t => `
    <div class="run-item ${t.run_id === selectedRunId ? 'selected' : ''}" onclick="selectRun('${t.run_id}')">
      <div class="run-status ${t.final_status === 'success' ? 'success' : t.final_status === 'failed' ? 'failed' : 'running'}"></div>
      <div class="run-info">
        <div class="run-title">${escapeHtml(t.task)}</div>
        <div class="run-meta">
          <span style="color:var(--cyan);font-weight:600">${t.agent_name}</span>
          <span>•</span>
          <span>${t.plan.length} steps${t.steps.some(s=>s.retries>0) ? ', <span style="color:var(--yellow)">' + t.steps.filter(s=>s.retries>0).length + ' retry</span>' : ''}</span>
          <span>•</span>
          <span>${formatDuration(t.started_at, t.ended_at)}</span>
        </div>
      </div>
      <div class="run-time">${formatTime(t.started_at)}</div>
    </div>
  `).join('');
}

function selectRun(runId) {
  selectedRunId = runId;
  renderRuns();
  const trace = traces.find(t => t.run_id === runId);
  if (!trace) return;
  renderPlan(trace);
  renderMemory(trace);
  showPanelDirect('plan');
}

function toggleExpand(el) {
  el.classList.toggle('expanded');
}

function renderPlan(trace) {
  document.getElementById('planMeta').textContent = `${trace.agent_name} · ${trace.plan.length} steps · ${trace.final_status}`;
  const container = document.getElementById('stepsContainer');
  container.innerHTML = trace.plan.map((step, idx) => {
    const stepData = trace.steps.find(s => s.step_id === step.status === 'retried' ? step.step_id + '-r1' : step.step_id) || trace.steps[idx];
    const isRetry = stepData && stepData.retries > 0;
    const status = step.status === 'success' ? 'success' : step.status === 'failed' ? 'failed' : isRetry ? 'retry' : 'pending';
    const icon = status === 'success' ? '✓' : status === 'failed' ? '✗' : status === 'retry' ? '↻' : '○';
    const toolCalls = stepData?.tool_calls || [];
    const toolsHtml = toolCalls.map(tc => `<span class="tag tag-tool">${tc.tool}</span>`).join(' ');
    const memTag = toolCalls.some(tc => tc.tool === 'memory_remember') ? `<span class="tag tag-memory">◆ memory</span>` : '';
    const llmTag = toolCalls.some(tc => tc.tool === 'llm_generate') ? `<span class="tag tag-llm">◇ llm</span>` : '';
    const quality = stepData?.quality_check;
    const qualityTag = quality ? `<span class="tag tag-quality-${quality.rule_check === 'pass' ? 'pass' : 'fail'}">${quality.rule_check === 'pass' ? '✓' : '✗'} ${quality.rule_check}</span>` : '';
    const rubricTag = quality?.llm_rubric_check ? `<span class="tag tag-quality-${quality.llm_rubric_check === 'pass' ? 'pass' : 'fail'}">rubric ${quality.llm_rubric_check}</span>` : '';

    let detailHtml = '';
    if (stepData) {
      detailHtml = `
        <div class="detail-block">
          <div class="detail-block-title">Tool Calls</div>
          ${toolCalls.map(tc => `
            <div class="code-block">${syntaxHighlight(JSON.stringify(tc, null, 2))}</div>
          `).join('')}
        </div>
        <div class="detail-block">
          <div class="detail-block-title">Quality Check</div>
          <div class="code-block">${syntaxHighlight(JSON.stringify(quality, null, 2))}</div>
        </div>
        <div class="detail-block">
          <div class="detail-block-title">Metadata</div>
          <div style="font-size:12px;color:var(--text-secondary);font-family:var(--font-mono);">
            duration: ${stepData.duration_ms}ms · retries: ${stepData.retries}
          </div>
        </div>
      `;
    }

    return `
      <div class="step" onclick="toggleExpand(this)">
        <div class="step-header">
          <div class="step-num ${status}">${icon}</div>
          <div class="step-body">
            <div class="step-title">Step ${idx+1}/${trace.plan.length}: ${escapeHtml(step.description)}</div>
            <div class="step-tags">${toolsHtml} ${memTag} ${llmTag} ${qualityTag} ${rubricTag}</div>
          </div>
          <div class="step-expand">▼</div>
        </div>
        <div class="step-content">${detailHtml}</div>
      </div>
      ${isRetry ? `<div class="retry-banner"><span style="font-family:var(--font-mono);font-size:16px;">↻</span> Self-heal triggered: same-step retry (attempt ${stepData.retries + 1}/3)</div>` : ''}
    `;
  }).join('');
}

function renderMemory(trace) {
  const list = document.getElementById('memoryList');
  const entries = activeMemTab === 'semantic' ? (trace.memory?.semantic || []) : (trace.memory?.episodic || []);
  if (entries.length === 0) {
    list.innerHTML = `<div class="memory-item"><div class="memory-text" style="color:var(--text-tertiary)">No ${activeMemTab} memory entries for this run.</div></div>`;
    return;
  }
  list.innerHTML = entries.map(e => `
    <div class="memory-item">
      <div class="memory-text">${escapeHtml(e.text)}</div>
      <div class="memory-meta">
        ${e.promoted_from_run_id ? `<span style="color:var(--cyan)">from ${e.promoted_from_run_id.slice(0,8)}</span>` : ''}
        ${e.run_id ? `<span style="color:var(--cyan)">run ${e.run_id.slice(0,8)}</span>` : ''}
        ${e.step_id ? `<span style="color:var(--magenta)">step ${e.step_id}</span>` : ''}
        <span>${formatTime(e.timestamp)}</span>
        ${e.tags ? `<span>tags: [${e.tags.join(', ')}]</span>` : ''}
      </div>
    </div>
  `).join('');
}

function switchMemTab(btn, tab) {
  activeMemTab = tab;
  document.querySelectorAll('.mem-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  const trace = traces.find(t => t.run_id === selectedRunId);
  if (trace) renderMemory(trace);
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function syntaxHighlight(json) {
  return json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/(".*?")/g, '<span class="string">$1</span>')
    .replace(/ (true|false) /g, '<span class="bool">$1</span>')
    .replace(/ (null) /g, '<span class="null">$1</span>')
    .replace(/ (\d+) /g, '<span class="number">$1</span>')
    .replace(/([{}[\],])/g, '<span class="key">$1</span>')
    .replace(/(".*?")\s*:/g, '<span class="key">$1</span>:');
}

function formatDuration(start, end) {
  if (!start || !end) return '—';
  const s = new Date(start), e = new Date(end);
  const sec = Math.round((e - s) / 1000);
  if (sec < 60) return sec + 's';
  const m = Math.floor(sec / 60), r = sec % 60;
  return m + 'm ' + (r > 0 ? r + 's' : '');
}

function formatTime(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
  return d.toLocaleDateString();
}

// Initialize
document.addEventListener('DOMContentLoaded', init);
