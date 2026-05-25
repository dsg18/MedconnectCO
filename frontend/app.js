/* ════════════════════════════════════════════════════════════════════════════
   MedConnectCo — Frontend
   ════════════════════════════════════════════════════════════════════════════ */

const API = ''; // Usar ruta relativa ya que el Gateway sirve ambos

// ── State ─────────────────────────────────────────────────────────────────────
const state = {
  token: localStorage.getItem('ehr_token') || null,
  user:  null,
};

// ── DOM helpers ───────────────────────────────────────────────────────────────
const $  = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);
const show = (el) => { if (typeof el === 'string') el = $(el); el?.classList.remove('hidden'); };
const hide = (el) => { if (typeof el === 'string') el = $(el); el?.classList.add('hidden'); };

// ── Toast ─────────────────────────────────────────────────────────────────────
function toast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  $('#toast-container').appendChild(t);
  setTimeout(() => t.classList.add('show'), 10);
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 350); }, 3500);
}

// ── HTTP client ───────────────────────────────────────────────────────────────
async function request(method, path, body = null, isForm = false) {
  const headers = {};
  if (state.token) headers['Authorization'] = `Bearer ${state.token}`;
  if (body && !isForm) headers['Content-Type'] = 'application/json';

  const opts = { method, headers };
  if (body) opts.body = isForm ? body : JSON.stringify(body);

  const res = await fetch(API + path, opts);

  if (res.status === 401) {
    if (path !== '/auth/login' && path !== '/login') {
      logout();
      throw new Error('Sesión expirada, inicia sesión nuevamente');
    }
  }
  if (res.status === 204) return null;

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `Error ${res.status}`);
  return data;
}

const http = {
  get:    (p)       => request('GET',    p),
  post:   (p, b, f) => request('POST',   p, b, f),
  patch:  (p, b)    => request('PATCH',  p, b),
  put:    (p, b)    => request('PUT',    p, b),
  delete: (p)       => request('DELETE', p),
};

// ── Auth ──────────────────────────────────────────────────────────────────────
async function login(username, password) {
  const form = new URLSearchParams({ username, password });
  const data = await http.post('/auth/login', form, true);
  state.token = data.access_token;
  localStorage.setItem('ehr_token', state.token);
}

function logout() {
  state.token = null;
  state.user  = null;
  localStorage.removeItem('ehr_token');
  showLogin();
}

async function loadMe() {
  state.user = await http.get('/auth/me');
}

// ── App shell ─────────────────────────────────────────────────────────────────
function showLogin() {
  show('#login-screen');
  hide('#app');
  $('#login-username').value = '';
  $('#login-password').value = '';
  hide('#login-error');
}

function showApp() {
  hide('#login-screen');
  show('#app');
  const u = state.user;
  $('#user-name').textContent   = u.username;
  const roleLabels = { admin: 'Administrador', admin_clinica: 'Admin. de Clínica', medico: 'Médico', paciente: 'Paciente' };
  $('#user-role').textContent   = roleLabels[u.rol] || u.rol;
  $('#user-avatar').textContent = u.username[0].toUpperCase();
  $('#user-avatar').className   = `user-avatar role-${u.rol}`;
  configureNav(u.rol);
  // Cada rol inicia en su sección principal
  const inicio = { admin: 'dashboard', admin_clinica: 'hospitales', medico: 'pacientes', paciente: 'historias' };
  navigateTo(inicio[u.rol] || 'pacientes');
}

// Controla qué secciones puede ver cada rol
function configureNav(rol) {
  const links = $$('.nav-link');
  links.forEach(l => {
    const section = l.dataset.section;
    let visible = true;
    if (rol === 'paciente') {
      visible = (section === 'historias' || section === 'notificaciones');
    } else if (rol === 'medico') {
      visible = (section === 'pacientes');
    } else {
      if (section === 'notificaciones') visible = false;
      if (section === 'usuarios' && rol !== 'admin' && rol !== 'admin_clinica') visible = false;
    }
    l.style.display = visible ? 'flex' : 'none';
  });
}

async function checkAuth() {
  console.log('Bootstrapping MedConnectCo...');
  if (!state.token) { console.log('No token found, showing login'); showLogin(); return; }
  try { await loadMe(); showApp(); }
  catch (e) { console.error('Auth check failed:', e); showLogin(); }
}

// ── Navigation ────────────────────────────────────────────────────────────────
const TITLES = { dashboard: 'Dashboard', hospitales: 'Hospitales', pacientes: 'Pacientes', historias: 'Historias Clínicas', usuarios: 'Gestión de Usuarios' };

function navigateTo(section) {
  $$('.content-section').forEach(s => s.classList.remove('active'));
  $$('.nav-link').forEach(l => l.classList.remove('active'));
  $(`#section-${section}`)?.classList.add('active');
  $(`.nav-link[data-section="${section}"]`)?.classList.add('active');
  
  $('#topbar-actions').innerHTML = '';

  switch (section) {
    case 'dashboard':
      $('#page-title').textContent = 'Dashboard';
      renderDashboard();
      break;
    case 'hospitales':
      $('#page-title').textContent = 'Hospitales';
      renderHospitales();
      break;
    case 'pacientes':
      $('#page-title').textContent = 'Pacientes';
      renderPacientes();
      break;
    case 'historias':
      $('#page-title').textContent = (state.user.rol === 'paciente') ? 'Mi Historia Clínica' : 'Historias Clínicas';
      renderHistorias();
      break;
    case 'notificaciones':
      $('#page-title').textContent = 'Mis Notificaciones';
      renderNotificaciones();
      break;
    case 'usuarios':
      $('#page-title').textContent = 'Gestión de Usuarios';
      renderUsuarios();
      break;
  }
}

// ── DASHBOARD ─────────────────────────────────────────────────────────────────
async function renderDashboard() {
  const isPaciente = state.user?.rol === 'paciente';
  if (isPaciente) {
    $('#page-title').textContent = 'Panel del Paciente';
    $('#section-dashboard').innerHTML = `
      <div id="paciente-header-info" style="margin-bottom:20px"></div>
      <div class="stats-grid">
        <div class="stat-card stat-blue">
          <div class="stat-icon">📋</div>
          <div id="stat-mis-historias" class="stat-value">...</div>
          <div class="stat-label">Mis Historias</div>
        </div>
        <div class="stat-card stat-yellow">
          <div class="stat-icon">🔔</div>
          <div id="stat-notif" class="stat-value">...</div>
          <div class="stat-label">Alertas</div>
        </div>
      </div>
      <div class="section-header"><h3>Actividad Reciente</h3></div>
      <div id="recent-historias" class="recent-list"></div>
    `;
    try {
      const [historias, notifs, patientData] = await Promise.all([
        http.get(`/historias/paciente/${state.user.username}`),
        http.get('/notificaciones/me'),
        http.get(`/pacientes/${state.user.username}`)
      ]);
      $('#stat-mis-historias').textContent = historias.length;
      $('#stat-notif').textContent = notifs.filter(n => !n.leido).length;
      
      if (patientData.condiciones && patientData.condiciones.length > 0) {
        $('#paciente-header-info').innerHTML = `
          <div class="card" style="padding:15px; border-left:4px solid var(--danger)">
            <label style="font-weight:600; color:var(--muted); font-size:11px; text-transform:uppercase; display:block; margin-bottom:8px">Mis Antecedentes Médicos:</label>
            <div class="tags-container">
              ${patientData.condiciones.map(c => `<span class="badge badge-danger" title="Diagnosticado el ${c.fecha_diagnostico}">${c.nombre}</span>`).join('')}
            </div>
          </div>
        `;
      }
      
      const recent = [...historias].reverse().slice(0, 3);
      $('#recent-historias').innerHTML = recent.map(h => `
        <div class="record-item">
          <div class="record-icon">📋</div>
          <div>
            <div class="record-title">${h.diagnostico}</div>
            <div class="record-sub">${fmtDate(h.fecha_creacion)}</div>
          </div>
        </div>`).join('') || emptyState('📋', 'No tienes historias clínicas registradas.');
    } catch (e) { toast(e.message, 'error'); }
    return;
  }

  try {
    const [hospitales, pacientes, historias] = await Promise.all([
      http.get('/hospitales/'),
      http.get('/pacientes/'),
      http.get('/historias/'),
    ]);
    $('#stat-hospitales').textContent = hospitales.length;
    $('#stat-aprobados').textContent  = hospitales.filter(h => h.aprobado).length;
    $('#stat-pacientes').textContent  = pacientes.length;
    $('#stat-historias').textContent  = historias.length;

    const recent = [...historias].reverse().slice(0, 6);
    $('#recent-historias').innerHTML = recent.length
      ? recent.map(h => `
          <div class="record-item">
            <div class="record-icon">📋</div>
            <div>
              <div class="record-title">${h.diagnostico}</div>
              <div class="record-sub">Paciente ID: ${h.paciente_id} &nbsp;·&nbsp; ${fmtDate(h.fecha_creacion)}</div>
            </div>
          </div>`).join('')
      : emptyState('📋', 'No hay historias clínicas registradas aún.');
  } catch (e) { toast(e.message, 'error'); }
}

// ── HOSPITALES ────────────────────────────────────────────────────────────────
async function renderHospitales() {
  const isAdmin      = state.user?.rol === 'admin';
  const isAdminCli   = state.user?.rol === 'admin_clinica';

  if (isAdmin) {
    $('#topbar-actions').innerHTML =
      `<button class="btn btn-primary" onclick="openModal('modal-hospital')">+ Nuevo Hospital</button>`;
  }
  try {
    const list = await http.get('/hospitales/');
    const container = $('#hospitales-list');
    if (!list.length) { container.innerHTML = emptyState('🏥', 'No hay hospitales registrados.'); return; }

    container.innerHTML = list.map(h => `
      <div class="card ${h.aprobado ? 'approved' : 'pending'}">
        <div class="card-header">
          <div>
            <div class="card-title">${h.nombre}</div>
            <div class="card-sub">📍 ${h.direccion}</div>
          </div>
          <span class="badge ${h.aprobado ? 'badge-success' : 'badge-warning'}">
            ${h.aprobado ? '✓ Aprobado' : '⏳ Pendiente'}
          </span>
        </div>
        ${isAdmin ? `
        <div class="card-actions">
          ${!h.aprobado ? `<button class="btn btn-sm btn-success" onclick="aprobarHospital(${h.id})">✓ Aprobar</button>` : ''}
          <button class="btn btn-sm btn-danger" onclick="eliminarHospital(${h.id}, '${escHtml(h.nombre)}')">Eliminar</button>
        </div>` : ''}
      </div>`).join('');
  } catch (e) { toast(e.message, 'error'); }
}

async function aprobarHospital(id) {
  try {
    await http.patch(`/hospitales/${id}/aprobar`);
    toast('Hospital aprobado en la red nacional');
    renderHospitales();
  } catch (e) { toast(e.message, 'error'); }
}

async function eliminarHospital(id, nombre) {
  if (!confirm(`¿Eliminar "${nombre}"? Esta acción no se puede deshacer.`)) return;
  try {
    await http.delete(`/hospitales/${id}`);
    toast('Hospital eliminado');
    renderHospitales();
  } catch (e) { toast(e.message, 'error'); }
}

// ── PACIENTES ─────────────────────────────────────────────────────────────────
async function renderPacientes(list = null) {
  const isMedico = state.user?.rol === 'medico';

  if (isMedico) {
    // Médico: solo puede buscar por documento, no ve lista completa
    $('#topbar-actions').innerHTML = `
      <div class="search-group">
        <input id="search-doc" type="text" class="search-input" placeholder="Documento del paciente…" />
        <button class="btn btn-primary" onclick="buscarPaciente()">Buscar</button>
      </div>
      <button class="btn btn-primary" onclick="openModal('modal-paciente')">+ Nuevo Paciente</button>`;
    setTimeout(() => {
      $('#search-doc')?.addEventListener('keydown', e => { if (e.key === 'Enter') buscarPaciente(); });
    }, 50);

    const container = $('#pacientes-list');
    if (!list) {
      // Primera carga: solo mostrar prompt de búsqueda
      container.innerHTML = emptyState('🔍', 'Ingrese el documento del paciente para buscarlo.');
      return;
    }
    // Si ya hay resultado de búsqueda, mostrarlo
    renderPacienteTabla(list);
    return;
  }

  // Admin / admin_clinica: controles completos
  $('#topbar-actions').innerHTML = `
    <div class="search-group">
      <input id="search-doc" type="text" class="search-input" placeholder="Buscar por documento…" />
      <button class="btn btn-primary" onclick="buscarPaciente()">Buscar</button>
      <button class="btn btn-outline" onclick="renderPacientes()">Limpiar</button>
    </div>
    <button class="btn btn-primary" onclick="openModal('modal-paciente')">+ Nuevo Paciente</button>`;
  setTimeout(() => {
    $('#search-doc')?.addEventListener('keydown', e => { if (e.key === 'Enter') buscarPaciente(); });
  }, 50);

  try {
    const data = list ?? await http.get('/pacientes/');
    renderPacienteTabla(data);
  } catch (e) { toast(e.message, 'error'); }
}

function renderPacienteTabla(data) {
  const container = $('#pacientes-list');
  if (!data.length) { container.innerHTML = emptyState('👤', 'No se encontraron pacientes.'); return; }
  container.innerHTML = `
    <table class="data-table">
      <thead><tr><th>Documento</th><th>Nombre Completo</th><th>Edad</th><th>Acciones</th></tr></thead>
      <tbody>
        ${data.map(p => `
          <tr>
            <td><code>${p.documento}</code></td>
            <td>${p.nombre_completo}</td>
            <td>${calculateAge(p.fecha_nacimiento)} años</td>
            <td>
              <button class="btn btn-sm btn-outline"
                onclick="verHistoriasDePaciente('${p.documento}', '${escHtml(p.nombre_completo)}')">
                Ver historias
              </button>
            </td>
          </tr>`).join('')}
      </tbody>
    </table>`;
}

async function buscarPaciente() {
  const doc = $('#search-doc')?.value.trim();
  const isMedico = state.user?.rol === 'medico';
  if (!doc) {
    if (isMedico) {
      $('#pacientes-list').innerHTML = emptyState('🔍', 'Ingrese el documento del paciente para buscarlo.');
    } else {
      renderPacientes();
    }
    return;
  }
  try {
    const p = await http.get(`/pacientes/${doc}`);
    renderPacienteTabla([p]);
  } catch (e) { toast(e.message, 'error'); }
}

// Documento del paciente que el médico está viendo actualmente
let _currentPatientDoc = null;
let _currentPatientNombre = null;

async function verHistoriasDePaciente(documento, nombre) {
  const isMedico = state.user?.rol === 'medico';
  if (isMedico) {
    // Médico: muestra las historias inline dentro de la sección Pacientes
    await mostrarDetallesPacienteMedico(documento, nombre);
    return;
  }
  // Admin / admin_clinica: navega a la sección de historias
  navigateTo('historias');
  try {
    const historias = await http.get(`/historias/paciente/${documento}`);
    renderHistoriasList(historias, `Historias de ${nombre}`);
  } catch (e) { toast(e.message, 'error'); }
}

async function mostrarDetallesPacienteMedico(documento, nombre) {
  // Buscar datos completos del paciente para tener la fecha de nacimiento
  let patientData;
  try {
    patientData = await http.get(`/pacientes/${documento}`);
  } catch (e) { toast(e.message, 'error'); return; }

  _currentPatientDoc       = documento;
  _currentPatientNombre    = nombre;
  _currentPatientBirthDate = patientData.fecha_nacimiento;

  const container = $('#pacientes-list');
  container.innerHTML = `
    <div style="margin-bottom:16px">
      <button class="btn btn-outline" onclick="renderPacientes()">← Volver a búsqueda</button>
    </div>
    <div class="card patient-detail-card">
      <div class="card-header">
        <div>
          <div class="card-title">${nombre}</div>
          <div class="card-sub">Documento: <code>${documento}</code> &nbsp;·&nbsp; Edad: ${calculateAge(_currentPatientBirthDate)} años</div>
        </div>
        <div style="display:flex; gap:10px">
          <button class="btn btn-outline" onclick="abrirNuevaCondicion('${documento}')">
            + Antecedentes
          </button>
          <button class="btn btn-primary" onclick="abrirNuevaHistoria('${documento}')">
            + Nueva Historia Clínica
          </button>
        </div>
      </div>
      
      <div id="paciente-condiciones" class="condiciones-container">
        <label style="font-weight:600; color:var(--muted); font-size:12px; text-transform:uppercase">Condiciones Crónicas / Antecedentes:</label>
        <div class="tags-container">
          ${patientData.condiciones && patientData.condiciones.length > 0 
            ? patientData.condiciones.map(c => `
                <span class="badge badge-danger" title="Diagnosticado el ${c.fecha_diagnostico}">
                  ${c.nombre}
                </span>`).join('')
            : '<span style="color:var(--muted); font-size:13px">Sin antecedentes registrados</span>'}
        </div>
      </div>

      <div class="detail-actions">
        <button class="btn btn-outline" onclick="renderPacientes()">Volver al listado</button>
      </div>
    </div>
    <div class="section-header"><h3>Historias Clínicas del Paciente</h3></div>
    <div id="historias-inline" class="cards-grid">
      <div class="empty-state"><div class="empty-state-icon">⏳</div>Cargando…</div>
    </div>`;

  try {
    const historias = await http.get(`/historias/paciente/${documento}`);
    const cont = $('#historias-inline');
    if (!historias.length) {
      cont.innerHTML = emptyState('📋', 'Este paciente no tiene historias clínicas todavía.');
      return;
    }
    cont.innerHTML = historias.map(h => `
      <div class="card historia-card">
        <div class="card-header">
          <div>
            <div class="card-title">Historia #${h.id}</div>
            <div class="card-sub">${fmtDate(h.fecha_creacion)}</div>
          </div>
          ${h.pdf_path
            ? `<button class="btn btn-sm btn-outline" onclick="downloadPDF(${h.id})">&#11015; Descargar PDF</button>`
            : '<span class="badge badge-warning">Sin PDF</span>'}
        </div>
        <div class="diag-label">Diagnóstico</div>
        <div class="diag-value">${h.diagnostico}</div>
        <div class="diag-label">Tratamiento</div>
        <div class="diag-value">${h.tratamiento}</div>
      </div>`).join('');
  } catch (e) {
    $('#historias-inline').innerHTML = emptyState('❌', e.message);
  }
}

function abrirNuevaHistoria(documento) {
  openModal('modal-historia');
  setTimeout(() => { if ($('#hc-doc')) $('#hc-doc').value = documento; }, 60);
}

function downloadPDF(historiaId) {
  fetch(`${API}/historias/${historiaId}/pdf`, {
    headers: { 'Authorization': `Bearer ${state.token}` }
  })
  .then(r => { if (!r.ok) throw new Error('PDF no disponible'); return r.blob(); })
  .then(blob => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `historia_clinica_${historiaId}.pdf`;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  })
  .catch(e => toast(e.message, 'error'));
}

// ── HISTORIAS ─────────────────────────────────────────────────────────────────
async function renderHistorias() {
  const rol = state.user?.rol;
  
  if (rol === 'paciente') {
    $('#topbar-actions').innerHTML = '';
    try {
      const data = await http.get(`/historias/paciente/${state.user.username}`);
      renderHistoriasList(data, 'Mis Registros Clínicos');
    } catch (e) { toast(e.message, 'error'); }
    return;
  }

  // Solo admin y admin_clinica pueden ver todas las historias
  $('#topbar-actions').innerHTML = `
    <div class="search-group">
      <input id="filter-doc" type="text" class="search-input" placeholder="Filtrar por documento del paciente…" />
      <button class="btn btn-primary" onclick="filtrarHistorias()">Filtrar</button>
      <button class="btn btn-outline" onclick="renderHistorias()">Limpiar</button>
    </div>`;

  setTimeout(() => {
    $('#filter-doc')?.addEventListener('keydown', e => { if (e.key === 'Enter') filtrarHistorias(); });
  }, 50);

  try {
    const data = await http.get('/historias/');
    renderHistoriasList(data);
  } catch (e) { toast(e.message, 'error'); }
}

async function filtrarHistorias() {
  const doc = $('#filter-doc')?.value.trim();
  if (!doc) { renderHistorias(); return; }
  try {
    const data = await http.get(`/historias/paciente/${doc}`);
    renderHistoriasList(data, `Historias — Documento ${doc}`);
  } catch (e) { toast(e.message, 'error'); }
}

function renderHistoriasList(list, subtitle = null) {
  if (subtitle) $('#page-title').textContent = subtitle;
  const container = $('#historias-list');
  if (!list.length) { container.innerHTML = emptyState('📋', 'No hay historias clínicas para mostrar.'); return; }

  container.innerHTML = list.map(h => `
    <div class="card historia-card">
      <div class="card-header">
        <div>
          <div class="card-title">${state.user.rol === 'paciente' ? 'Consulta Médica' : 'Paciente #' + h.paciente_id}</div>
          <div class="card-sub">${fmtDate(h.fecha_creacion)} &nbsp;·&nbsp; Hosp. ID ${h.hospital_id}</div>
        </div>
        <div class="card-actions">
           <button class="btn btn-sm btn-outline" onclick="downloadPDF(${h.id})">Descargar PDF</button>
           <span class="badge badge-info">#${h.id}</span>
        </div>
      </div>
      <div class="diag-label">Diagnóstico</div>
      <div class="diag-value">${h.diagnostico}</div>
      <div class="diag-label">Tratamiento</div>
      <div class="diag-value">${h.tratamiento}</div>
    </div>`).join('');
}

// ── NOTIFICACIONES ────────────────────────────────────────────────────────────
async function renderNotificaciones() {
  try {
    const list = await http.get('/notificaciones/me');
    const container = $('#notificaciones-list');
    if (!list.length) { container.innerHTML = emptyState('🔔', 'No tienes notificaciones por ahora.'); return; }

    container.innerHTML = list.map(n => `
      <div class="record-item ${n.leido ? '' : 'unread'}" style="${n.leido ? '' : 'border-left: 4px solid var(--blue)'}">
        <div class="record-icon">${n.leido ? '📩' : '✉️'}</div>
        <div style="flex:1">
          <div class="record-title" style="${n.leido ? '' : 'font-weight:700'}">${n.mensaje}</div>
          <div class="record-sub">${fmtDate(n.timestamp)}</div>
        </div>
        ${!n.leido ? `<button class="btn btn-sm btn-outline" onclick="markNotifAsRead(${n.id})">Marcar leída</button>` : ''}
      </div>`).join('');
  } catch (e) { toast(e.message, 'error'); }
}

async function markNotifAsRead(id) {
  try {
    await http.put(`/notificaciones/${id}/read`);
    renderNotificaciones();
  } catch (e) { toast(e.message, 'error'); }
}

function abrirNuevaCondicion(doc) {
  _currentPatientDoc = doc;
  openModal('modal-condicion');
}

// ── MODALS ────────────────────────────────────────────────────────────────────
function openModal(id) {
  show('#modal-overlay');
  $$('.modal').forEach(m => hide(m));
  show(`#${id}`);
}

function closeModal() {
  hide('#modal-overlay');
  $$('.modal').forEach(m => hide(m));
  $$('.error-msg').forEach(e => { hide(e); e.textContent = ''; });
  // Reset forms
  ['form-hospital', 'form-paciente', 'form-historia', 'form-usuario', 'form-condicion'].forEach(id => $(`#${id}`)?.reset());
  // Show/Hide hospital group based on role
  if (state.user?.rol === 'admin') show('#group-hospital');
  else hide('#group-hospital');
}

// ── FORM: Usuario ─────────────────────────────────────────────────────────────
$('#form-usuario')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = $('#form-usuario-error');
  hide(errEl);
  const btn = e.target.querySelector('[type=submit]');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>';
  try {
    const hospitalVal = $('#u-hospital-select')?.value;
    await http.post('/usuarios/', {
      username:   $('#u-username').value.trim(),
      password:   $('#u-password').value,
      rol:        $('#u-rol').value,
      hospital_id: hospitalVal ? parseInt(hospitalVal) : null,
    });
    closeModal();
    toast('Usuario creado correctamente');
    renderUsuarios();
  } catch (err) {
    show(errEl); errEl.textContent = err.message;
  } finally { btn.disabled = false; btn.textContent = 'Crear Usuario'; }
});

// Close on overlay click
$('#modal-overlay')?.addEventListener('click', e => { if (e.target === $('#modal-overlay')) closeModal(); });

// ── USUARIOS ──────────────────────────────────────────────────────────────────
async function renderUsuarios() {
  const isAdmin = state.user?.rol === 'admin';
  $('#topbar-actions').innerHTML =
    `<button class="btn btn-primary" onclick="openModal('modal-usuario')">+ Nuevo Usuario</button>`;

  const rolSelect = $('#u-rol');
  if (rolSelect) {
    if (!isAdmin) {
      rolSelect.innerHTML = '<option value="medico">Médico</option>';
    } else {
      rolSelect.innerHTML = `
        <option value="medico">Médico</option>
        <option value="admin_clinica">Admin de Clínica</option>
        <option value="admin">Admin del Sistema</option>`;
    }
  }

  // Cargar hospitales si es admin
  if (isAdmin) {
    try {
      const hospitals = await http.get('/hospitales/');
      const select = $('#u-hospital-select');
      select.innerHTML = '<option value="">-- Seleccione un hospital --</option>' + 
        hospitals.map(h => `<option value="${h.id}">${h.nombre}</option>`).join('');
    } catch (e) { console.error('Error cargando hospitales', e); }
  }

  try {
    const list = await http.get('/usuarios/');
    const container = $('#usuarios-list');
    if (!list.length) { container.innerHTML = emptyState('👥', 'No hay usuarios registrados.'); return; }

    const roleLabels = { admin: 'Administrador', admin_clinica: 'Admin. Clínica', medico: 'Médico' };
    const roleColors = { admin: 'badge-info', admin_clinica: 'badge-warning', medico: 'badge-success' };

    container.innerHTML = `
      <table class="data-table">
        <thead><tr><th>Usuario</th><th>Rol</th><th>Hospital</th><th>Creado por</th><th>Acciones</th></tr></thead>
        <tbody>
          ${list.map(u => `
            <tr>
              <td><strong>${u.username}</strong></td>
              <td><span class="badge ${roleColors[u.rol] || 'badge-info'}">${roleLabels[u.rol] || u.rol}</span></td>
              <td>${u.hospital_id ?? '—'}</td>
              <td><small style="color:var(--muted)">${u.creado_por || 'Sistema'}</small></td>
              <td>
                ${u.id !== state.user?.id ? `
                  <button class="btn btn-sm btn-danger" onclick="eliminarUsuario(${u.id}, '${escHtml(u.username)}')">Eliminar</button>
                ` : '<span style="color:var(--muted);font-size:12px">(tú)</span>'}
              </td>
            </tr>`).join('')}
        </tbody>
      </table>`;
  } catch (e) { toast(e.message, 'error'); }
}

async function eliminarUsuario(id, username) {
  if (!confirm(`¿Eliminar usuario "${username}"? Esta acción no se puede deshacer.`)) return;
  try {
    await http.delete(`/usuarios/${id}`);
    toast('Usuario eliminado');
    renderUsuarios();
  } catch (e) { toast(e.message, 'error'); }
}

// ── FORM: Usuario ─────────────────────────────────────────────────────────────
$('#form-hospital')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = $('#form-hospital-error');
  hide(errEl);
  const btn = e.target.querySelector('[type=submit]');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>';
  try {
    await http.post('/hospitales/', {
      nombre:    $('#h-nombre').value.trim(),
      direccion: $('#h-direccion').value.trim(),
    });
    closeModal();
    toast('Hospital registrado correctamente');
    renderHospitales();
  } catch (err) {
    show(errEl); errEl.textContent = err.message;
  } finally { btn.disabled = false; btn.textContent = 'Crear Hospital'; }
});

// ── FORM: Paciente ────────────────────────────────────────────────────────────
$('#form-paciente')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = $('#form-paciente-error');
  hide(errEl);
  const btn = e.target.querySelector('[type=submit]');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>';
  try {
    await http.post('/pacientes/', {
      documento:        $('#p-documento').value.trim(),
      nombre_completo:  $('#p-nombre').value.trim(),
      fecha_expedicion: $('#p-expedicion').value,
      fecha_nacimiento: $('#p-nacimiento').value,
      pin:             $('#p-pin').value,
      consentimiento:   $('#p-consentimiento').checked,
    });
    closeModal();
    toast('Paciente registrado correctamente');
    renderPacientes();
  } catch (err) {
    show(errEl); errEl.textContent = err.message;
  } finally { btn.disabled = false; btn.textContent = 'Registrar Paciente'; }
});

// ── FORM: Historia ────────────────────────────────────────────────────────────
$('#form-historia')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = $('#form-historia-error');
  hide(errEl);
  const btn = e.target.querySelector('[type=submit]');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Generando…';
  try {
    const nueva = await http.post('/historias/', {
      paciente_documento: $('#hc-doc').value.trim(),
      diagnostico:        $('#hc-diagnostico').value.trim(),
      tratamiento:        $('#hc-tratamiento').value.trim(),
    });
    closeModal();
    toast('✅ Historia clínica creada — descargando PDF…');

    // Refrescar la vista según el rol
    const isMedico = state.user?.rol === 'medico';
    if (isMedico && _currentPatientDoc) {
      // Volver al detalle del paciente con las historias actualizadas
      await mostrarDetallesPacienteMedico(_currentPatientDoc, _currentPatientNombre);
    } else {
      renderHistorias();
    }

    // Auto-descarga del PDF
    if (nueva?.id) {
      setTimeout(() => downloadPDF(nueva.id), 800);
    }
  } catch (err) {
    show(errEl); errEl.textContent = err.message;
  } finally { btn.disabled = false; btn.textContent = 'Guardar Historia'; }
});

// ── FORM: Condición Crónica ───────────────────────────────────────────────────
$('#form-condicion')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = $('#form-condicion-error');
  hide(errEl);
  const btn = e.target.querySelector('[type=submit]');
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>';
  try {
    await http.post(`/pacientes/${_currentPatientDoc}/condiciones`, {
      nombre:           $('#cond-nombre').value.trim(),
      fecha_diagnostico: $('#cond-fecha').value,
    });
    closeModal();
    toast('Antecedente registrado correctamente');
    // Refrescar el detalle del paciente para ver la nueva tag
    mostrarDetallesPacienteMedico(_currentPatientDoc, _currentPatientNombre);
  } catch (err) {
    show(errEl); errEl.textContent = err.message;
  } finally { btn.disabled = false; btn.textContent = 'Registrar Condición'; }
});

// ── Boot & Events ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();

  // ── LOGIN form ──────────────────────────────────────────────────────────────
  $('#login-form')?.addEventListener('submit', async (e) => {
    console.log('Login form submitted');
    e.preventDefault();
    const errEl = $('#login-error');
    hide(errEl);
    const btn = $('#login-btn');
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span>';
    try {
      await login($('#login-username').value.trim(), $('#login-password').value);
      await loadMe();
      showApp();
    } catch (err) {
      console.error('Login failed:', err);
      show(errEl); errEl.textContent = err.message || 'Credenciales incorrectas';
    } finally { btn.disabled = false; btn.textContent = 'Iniciar sesión'; }
  });

  // ── Logout ──────────────────────────────────────────────────────────────────
  $('#logout-btn')?.addEventListener('click', logout);

  // ── Sidebar navigation ──────────────────────────────────────────────────────
  $$('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo(link.dataset.section);
    });
  });
});

// ── Utilities ─────────────────────────────────────────────────────────────────
function fmtDate(iso) {
  if (!iso) return '–';
  return new Date(iso).toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });
}

function escHtml(str) {
  return String(str).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function emptyState(icon, msg) {
  return `<div class="empty-state"><div class="empty-state-icon">${icon}</div>${msg}</div>`;
}

function calculateAge(birthDate) {
  if (!birthDate) return '–';
  const today = new Date();
  const birth = new Date(birthDate);
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}

let _currentPatientBirthDate = null;
