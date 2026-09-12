const THEME_KEY = 'asterix-theme';
const VM_STORAGE_KEY = 'asterix-vm-catalog';
const SSH_KEY_STORAGE_KEY = 'asterix-ssh-keys';
const API_BASE_URL = 'http://localhost:8765';
const defaultVmCatalog = [
  { name: 'vps-prod-01', region: 'us-east', cpu: '8 vCPU', ram: '32 GB', status: 'Running', progress: 88, image: 'Ubuntu 24.04 LTS', sshKey: 'operator@asterix' },
  { name: 'vps-dev-03', region: 'eu-west', cpu: '4 vCPU', ram: '16 GB', status: 'Scaling', progress: 62, image: 'Debian 12', sshKey: 'ci-bot@dev' },
  { name: 'edge-node-09', region: 'ap-south', cpu: '6 vCPU', ram: '24 GB', status: 'Healthy', progress: 74, image: 'Fedora 40', sshKey: 'edge-gateway' },
  { name: 'sandbox-12', region: 'local', cpu: '2 vCPU', ram: '8 GB', status: 'Paused', progress: 34, image: 'Ubuntu 24.04 LTS', sshKey: 'operator@asterix' },
  { name: 'demo-k8s-01', region: 'us-central', cpu: '12 vCPU', ram: '48 GB', status: 'Ready', progress: 91, image: 'Custom ISO', sshKey: 'ci-bot@dev' },
  { name: 'backup-vm-02', region: 'us-east', cpu: '4 vCPU', ram: '16 GB', status: 'Queued', progress: 48, image: 'Debian 12', sshKey: 'new-key' }
];
const defaultKeyCatalog = [
  { name: 'operator@asterix', fingerprint: 'SHA256:tQx3Qf...7zM' },
  { name: 'ci-bot@dev', fingerprint: 'SHA256:6Vxy8K...pFO' },
  { name: 'edge-gateway', fingerprint: 'SHA256:Hmp9kL...Q1L' }
];
const defaultSnapshotCatalog = [
  { name: 'prod-snapshot-01', created: '2026-09-12 09:15', size: '14 GB', status: 'Verified' },
  { name: 'edge-snapshot-02', created: '2026-09-11 21:42', size: '8 GB', status: 'Ready' },
  { name: 'sandbox-snapshot-04', created: '2026-09-10 18:01', size: '4 GB', status: 'Queued' }
];

let vmCatalog = JSON.parse(localStorage.getItem(VM_STORAGE_KEY) || 'null') || [...defaultVmCatalog];
let sshKeyCatalog = JSON.parse(localStorage.getItem(SSH_KEY_STORAGE_KEY) || 'null') || [...defaultKeyCatalog];
let snapshotCatalog = JSON.parse(localStorage.getItem('asterix-snapshots') || 'null') || [...defaultSnapshotCatalog];

async function fetchJson(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...options
    });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.warn(`API request failed for ${url}:`, error.message);
    return null;
  }
}

async function loadAdminData() {
  const payload = await fetchJson(`${API_BASE_URL}/api/admin`);
  if (!payload) return;

  if (Array.isArray(payload.vms)) {
    vmCatalog = payload.vms;
    localStorage.setItem(VM_STORAGE_KEY, JSON.stringify(vmCatalog));
  }
  if (Array.isArray(payload.keys)) {
    sshKeyCatalog = payload.keys;
    localStorage.setItem(SSH_KEY_STORAGE_KEY, JSON.stringify(sshKeyCatalog));
  }
  if (Array.isArray(payload.snapshots)) {
    snapshotCatalog = payload.snapshots;
    localStorage.setItem('asterix-snapshots', JSON.stringify(snapshotCatalog));
  }

  renderDashboard();
  renderVMs();
  renderSSHKeys();
  renderSnapshots();
  renderAdminVMs();
}

function initFloatingWindows() {
  const windows = document.querySelectorAll('.floating-window');
  windows.forEach((windowEl) => {
    const titlebar = windowEl.querySelector('.window-titlebar');
    if (!titlebar) return;

    titlebar.addEventListener('mousedown', (event) => {
      if (event.target.closest('button')) return;
      const parent = windowEl.parentElement;
      const rect = windowEl.getBoundingClientRect();
      const shellRect = parent.getBoundingClientRect();
      const offsetX = event.clientX - rect.left;
      const offsetY = event.clientY - rect.top;

      function onMove(moveEvent) {
        const newLeft = Math.min(Math.max(moveEvent.clientX - shellRect.left - offsetX, 10), shellRect.width - rect.width - 10);
        const newTop = Math.min(Math.max(moveEvent.clientY - shellRect.top - offsetY, 10), shellRect.height - rect.height - 10);
        windowEl.style.left = `${newLeft}px`;
        windowEl.style.top = `${newTop}px`;
      }

      function onUp() {
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      }

      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    });
  });
}

const systemOverview = {
  nodes: 4,
  vms: 12,
  uptime: '99.4%',
  cpu: '42%',
  ram: '73%',
  latency: '18ms',
  threat: 'Low',
  workloads: [
    { service: 'vm-orchestrator', owner: 'ops', status: 'Ready', health: '99.8%' },
    { service: 'cloud-scan', owner: 'security', status: 'Running', health: '97.6%' },
    { service: 'api-gateway', owner: 'platform', status: 'Scaling', health: '93.2%' },
    { service: 'vault-sync', owner: 'infra', status: 'Review', health: '88.4%' }
  ],
  vms: [
    { name: 'vps-prod-01', region: 'us-east', cpu: '8 vCPU', ram: '32 GB', status: 'Running', progress: 88 },
    { name: 'vps-dev-03', region: 'eu-west', cpu: '4 vCPU', ram: '16 GB', status: 'Scaling', progress: 62 },
    { name: 'edge-node-09', region: 'ap-south', cpu: '6 vCPU', ram: '24 GB', status: 'Healthy', progress: 74 },
    { name: 'sandbox-12', region: 'local', cpu: '2 vCPU', ram: '8 GB', status: 'Paused', progress: 34 },
    { name: 'demo-k8s-01', region: 'us-central', cpu: '12 vCPU', ram: '48 GB', status: 'Ready', progress: 91 },
    { name: 'backup-vm-02', region: 'us-east', cpu: '4 vCPU', ram: '16 GB', status: 'Queued', progress: 48 }
  ],
  activity: [
    { title: 'VM bootstrap completed', text: 'Operator workflow finished successfully across 3 hosts.', time: '2m ago', level: 'info' },
    { title: 'Storage threshold warning', text: 'Persistent volume nearing the recommended reuse limit.', time: '9m ago', level: 'warning' },
    { title: 'Firewall rule review required', text: 'One suspicious port pattern was flagged during routine inspection.', time: '14m ago', level: 'alert' }
  ]
};

function renderDashboard() {
  const tableBody = document.querySelector('#workloadTableBody');
  if (tableBody) {
    tableBody.innerHTML = systemOverview.workloads.map(item => `
      <tr>
        <td>${item.service}</td>
        <td>${item.owner}</td>
        <td><span class="pill ${item.status === 'Ready' ? 'healthy' : item.status === 'Running' ? 'healthy' : item.status === 'Scaling' ? 'warning' : 'alert'}">${item.status}</span></td>
        <td>${item.health}</td>
      </tr>
    `).join('');
  }

  const activityList = document.querySelector('#activityList');
  if (activityList) {
    activityList.innerHTML = systemOverview.activity.map(item => `
      <div class="activity-item ${item.level === 'warning' ? 'warning' : item.level === 'alert' ? 'alert' : ''}">
        <div class="activity-dot"></div>
        <div>
          <strong>${item.title}</strong>
          <span>${item.text}</span>
        </div>
        <time>${item.time}</time>
      </div>
    `).join('');
  }

  const statsMap = {
    '#statNodes': systemOverview.nodes,
    '#statVMs': systemOverview.vms,
    '#statUptime': systemOverview.uptime,
    '#statCPU': systemOverview.cpu,
    '#statRAM': systemOverview.ram,
    '#statLatency': systemOverview.latency,
    '#statThreat': systemOverview.threat
  };

  Object.entries(statsMap).forEach(([selector, value]) => {
    const node = document.querySelector(selector);
    if (node) node.textContent = value;
  });
}

function renderVMs() {
  const vmGrid = document.querySelector('#vmGrid');
  if (!vmGrid) return;

  vmGrid.innerHTML = vmCatalog.map(vm => `
    <div class="vm-card">
      <div class="vm-header">
        <span class="vm-name">${vm.name}</span>
        <span class="pill ${vm.status === 'Running' || vm.status === 'Healthy' || vm.status === 'Ready' ? 'healthy' : vm.status === 'Scaling' ? 'warning' : 'alert'}">${vm.status}</span>
      </div>
      <div class="vm-meta">${vm.image || 'Ubuntu 24.04 LTS'} • ${vm.region} • ${vm.cpu} • ${vm.ram}</div>
      <div class="progress"><div class="progress-bar" style="width:${vm.progress}%"></div></div>
      <div class="vm-meta">Key: ${vm.sshKey || 'operator@asterix'} • Capacity ${vm.progress}%</div>
    </div>
  `).join('');
}

function renderSSHKeys() {
  const sshList = document.querySelector('#sshList');
  const adminKeyList = document.querySelector('#adminKeyList');

  const markup = sshKeyCatalog.map(key => `
    <div class="key-item">
      <div class="key-meta">
        <span class="key-name">${key.name}</span>
        <span class="key-fpr">${key.fingerprint}</span>
      </div>
      <span class="pill healthy">Active</span>
    </div>
  `).join('');

  if (sshList) sshList.innerHTML = markup;
  if (adminKeyList) adminKeyList.innerHTML = markup;
}

function renderSnapshots() {
  const snapshotList = document.querySelector('#snapshotList');
  if (!snapshotList) return;

  snapshotList.innerHTML = snapshotCatalog.map(snapshot => `
    <div class="key-item">
      <div class="key-meta">
        <span class="key-name">${snapshot.name}</span>
        <span class="key-fpr">${snapshot.created} • ${snapshot.size}</span>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <span class="pill ${snapshot.status === 'Verified' ? 'healthy' : snapshot.status === 'Ready' ? 'healthy' : 'warning'}">${snapshot.status}</span>
        <button class="snapshot-action" data-snapshot="${snapshot.name}" type="button">Cleanup</button>
      </div>
    </div>
  `).join('');

  document.querySelectorAll('.snapshot-action').forEach((button) => {
    button.addEventListener('click', async () => {
      const snapshotName = button.dataset.snapshot;
      const result = await fetchJson(`${API_BASE_URL}/api/snapshot/${encodeURIComponent(snapshotName)}`, { method: 'DELETE' });
      if (result && Array.isArray(result.snapshots)) {
        snapshotCatalog = result.snapshots;
        localStorage.setItem('asterix-snapshots', JSON.stringify(snapshotCatalog));
        renderSnapshots();
      }
    });
  });
}

function renderAdminVMs() {
  const adminVmTableBody = document.querySelector('#adminVmTableBody');
  if (!adminVmTableBody) return;

  adminVmTableBody.innerHTML = vmCatalog.slice(0, 6).map(vm => `
    <tr>
      <td>${vm.name}</td>
      <td>${vm.region}</td>
      <td><span class="pill ${vm.status === 'Running' || vm.status === 'Healthy' || vm.status === 'Ready' ? 'healthy' : vm.status === 'Scaling' ? 'warning' : 'alert'}">${vm.status}</span></td>
      <td>
        <div class="lifecycle-actions" style="margin: 0;">
          <button class="vm-action" data-vm="${vm.name}" data-action="start" type="button">Start</button>
          <button class="vm-action" data-vm="${vm.name}" data-action="stop" type="button">Stop</button>
          <button class="vm-action" data-vm="${vm.name}" data-action="reboot" type="button">Reboot</button>
          <button class="vm-action" data-vm="${vm.name}" data-action="delete" type="button">Delete</button>
        </div>
      </td>
    </tr>
  `).join('');

  document.querySelectorAll('.vm-action').forEach((button) => {
    button.addEventListener('click', async () => {
      const action = button.dataset.action;
      const vmName = button.dataset.vm;
      await handleVmAction(action, vmName);
    });
  });
}

function applyTheme(theme) {
  const selected = theme === 'light' ? 'light' : 'dark';
  document.body.setAttribute('data-theme', selected);
  localStorage.setItem(THEME_KEY, selected);

  const toggle = document.querySelector('#themeToggleBtn');
  if (toggle) {
    toggle.textContent = selected === 'dark' ? 'Theme: Dark' : 'Theme: Light';
  }
}

function toggleTheme() {
  const current = document.body.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

function bindNavigation() {
  const navLinks = document.querySelectorAll('[data-page-link]');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navLinks.forEach(item => item.classList.remove('active'));
      link.classList.add('active');
    });
  });
}

async function handleVmAction(action, vmName) {
  if (!vmName) return;

  const endpoint = action === 'delete'
    ? `${API_BASE_URL}/api/vm/${encodeURIComponent(vmName)}`
    : `${API_BASE_URL}/api/vm/${encodeURIComponent(vmName)}/${action}`;

  const result = await fetchJson(endpoint, {
    method: action === 'delete' ? 'DELETE' : 'POST',
    body: JSON.stringify({ action })
  });

  if (result && Array.isArray(result.vms)) {
    vmCatalog = result.vms;
    localStorage.setItem(VM_STORAGE_KEY, JSON.stringify(vmCatalog));
    renderVMs();
    renderAdminVMs();
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  applyTheme(localStorage.getItem(THEME_KEY) || 'dark');
  initFloatingWindows();
  await loadAdminData();
  bindNavigation();

  const themeToggle = document.querySelector('#themeToggleBtn');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }

  const modal = document.querySelector('#vmModal');
  const openVmModalBtn = document.querySelector('#openVmModalBtn');
  const closeVmModalBtn = document.querySelector('#closeVmModalBtn');
  const vmForm = document.querySelector('#vmForm');

  if (openVmModalBtn && modal) {
    openVmModalBtn.addEventListener('click', () => modal.classList.remove('hidden'));
  }

  if (closeVmModalBtn && modal) {
    closeVmModalBtn.addEventListener('click', () => modal.classList.add('hidden'));
  }

  if (modal) {
    modal.addEventListener('click', (event) => {
      if (event.target === modal) modal.classList.add('hidden');
    });
  }

  if (vmForm) {
    vmForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(vmForm);
      const newVm = {
        name: formData.get('vmName') || 'new-vm',
        region: formData.get('vmRegion') || 'us-east',
        image: formData.get('vmImage') || 'Ubuntu 24.04 LTS',
        cpu: formData.get('vmCpu') || '4 vCPU',
        ram: formData.get('vmRam') || '16 GB',
        sshKey: formData.get('vmKey') || 'operator@asterix',
        status: 'Queued',
        progress: 18
      };

      vmCatalog = [newVm, ...vmCatalog];
      localStorage.setItem(VM_STORAGE_KEY, JSON.stringify(vmCatalog));
      renderVMs();
      vmForm.reset();
      if (modal) modal.classList.add('hidden');
    });
  }

  const addKeyBtn = document.querySelector('#addKeyBtn');
  if (addKeyBtn) {
    addKeyBtn.addEventListener('click', () => {
      const keyName = `key-${sshKeyCatalog.length + 1}`;
      const newKey = { name: keyName, fingerprint: 'SHA256:generated...' };
      sshKeyCatalog = [newKey, ...sshKeyCatalog];
      localStorage.setItem(SSH_KEY_STORAGE_KEY, JSON.stringify(sshKeyCatalog));
      renderSSHKeys();
    });
  }

  const createSnapshotBtn = document.querySelector('.primary-btn');
  if (createSnapshotBtn && window.location.pathname.includes('admin.html')) {
    createSnapshotBtn.addEventListener('click', async () => {
      const stamp = new Date().toISOString().slice(0, 16).replace('T', ' ');
      const snapshotName = `snapshot-${snapshotCatalog.length + 1}`;
      const result = await fetchJson(`${API_BASE_URL}/api/snapshot`, {
        method: 'POST',
        body: JSON.stringify({ name: snapshotName, created: stamp, size: '2 GB', status: 'Queued' })
      });

      if (result && Array.isArray(result.snapshots)) {
        snapshotCatalog = result.snapshots;
        localStorage.setItem('asterix-snapshots', JSON.stringify(snapshotCatalog));
      } else {
        snapshotCatalog = [{ name: snapshotName, created: stamp, size: '2 GB', status: 'Queued' }, ...snapshotCatalog];
        localStorage.setItem('asterix-snapshots', JSON.stringify(snapshotCatalog));
      }
      renderSnapshots();
    });
  }

  const loginForm = document.querySelector('#loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const username = document.querySelector('#username')?.value || 'operator';
      const host = document.querySelector('#host')?.value || 'asterix-primary';
      const session = { loggedIn: true, username, host, signedAt: new Date().toISOString() };
      localStorage.setItem('asterix_desktop_login_v1', JSON.stringify(session));
      const redirectTarget = `index.html?login=1&user=${encodeURIComponent(username)}&host=${encodeURIComponent(host)}`;
      window.location.href = redirectTarget;
    });
  }

  const searchInput = document.querySelector('#quickSearch');
  if (searchInput) {
    searchInput.addEventListener('input', (event) => {
      const query = event.target.value.trim().toLowerCase();
      const cards = document.querySelectorAll('.vm-card');
      cards.forEach(card => {
        const label = card.textContent.toLowerCase();
        card.style.display = label.includes(query) ? '' : 'none';
      });
    });
  }
});
