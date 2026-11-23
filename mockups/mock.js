/* 随便记 UI 原型 · 交互与模拟数据 */

const ICONS = {
  key: '<circle cx="8.5" cy="15.5" r="3.5"/><path d="M11 13 20 4"/><path d="m17 5 2 2"/><path d="m14.5 7.5 2 2"/>',
  bulb: '<path d="M9 18h6"/><path d="M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.7.5 1.1 1.3 1.1 2.2h5c0-.9.4-1.7 1.1-2.2A6 6 0 0 0 12 3Z"/>',
  wallet: '<rect x="3" y="6" width="18" height="13" rx="3"/><path d="M3 9.5h18"/><path d="M16 13.5h2"/>',
  sparkles: '<path d="M12 3.5 13.8 9l5.5 1.8-5.5 1.8L12 18l-1.8-5.4L4.7 10.8 10.2 9 12 3.5Z"/><path d="M19 15.5l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7.7-2Z"/>',
  shield: '<path d="M12 3 19 6v5c0 4.4-2.9 7.4-7 9-4.1-1.6-7-4.6-7-9V6l7-3Z"/><path d="m9 12 2 2 4-4"/>',
  sliders: '<path d="M4 7h9"/><path d="M18 7h2"/><path d="M4 17h4"/><path d="M13 17h7"/><circle cx="15.5" cy="7" r="2"/><circle cx="10.5" cy="17" r="2"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.4-3.4"/>',
  plus: '<path d="M12 5v14"/><path d="M5 12h14"/>',
  edit: '<path d="M15.5 5.5l3 3L8 19H5v-3L15.5 5.5Z"/>',
  trash: '<path d="M4 7h16"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M6 7l1 13h10l1-13"/><path d="M9 7V4h6v3"/>',
  x: '<path d="M6 6l12 12"/><path d="M18 6 6 18"/>',
  eye: '<path d="M2.5 12S6 6 12 6s9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z"/><circle cx="12" cy="12" r="2.5"/>',
  eyeoff: '<path d="M3 3l18 18"/><path d="M10.6 6.2A9.8 9.8 0 0 1 12 6c6 0 9.5 6 9.5 6a17 17 0 0 1-3.2 3.8"/><path d="M6.3 7.4A17.5 17.5 0 0 0 2.5 12S6 18 12 18c1 0 2-.2 2.9-.5"/>',
  copy: '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/>',
  chevron: '<path d="m9 5 7 7-7 7"/>',
  file: '<path d="M6 3h8l4 4v14H6V3Z"/><path d="M14 3v4h4"/><path d="M9 12h6"/><path d="M9 16h4"/>'
};

function icon(name, size = 18) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]}</svg>`;
}

const DATA = {
  accounts: {
    name: '账号密码', en: 'ACCOUNTS', icon: 'key',
    filters: ['全部', '工作', '邮箱', '社交', '视频', '购物', '论坛'],
    columns: ['类型', '网站', '用户名', '网址', '最近更新'],
    cols: '92px 1.1fr 1.2fr 1.5fr 104px',
    rows: [
      { type: '工作', site: 'GitHub', user: 'wei.dev@gmail.com', password: 'gh-2026-vault', url: 'github.com', notes: '开启两步验证', updated: '今天 09:42' },
      { type: '邮箱', site: 'Gmail', user: 'wei.dev@gmail.com', password: 'mail-pass-2026', url: 'mail.google.com', notes: '主力邮箱', updated: '昨天 21:10' },
      { type: '视频', site: '哔哩哔哩', user: '阿伟的实验室', password: 'bili-2026', url: 'bilibili.com', notes: '', updated: '10月18日' },
      { type: '购物', site: '淘宝', user: 'wei_1996', password: 'tb-2026', url: 'taobao.com', notes: '收货地址已更新', updated: '10月15日' },
      { type: '社交', site: 'Notion', user: 'wei@workspace', password: 'notion-2026', url: 'notion.so', notes: '团队空间', updated: '10月12日' },
      { type: '论坛', site: 'V2EX', user: 'wei_dev', password: 'v2ex-2026', url: 'v2ex.com', notes: '', updated: '10月09日' },
      { type: '工作', site: '公司邮箱', user: 'wei@company.cn', password: 'corp-2026', url: 'mail.company.cn', notes: 'VPN 内网访问', updated: '09月28日' }
    ]
  },
  ideas: {
    name: '想法记录', en: 'IDEAS', icon: 'bulb',
    filters: ['全部', '灵感', '产品', '生活', '阅读'],
    columns: ['标题', '内容', '标签', '最近更新'],
    cols: '1.25fr 1.9fr 190px 92px',
    rows: [
      { title: '把周报做成语音摘要', content: '录制 3 分钟口述，自动转文字并生成结构化周报…', tags: ['效率', 'AI'], group: '灵感', updated: '今天 11:20' },
      { title: '本地优先的密码管理器', content: '所有数据只存在本机，主密码派生密钥，不联网…', tags: ['产品', '安全'], group: '产品', updated: '昨天' },
      { title: '周末去苏州的路线', content: '平江路 → 苏州博物馆 → 金鸡湖日落，避开周六上午…', tags: ['生活'], group: '生活', updated: '10月17日' },
      { title: '给日记加一个“随机回顾”', content: '每天打开时抽取一条一年前的记录，制造偶然的回忆…', tags: ['产品', '灵感'], group: '灵感', updated: '10月14日' },
      { title: '读《创造者的悖论》', content: '记录型工具的价值不在存储，而在于重新遇见过去的自己…', tags: ['阅读'], group: '阅读', updated: '10月08日' },
      { title: '提示词：结构化复盘', content: '你是一名严谨的复盘教练，请从目标、行动、偏差三个维度…', tags: ['AI', '写作'], group: '产品', updated: '09月30日' }
    ]
  },
  wallets: {
    name: '钱包地址', en: 'WALLETS', icon: 'wallet',
    filters: ['全部', 'BTC', 'ETH', 'SOL'],
    columns: ['名称', '地址', '类型', '备注'],
    cols: '1fr 1.7fr 84px 1.35fr',
    rows: [
      { name: '主力冷钱包', address: 'bc1q9x8v…7k2m4p', type: 'BTC', notes: 'Ledger Nano X · 助记词离线保存', group: 'BTC' },
      { name: '以太坊日常', address: '0x7A3f…9E2b', type: 'ETH', notes: 'MetaMask · 小额交互', group: 'ETH' },
      { name: 'Solana 实验', address: '7xKX…Qm9L', type: 'SOL', notes: 'Phantom · 测试用途', group: 'SOL' },
      { name: '交易所充值', address: '0x51Bc…33Aa', type: 'ETH', notes: '仅用于充提，不长期存放', group: 'ETH' },
      { name: '观察地址', address: 'bc1p5…8sQe', type: 'BTC', notes: '只读地址，追踪长期持仓', group: 'BTC' }
    ]
  },
  prompts: {
    name: 'AI 提示词', en: 'AI PROMPTS', icon: 'sparkles',
    filters: ['全部', '写作', '编程', '分析'],
    columns: ['标题', '内容', '分类', '最近更新'],
    cols: '1fr 1.9fr 110px 92px',
    rows: [
      { title: '深度复盘教练', content: '你是一名严谨的复盘教练，请从目标、行动、偏差…', category: '分析', group: '分析', updated: '今天' },
      { title: '长文结构化改写', content: '在不改变事实的前提下，将以下长文改写为分点笔记…', category: '写作', group: '写作', updated: '昨天' },
      { title: '代码审查清单', content: '请以资深工程师视角审查以下代码，优先指出正确性…', category: '编程', group: '编程', updated: '10月16日' },
      { title: '产品需求澄清', content: '你是产品经理，请针对以下模糊需求提出 5 个澄清问题…', category: '分析', group: '分析', updated: '10月11日' },
      { title: '中文润色', content: '保留原意与语气，仅优化表达，不要扩写，不要解释…', category: '写作', group: '写作', updated: '10月02日' }
    ]
  }
};

const FORMS = {
  accounts: [
    { key: 'type', label: '类型', type: 'select', options: ['邮箱', '视频', '论坛', '社交', '购物', '工作', '其他'], half: true },
    { key: 'site', label: '网站', placeholder: '例如 GitHub', half: true },
    { key: 'user', label: '用户名', placeholder: '邮箱或用户名', half: true },
    { key: 'password', label: '密码', type: 'password', placeholder: '输入密码', half: true },
    { key: 'url', label: '网址', placeholder: 'https://', full: true },
    { key: 'notes', label: '备注', type: 'textarea', placeholder: '补充说明（可选）', full: true }
  ],
  ideas: [
    { key: 'title', label: '标题', placeholder: '给这个想法起个名字', full: true },
    { key: 'content', label: '内容', type: 'textarea', placeholder: '写下你的想法…', full: true },
    { key: 'tags', label: '标签', placeholder: '用逗号分隔，例如：效率, AI', full: true }
  ],
  wallets: [
    { key: 'name', label: '名称', placeholder: '例如 主力冷钱包', half: true },
    { key: 'type', label: '类型', type: 'select', options: ['BTC', 'ETH', 'SOL', '其他'], half: true },
    { key: 'address', label: '地址', placeholder: '钱包地址', full: true },
    { key: 'notes', label: '备注', type: 'textarea', placeholder: '用途、保管方式等（可选）', full: true }
  ],
  prompts: [
    { key: 'title', label: '标题', placeholder: '例如 深度复盘教练', half: true },
    { key: 'category', label: '分类', type: 'select', options: ['写作', '编程', '分析', '其他'], half: true },
    { key: 'content', label: '内容', type: 'textarea', placeholder: '粘贴提示词正文…', full: true }
  ]
};

const state = { cat: 'accounts', filter: '全部', query: '', selected: null };

function esc(value) {
  return String(value ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function visibleEntries() {
  const rows = DATA[state.cat].rows;
  const q = state.query.trim().toLowerCase();
  return rows
    .map((row, index) => ({ row, index }))
    .filter(({ row }) => {
      const groupOk = state.filter === '全部' || row.group === state.filter || row.type === state.filter || row.account_type === state.filter;
      if (!groupOk) return false;
      if (!q) return true;
      return Object.values(row).join(' ').toLowerCase().includes(q);
    });
}

function rowTitle(row) {
  return row.title || row.site || row.name || '这条记录';
}

function rowCells(row) {
  switch (state.cat) {
    case 'accounts':
      return [
        `<span class="badge">${esc(row.type)}</span>`,
        `<div class="cell strong"><i class="dot"></i>${esc(row.site)}</div>`,
        `<div class="cell">${esc(row.user)}</div>`,
        `<div class="cell mono">${esc(row.url)}</div>`,
        `<div class="cell muted">${esc(row.updated)}</div>`
      ];
    case 'ideas':
      return [
        `<div class="cell strong">${esc(row.title)}</div>`,
        `<div class="cell muted">${esc(row.content)}</div>`,
        `<div class="cell tags">${(row.tags || []).map(tag => `<span class="tag">${esc(tag)}</span>`).join('')}</div>`,
        `<div class="cell muted">${esc(row.updated)}</div>`
      ];
    case 'wallets':
      return [
        `<div class="cell strong"><i class="dot"></i>${esc(row.name)}</div>`,
        `<div class="cell mono">${esc(row.address)}</div>`,
        `<span class="badge">${esc(row.type)}</span>`,
        `<div class="cell muted">${esc(row.notes)}</div>`
      ];
    case 'prompts':
      return [
        `<div class="cell strong">${esc(row.title)}</div>`,
        `<div class="cell muted">${esc(row.content)}</div>`,
        `<div class="cell"><span class="tag">${esc(row.category)}</span></div>`,
        `<div class="cell muted">${esc(row.updated)}</div>`
      ];
    default:
      return [];
  }
}

function renderChrome() {
  const cat = DATA[state.cat];
  document.getElementById('eyebrow').textContent = cat.en;
  document.getElementById('title').textContent = cat.name;
  document.getElementById('searchInput').placeholder = state.cat === 'accounts' ? '搜索网站、用户名或备注…' : '搜索记录…';
  document.querySelectorAll('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.cat === state.cat));
  document.querySelectorAll('.nav-count').forEach(el => { el.textContent = DATA[el.dataset.count].rows.length; });
  renderChips();
  renderTable();
}

function renderChips() {
  const cat = DATA[state.cat];
  document.getElementById('chips').innerHTML = cat.filters
    .map(f => `<button class="chip${f === state.filter ? ' active' : ''}" data-filter="${esc(f)}">${esc(f)}</button>`)
    .join('');
}

function renderTable() {
  const cat = DATA[state.cat];
  const entries = visibleEntries();
  const filtering = state.query.trim() || state.filter !== '全部';
  document.getElementById('subtitle').innerHTML = filtering
    ? `<b>${entries.length}</b> / ${cat.rows.length} 条记录 · 本地加密存储`
    : `<b>${cat.rows.length}</b> 条记录 · 本地加密存储`;

  document.querySelector('.table-card').style.setProperty('--cols', cat.cols);
  document.getElementById('tableHead').innerHTML = cat.columns.map(c => `<span>${esc(c)}</span>`).join('');

  const body = document.getElementById('tableBody');
  if (!entries.length) {
    body.innerHTML = `<div class="empty">${icon('file', 26)}<strong>没有匹配的记录</strong><span>换个关键词，或清空筛选条件试试</span></div>`;
  } else {
    body.innerHTML = entries.map(({ row, index }) => `
      <div class="row${state.selected === row ? ' selected' : ''}" data-index="${index}">
        ${rowCells(row).join('')}
      </div>`).join('');
  }

  const hasSelection = !!state.selected && cat.rows.includes(state.selected);
  document.getElementById('editBtn').disabled = !hasSelection;
  document.getElementById('deleteBtn').disabled = !hasSelection;
}

function selectRow(row) {
  state.selected = state.selected === row ? null : row;
  renderTable();
}

function openForm(mode) {
  const cat = DATA[state.cat];
  const editing = mode === 'edit' ? state.selected : null;
  const fields = FORMS[state.cat];
  const body = fields.map(field => {
    const value = editing ? (editing[field.key] ?? '') : '';
    const label = `<label>${esc(field.label)}</label>`;
    let control;
    if (field.type === 'select') {
      const options = field.options.map(opt => `<option${opt === value ? ' selected' : ''}>${esc(opt)}</option>`).join('');
      control = `<div class="select-wrap"><select class="control" data-key="${esc(field.key)}">${options}</select>${icon('chevron', 13)}</div>`;
    } else if (field.type === 'textarea') {
      control = `<textarea class="control" data-key="${esc(field.key)}" placeholder="${esc(field.placeholder || '')}">${esc(value)}</textarea>`;
    } else if (field.type === 'password') {
      control = `<div class="input-wrap"><input class="control" type="password" data-key="${esc(field.key)}" value="${esc(value)}" placeholder="${esc(field.placeholder || '')}"><button class="icon-btn" data-eye type="button">${icon('eye', 15)}</button></div>`;
    } else {
      control = `<input class="control" data-key="${esc(field.key)}" value="${esc(value)}" placeholder="${esc(field.placeholder || '')}">`;
    }
    return `<div class="field${field.full ? ' full' : ''}">${label}${control}</div>`;
  }).join('');

  const root = document.getElementById('modal-root');
  root.innerHTML = `
    <div class="modal-mask" id="modalMask">
      <div class="modal" role="dialog" aria-modal="true">
        <div class="modal-head">
          <div>
            <div class="modal-eyebrow">${esc(cat.name)}</div>
            <h2 class="modal-title">${mode === 'add' ? '添加记录' : '编辑记录'}</h2>
          </div>
          <button class="icon-btn" data-close>${icon('x', 15)}</button>
        </div>
        <div class="modal-body"><div class="form-grid">${body}</div></div>
        <div class="modal-foot">
          <button class="btn btn-ghost" data-close>取消</button>
          <button class="btn btn-primary" data-save>保存</button>
        </div>
      </div>
    </div>`;
  const mask = document.getElementById('modalMask');
  requestAnimationFrame(() => mask.classList.add('open'));

  mask.addEventListener('mousedown', event => { if (event.target === mask) closeModal(); });
  mask.querySelectorAll('[data-close]').forEach(btn => btn.addEventListener('click', closeModal));
  const eye = mask.querySelector('[data-eye]');
  if (eye) {
    eye.addEventListener('click', () => {
      const input = eye.parentElement.querySelector('input');
      input.type = input.type === 'password' ? 'text' : 'password';
      eye.innerHTML = icon(input.type === 'password' ? 'eye' : 'eyeoff', 15);
    });
  }
  mask.querySelector('[data-save]').addEventListener('click', () => saveForm(mode));
  setTimeout(() => { const first = mask.querySelector('input, textarea'); if (first) first.focus(); }, 60);
}

function saveForm(mode) {
  const cat = DATA[state.cat];
  const values = {};
  document.querySelectorAll('#modalMask [data-key]').forEach(el => { values[el.dataset.key] = el.value.trim(); });

  let row;
  if (state.cat === 'accounts') {
    row = { type: values.type || '其他', site: values.site || '未命名网站', user: values.user || '', password: values.password || '', url: values.url || '', notes: values.notes || '', updated: '刚刚' };
  } else if (state.cat === 'ideas') {
    const tags = (values.tags || '').split(/[,，]/).map(t => t.trim()).filter(Boolean);
    row = { title: values.title || '未命名想法', content: values.content || '', tags, group: tags[0] || '灵感', updated: '刚刚' };
  } else if (state.cat === 'wallets') {
    row = { name: values.name || '未命名钱包', address: values.address || '', type: values.type || '其他', notes: values.notes || '', group: values.type || '其他' };
  } else {
    row = { title: values.title || '未命名提示词', content: values.content || '', category: values.category || '其他', group: values.category || '其他', updated: '刚刚' };
  }

  if (mode === 'add') {
    cat.rows.unshift(row);
    state.selected = row;
    state.filter = '全部';
    state.query = '';
    document.getElementById('searchInput').value = '';
    renderChrome();
    toast('已添加一条演示记录');
  } else if (state.selected) {
    Object.assign(state.selected, row, { updated: '刚刚' });
    renderTable();
    toast('已保存修改（演示数据）');
  }
  closeModal();
}

function openConfirm() {
  if (!state.selected) return;
  const row = state.selected;
  const root = document.getElementById('modal-root');
  root.innerHTML = `
    <div class="modal-mask" id="modalMask">
      <div class="modal" style="width:min(430px,100%)" role="dialog" aria-modal="true">
        <div class="modal-head">
          <div>
            <div class="modal-eyebrow">删除记录</div>
            <h2 class="modal-title">确定删除？</h2>
          </div>
          <button class="icon-btn" data-close>${icon('x', 15)}</button>
        </div>
        <div class="modal-body">
          <p style="font-size:12.5px;line-height:1.7;color:var(--muted);margin:2px 0 16px">
            「${esc(rowTitle(row))}」将从本地加密数据中移除，此操作无法撤销。
          </p>
        </div>
        <div class="modal-foot">
          <button class="btn btn-ghost" data-close>取消</button>
          <button class="btn btn-primary" data-delete style="background:var(--danger);color:#fff">删除</button>
        </div>
      </div>
    </div>`;
  const mask = document.getElementById('modalMask');
  requestAnimationFrame(() => mask.classList.add('open'));
  mask.addEventListener('mousedown', event => { if (event.target === mask) closeModal(); });
  mask.querySelectorAll('[data-close]').forEach(btn => btn.addEventListener('click', closeModal));
  mask.querySelector('[data-delete]').addEventListener('click', () => {
    const rows = DATA[state.cat].rows;
    const index = rows.indexOf(state.selected);
    if (index >= 0) rows.splice(index, 1);
    state.selected = null;
    closeModal();
    renderChrome();
    toast('演示记录已删除');
  });
}

function openSettings() {
  const root = document.getElementById('modal-root');
  root.innerHTML = `
    <div class="modal-mask" id="modalMask">
      <div class="modal" style="width:min(500px,100%)" role="dialog" aria-modal="true">
        <div class="modal-head">
          <div>
            <div class="modal-eyebrow">Preferences</div>
            <h2 class="modal-title">设置</h2>
          </div>
          <button class="icon-btn" data-close>${icon('x', 15)}</button>
        </div>
        <div class="modal-body">
          <div class="settings-block">
            <h3>安全</h3>
            <div class="set-row">
              <div>
                <div class="set-title">一天内免密登录</div>
                <div class="set-desc">主密码保存在系统钥匙串，24 小时后自动失效</div>
              </div>
              <button class="switch" data-switch aria-label="一天内免密登录"></button>
            </div>
          </div>
          <div class="settings-block">
            <h3>账号密码分类</h3>
            <div class="type-tags">
              ${['邮箱', '视频', '论坛', '社交', '购物', '工作', '其他'].map(t => `<span class="tag">${t}</span>`).join('')}
              <span class="tag" style="background:transparent;border:1px dashed var(--line);color:var(--muted)">+ 新增</span>
            </div>
          </div>
        </div>
        <div class="modal-foot">
          <button class="btn btn-ghost" data-close>取消</button>
          <button class="btn btn-primary" data-settings-save>保存</button>
        </div>
      </div>
    </div>`;
  const mask = document.getElementById('modalMask');
  requestAnimationFrame(() => mask.classList.add('open'));
  mask.addEventListener('mousedown', event => { if (event.target === mask) closeModal(); });
  mask.querySelectorAll('[data-close]').forEach(btn => btn.addEventListener('click', closeModal));
  mask.querySelector('[data-switch]').addEventListener('click', event => event.currentTarget.classList.toggle('on'));
  mask.querySelector('[data-settings-save]').addEventListener('click', () => {
    closeModal();
    toast('设置已保存（演示）');
  });
}

function closeModal() {
  const mask = document.getElementById('modalMask');
  if (!mask) return;
  mask.classList.remove('open');
  setTimeout(() => {
    const root = document.getElementById('modal-root');
    if (root.contains(mask)) root.innerHTML = '';
  }, 180);
}

let toastTimer;
function toast(message) {
  const el = document.getElementById('toast');
  el.textContent = message;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 2200);
}

function mount() {
  const nav = Object.entries(DATA).map(([key, cat]) => `
    <button class="nav-item" data-cat="${key}">
      <span class="nav-icon">${icon(cat.icon, 18)}</span>
      <span class="nav-text">${cat.name}<span class="nav-en">${cat.en}</span></span>
      <span class="nav-count" data-count="${key}">${cat.rows.length}</span>
    </button>`).join('');

  document.getElementById('app').innerHTML = `
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">随</div>
        <div>
          <div class="brand-name">随便记</div>
          <div class="brand-sub">Private Ledger</div>
        </div>
      </div>
      <nav class="nav">
        <div class="nav-label">我的记录</div>
        ${nav}
      </nav>
      <div class="side-foot">
        <div class="secure-note">${icon('shield', 14)}<span>本地加密 · 仅此设备可见</span></div>
        <button class="side-settings" id="settingsBtn">
          ${icon('sliders', 16)}<span>设置</span><span class="side-version">v1.0.0</span>
        </button>
      </div>
    </aside>
    <main class="main">
      <header class="topbar">
        <div class="page-title">
          <div class="eyebrow" id="eyebrow"></div>
          <h1 id="title"></h1>
          <p class="subtitle" id="subtitle"></p>
        </div>
        <div class="top-actions">
          <label class="search">
            ${icon('search', 16)}<input id="searchInput" placeholder="搜索记录…"><kbd>Ctrl K</kbd>
          </label>
          <button class="btn btn-primary" id="addBtn">${icon('plus', 15)}<span>添加</span></button>
        </div>
      </header>
      <div class="toolbar">
        <div class="chips" id="chips"></div>
        <div class="row-actions">
          <button class="btn btn-ghost" id="editBtn" disabled>${icon('edit', 14)}编辑</button>
          <button class="btn btn-danger-ghost" id="deleteBtn" disabled>${icon('trash', 14)}删除</button>
        </div>
      </div>
      <section class="table-card">
        <div class="table-head" id="tableHead"></div>
        <div class="table-body" id="tableBody"></div>
      </section>
      <footer class="hint">
        ${icon('copy', 13)}<span>右键任意记录可快速复制字段</span>
        <span class="spacer"></span><span>数据以 AES-256 加密保存在本地</span>
      </footer>
    </main>`;

  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      state.cat = btn.dataset.cat;
      state.filter = '全部';
      state.query = '';
      state.selected = null;
      document.getElementById('searchInput').value = '';
      renderChrome();
    });
  });

  document.getElementById('chips').addEventListener('click', event => {
    const chip = event.target.closest('.chip');
    if (!chip) return;
    state.filter = chip.dataset.filter;
    renderChips();
    renderTable();
  });

  document.getElementById('tableBody').addEventListener('click', event => {
    const rowEl = event.target.closest('.row');
    if (!rowEl) return;
    selectRow(DATA[state.cat].rows[Number(rowEl.dataset.index)]);
  });

  document.getElementById('tableBody').addEventListener('dblclick', event => {
    const rowEl = event.target.closest('.row');
    if (!rowEl) return;
    state.selected = DATA[state.cat].rows[Number(rowEl.dataset.index)];
    openForm('edit');
  });

  document.getElementById('searchInput').addEventListener('input', event => {
    state.query = event.target.value;
    renderTable();
  });

  document.getElementById('addBtn').addEventListener('click', () => {
    state.selected = null;
    renderTable();
    openForm('add');
  });

  document.getElementById('editBtn').addEventListener('click', () => {
    if (state.selected) openForm('edit');
  });

  document.getElementById('deleteBtn').addEventListener('click', openConfirm);
  document.getElementById('settingsBtn').addEventListener('click', openSettings);

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeModal();
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      document.getElementById('searchInput').focus();
    }
  });

  renderChrome();
}

mount();
