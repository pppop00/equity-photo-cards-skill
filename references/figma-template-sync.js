// Rebuild the Tesla Figma white-card template to match the latest skill rules.
// Target file key: jNdCyw4DXyLVPGjSDPLkhE
// Run this through the Figma use_figma tool when MCP rate limits allow.

async function loadFonts() {
  const fonts = [
    { family: 'Arial', style: 'Regular' },
    { family: 'Arial', style: 'Bold' }
  ];
  for (const f of fonts) await figma.loadFontAsync(f);
}
function rgb(hex) {
  const h = hex.replace('#', '');
  return { r: parseInt(h.slice(0,2),16)/255, g: parseInt(h.slice(2,4),16)/255, b: parseInt(h.slice(4,6),16)/255 };
}
function text(parent, chars, x, y, size, fill, style='Regular', width, linePx) {
  const n = figma.createText();
  n.fontName = { family: 'Arial', style };
  n.characters = chars;
  n.fontSize = size;
  n.fills = [{ type:'SOLID', color: rgb(fill) }];
  n.lineHeight = { unit:'PIXELS', value: linePx || Math.round(size * 1.35) };
  n.x = x;
  n.y = y;
  if (width) {
    n.resize(width, n.height);
    n.textAutoResize = 'HEIGHT';
  }
  parent.appendChild(n);
  return n;
}
function rect(parent, x, y, w, h, fill, radius=0, stroke=null, sw=1) {
  const r = figma.createRectangle();
  r.resize(w,h); r.x=x; r.y=y; r.cornerRadius=radius;
  r.fills = [{ type:'SOLID', color: rgb(fill) }];
  if (stroke) { r.strokes = [{ type:'SOLID', color: rgb(stroke) }]; r.strokeWeight = sw; }
  parent.appendChild(r); return r;
}
function bullet(parent, str, x, y, width, size=22) {
  const d = figma.createEllipse();
  d.resize(10,10); d.x=x; d.y=y+12; d.fills=[{ type:'SOLID', color: rgb('#E82127') }];
  parent.appendChild(d);
  return text(parent, str, x+24, y, size, '#111827', 'Regular', width-24, size === 22 ? 32 : 36);
}
function metric(parent, label, value, x, y, w, accent) {
  rect(parent, x, y, w, 110, '#FFFFFF', 18, '#E5E7EB', 1);
  rect(parent, x, y, 8, 110, accent, 18);
  text(parent, label, x+24, y+16, 19, '#667085', 'Regular', w-36, 24);
  text(parent, value, x+24, y+52, 28, '#111827', 'Bold', w-36, 34);
}
function forceBar(parent, label, score, x, y) {
  text(parent, label, x, y, 20, '#475467', 'Regular', undefined, 24);
  rect(parent, x, y+36, 200, 16, '#E5E7EB', 8);
  rect(parent, x, y+36, 200*score/5, 16, score >= 4 ? '#E82127' : '#C9A35D', 8);
  text(parent, `${score}/5`, x+224, y+4, 24, '#111827', 'Bold', undefined, 30);
}
function header(parent, no) {
  text(parent, '金融豹', 72, 56, 26, '#111827', 'Bold', undefined, 30);
  text(parent, 'FINANCE LEOPARD', 72, 92, 14, '#B45309', 'Regular', undefined, 18);
  text(parent, String(no).padStart(2,'0'), 942, 56, 30, '#111827', 'Bold', undefined, 34);
  rect(parent, 72, 126, 936, 2, '#EAECF0');
}
function footer(parent) {
  text(parent, '特斯拉 | 2026年4月8日', 72, 1288, 16, '#667085', 'Regular', undefined, 20);
}
function frame(page, name, x) {
  const f = figma.createFrame();
  f.name = name; f.resize(1080,1350); f.x=x; f.y=0;
  f.fills = [{ type:'SOLID', color: rgb('#FCFCFD') }];
  page.appendChild(f); return f;
}

async function rebuildTeslaTemplate() {
  await loadFonts();
  const page = figma.currentPage;
  page.name = 'Tesla White Social Cards';
  for (const child of [...page.children]) child.remove();
  const frames = [];
  for (let i=0;i<5;i++) frames.push(frame(page, `Tesla Card ${i+1}`, i*1140));

  {
    const f = frames[0]; header(f,1);
    text(f, '每天学习一个公司', 72, 198, 58, '#111827', 'Bold', 760, 66);
    text(f, '特斯拉', 72, 292, 96, '#E82127', 'Bold', 520, 102);
    text(f, 'Tesla, Inc. · TSLA', 78, 412, 26, '#667085', 'Regular', 420, 32);
    text(f, '从高增长电动车制造商，切向“电动车+储能+物理AI平台”叙事。', 78, 454, 28, '#344054', 'Regular', 860, 40);
    metric(f, 'FY2025 总收入', '948.3 亿美元', 72, 566, 280, '#C9A35D');
    metric(f, '汽车收入', '695.3 亿美元', 372, 566, 280, '#E82127');
    metric(f, 'FSD 活跃付费', '110 万账户', 672, 566, 280, '#12B76A');
    rect(f, 72, 736, 936, 324, '#FFF7ED', 28);
    text(f, '公司看点', 108, 786, 34, '#111827', 'Bold', 220, 40);
    text(f, '特斯拉 正从高增长电动车制造商转向“电动车+储能+物理AI平台”。汽车业务仍承压，但 FSD 活跃付费账户已具规模，软件变现开始形成抓手。储能增长更稳，是汽车之外最确定的第二增长引擎。', 108, 842, 24, '#344054', 'Regular', 860, 36);
    footer(f);
  }

  {
    const f = frames[1]; header(f,2);
    text(f, '公司背景 + 行业介绍', 72, 198, 58, '#111827', 'Bold', 720, 66);
    rect(f, 72, 314, 526, 910, '#FFFFFF', 28, '#E5E7EB', 1);
    rect(f, 622, 314, 386, 910, '#FFF7ED', 28);
    text(f, '公司背景', 108, 362, 34, '#111827', 'Bold', 220, 40);
    bullet(f, 'FY2025 总收入 948.27 亿美元，同比下降2.9%。', 108, 424, 446, 24);
    bullet(f, '汽车收入 695.26 亿美元，同比下降10.0%；储能收入 127.71 亿美元，同比增长27.0%。', 108, 504, 446, 24);
    bullet(f, 'FSD 活跃付费账户 110 万，软件付费基盘开始形成。', 108, 620, 446, 24);
    text(f, '行业层面', 108, 786, 34, '#111827', 'Bold', 220, 40);
    text(f, '从行业层面看，Tesla 所处的是全球电动车与智能驾驶交叉赛道，其竞争逻辑已由单纯的电动化渗透转向价格、产品、软件、制造效率和算力的复合博弈。供需与上游约束仍在强化。', 108, 844, 24, '#344054', 'Regular', 446, 37);
    text(f, '波特五力', 656, 362, 34, '#111827', 'Bold', 180, 40);
    forceBar(f, '供应商', 3, 656, 430);
    forceBar(f, '买方', 4, 656, 540);
    forceBar(f, '新进入者', 4, 656, 650);
    forceBar(f, '替代品', 3, 656, 760);
    forceBar(f, '竞争强度', 5, 656, 870);
    text(f, '一句结论', 656, 1018, 30, '#111827', 'Bold', 180, 36);
    text(f, '硬件竞争已非常激烈，软件、自动驾驶与能源生态才是估值上限所在。', 656, 1066, 22, '#344054', 'Regular', 300, 34);
    footer(f);
  }

  {
    const f = frames[2]; header(f,3);
    text(f, '实际 Revenue 分析', 72, 198, 58, '#111827', 'Bold', 620, 66);
    rect(f, 72, 314, 936, 856, '#FFFFFF', 28, '#E5E7EB', 1);
    text(f, 'FY2025 收入流', 108, 360, 34, '#111827', 'Bold', 260, 40);
    const rows = [
      ['总收入','948.3 亿美元',948.3,'#C9A35D'],
      ['营业成本','777.3 亿美元',777.3,'#E82127'],
      ['毛利润','170.9 亿美元',170.9,'#12B76A'],
      ['营业利润','43.5 亿美元',43.5,'#1570EF'],
      ['净利润','37.9 亿美元',37.9,'#111827'],
    ];
    const max = 948.3;
    rows.forEach((item, idx) => {
      const y = 438 + idx*56;
      text(f, item[0], 108, y, 22, '#475467', 'Regular', 120, 28);
      rect(f, 244, y+6, 500, 22, '#EAECF0', 11);
      rect(f, 244, y+6, 500*item[2]/max, 22, item[3], 11);
      text(f, item[1], 782, y-6, 26, '#111827', 'Bold', 170, 32);
    });
    metric(f, '毛利率', '18.0%', 108, 710, 220, '#12B76A');
    metric(f, '营业利润率', '4.6%', 350, 710, 220, '#1570EF');
    metric(f, '净利率', '4.0%', 592, 710, 220, '#E82127');
    rect(f, 72, 896, 936, 292, '#FFF7ED', 28);
    text(f, '怎么理解这张图', 108, 942, 34, '#111827', 'Bold', 260, 40);
    bullet(f, '收入大头依然来自硬件交付，高成本制造先吃掉大部分收入。', 108, 1002, 820, 24);
    bullet(f, '利润池还不够像软件公司，经营杠杆修复要靠高毛利业务占比提升。', 108, 1070, 820, 24);
    bullet(f, '真正支撑估值弹性的，不是卖出多少辆车，而是 FSD、Robotaxi 与储能渗透。', 108, 1138, 820, 24);
    footer(f);
  }

  {
    const f = frames[3]; header(f,4);
    text(f, '实际业务 + 未来展望', 72, 198, 58, '#111827', 'Bold', 700, 66);
    rect(f, 72, 314, 434, 906, '#FFFFFF', 28, '#E5E7EB', 1);
    rect(f, 534, 314, 474, 906, '#FFFFFF', 28, '#E5E7EB', 1);
    text(f, '现在靠什么赚钱', 108, 362, 32, '#111827', 'Bold', 240, 38);
    bullet(f, '整车仍是收入主体，财务现实仍由汽车业务决定，利润池依旧主要靠汽车承载。', 108, 424, 350, 22);
    bullet(f, '储能业务增长更稳，已经成为第二增长引擎，也是汽车之外更确定的扩张方向。', 108, 530, 350, 22);
    bullet(f, 'FSD 110 万活跃付费账户，说明软件变现不是空故事，而是已有真实付费基础。', 108, 636, 350, 22);
    bullet(f, '现金储备充足，给 AI、Robotaxi 与机器人业务留出了继续投入和试错的时间。', 108, 742, 350, 22);
    text(f, '未来 2-3 年看什么', 570, 362, 32, '#111827', 'Bold', 280, 38);
    bullet(f, '估值锚点正从卖车切向软件期权，关键变量是 FSD 渗透率、用户留存和真实付费意愿。', 570, 424, 368, 22);
    bullet(f, 'AI 算力、机器人产线和数据中心会继续抬高资本开支，也会拉高对执行效率的要求。', 570, 548, 368, 22);
    bullet(f, '若竞争对手的高阶辅助驾驶持续逼近，Tesla 的软件溢价和估值想象空间会被重估。', 570, 672, 368, 22);
    bullet(f, '股价能否站稳，最终要看现金流、软件用户数与高毛利业务占比能否持续兑现。', 570, 796, 368, 22);
    rect(f, 570, 980, 378, 196, '#FFF7ED', 24);
    text(f, '一句判断', 602, 1028, 28, '#111827', 'Bold', 160, 34);
    text(f, '汽车现金流承压，软件期权在抬估值。短期不便宜，中期看兑现。', 602, 1076, 316, 20, '#344054', 'Regular', 316, 30);
    footer(f);
  }

  {
    const f = frames[4]; header(f,5);
    text(f, '金融豹', 72, 214, 110, '#111827', 'Bold', 420, 116);
    text(f, '一句话看特斯拉', 78, 346, 46, '#B45309', 'Bold', 360, 52);
    text(f, '汽车现金流承压，软件期权在抬估值。', 78, 476, 52, '#E82127', 'Bold', 760, 64);
    rect(f, 72, 646, 936, 360, '#FFF7ED', 28);
    text(f, '今日总结', 108, 696, 34, '#111827', 'Bold', 220, 40);
    bullet(f, '主业仍靠整车承载利润，汽车收入同比下滑。', 108, 758, 820, 24);
    bullet(f, '储能增长更稳，是第二增长引擎。', 108, 832, 820, 24);
    bullet(f, '估值天花板要看 FSD、Robotaxi 与软件付费兑现。', 108, 906, 820, 24);
    text(f, '关注金融豹，每天学习一个公司。', 72, 1098, 34, '#111827', 'Bold', 520, 40);
    for (const [x,y,s] of [[900,218,88],[980,360,64],[900,520,74]]) {
      const c = figma.createEllipse();
      c.resize(s,s); c.x=x; c.y=y; c.fills=[];
      c.strokes=[{ type:'SOLID', color: rgb('#E82127') }]; c.strokeWeight=3;
      f.appendChild(c);
    }
    footer(f);
  }

  figma.currentPage.selection = frames;
  figma.viewport.scrollAndZoomIntoView(frames);
  figma.notify('Figma template synced to latest skill rules.');
}

rebuildTeslaTemplate();
