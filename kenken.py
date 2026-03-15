#!/usr/bin/env python3
"""
KenKen Puzzle Generator
Run with:  python3 kenken.py
Opens a fully self-contained KenKen puzzle in your default browser.
No external dependencies required.
"""

import webbrowser
import tempfile
import os

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KenKen Puzzle</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:      #0d0d14;
    --surface: #1a1a28;
    --border:  #2e2e42;
    --accent:  #f5c542;
    --text:    #f0eee8;
    --muted:   #888;
    --green:   #6fcf97;
    --red:     #eb5757;
    --blue:    #a0cfff;
  }

  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem 1rem 4rem;
  }

  /* ── Header ── */
  header { text-align: center; margin-bottom: 2rem; }
  .logo {
    font-family: 'Space Mono', monospace;
    font-size: clamp(2rem, 6vw, 3.5rem);
    font-weight: 700;
    letter-spacing: -2px;
    line-height: 1;
  }
  .logo span { color: var(--accent); }
  .tagline {
    font-size: 0.78rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.4rem;
  }

  /* ── Controls bar ── */
  .controls {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
    justify-content: center;
    margin-bottom: 2rem;
  }
  .ctrl-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--muted);
  }
  select, button {
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem;
    border-radius: 4px;
    cursor: pointer;
    outline: none;
    transition: all 0.15s;
  }
  select {
    background: var(--surface);
    border: 1px solid #444;
    color: var(--text);
    padding: 0.5rem 1rem;
  }
  select:hover, select:focus { border-color: var(--accent); }

  button {
    padding: 0.5rem 1.3rem;
    font-weight: 700;
    letter-spacing: 1px;
    border: none;
  }
  .btn-primary { background: var(--accent); color: #0d0d14; }
  .btn-primary:hover { background: #ffd966; }
  .btn-primary:active { transform: scale(0.97); }
  .btn-secondary {
    background: transparent;
    border: 1px solid #444;
    color: var(--text);
  }
  .btn-secondary:hover { border-color: var(--accent); color: var(--accent); }

  .status-badge {
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    padding: 0.4rem 1rem;
    border-radius: 4px;
    border: 1px solid #444;
    color: var(--muted);
    min-width: 110px;
    text-align: center;
    transition: all 0.2s;
  }
  .status-badge.loading { color: var(--accent); border-color: var(--accent); animation: pulse 1s infinite; }
  .status-badge.ok      { color: var(--green);  border-color: var(--green); }
  .status-badge.err     { color: var(--red);    border-color: var(--red); }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  /* ── Game area ── */
  #gameArea {
    display: flex;
    gap: 2rem;
    align-items: flex-start;
    flex-wrap: wrap;
    justify-content: center;
  }

  /* ── Grid ── */
  #gridWrap { position: relative; }
  #grid {
    display: inline-grid;
    border: 2.5px solid var(--accent);
    background: var(--surface);
  }

  .cell {
    position: relative;
    width: 70px; height: 70px;
    border: 1px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    transition: background 0.1s;
    user-select: none;
  }
  .cell:hover { background: #22223a; }
  .cell.selected { background: #2a2a44 !important; outline: 2px solid var(--accent); outline-offset: -2px; }
  .cell.correct  { background: #152515 !important; }
  .cell.wrong    { background: #2a1515 !important; }

  .cage-hint {
    position: absolute;
    top: 3px; left: 4px;
    font-family: 'Space Mono', monospace;
    font-size: 0.6rem; font-weight: 700;
    color: var(--accent);
    pointer-events: none; z-index: 2;
    line-height: 1;
  }
  .cell-val {
    font-family: 'Space Mono', monospace;
    font-size: 1.5rem; font-weight: 700;
    color: var(--blue);
    pointer-events: none; z-index: 1;
  }
  .cell-val.user-ok  { color: var(--green); }
  .cell-val.user-err { color: var(--red); }

  /* Cage borders */
  .cbt { border-top:    2.5px solid var(--accent) !important; }
  .cbb { border-bottom: 2.5px solid var(--accent) !important; }
  .cbl { border-left:   2.5px solid var(--accent) !important; }
  .cbr { border-right:  2.5px solid var(--accent) !important; }

  /* ── Right panel ── */
  .right-panel { display: flex; flex-direction: column; gap: 1.25rem; }

  /* Numpad */
  .numpad-title {
    font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 2px; color: var(--muted);
    text-align: center; margin-bottom: 0.25rem;
  }
  #numpad { display: grid; gap: 6px; }
  .num-btn {
    width: 52px; height: 52px;
    background: var(--surface);
    border: 1px solid #444;
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 1.2rem; font-weight: 700;
    border-radius: 4px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.1s;
  }
  .num-btn:hover { background: #2a2a44; border-color: var(--accent); color: var(--accent); }
  .erase-btn {
    background: transparent; border: 1px solid #444; color: var(--muted);
    font-family: 'Space Mono', monospace; font-size: 0.7rem;
    letter-spacing: 1px; padding: 0.4rem;
    width: 100%; border-radius: 4px; cursor: pointer;
    transition: all 0.1s;
  }
  .erase-btn:hover { border-color: var(--red); color: var(--red); }

  /* Info panel */
  .info-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.25rem;
    min-width: 180px;
  }
  .info-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem; letter-spacing: 2px;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: 0.75rem;
  }
  .stat-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.35rem 0; border-bottom: 1px solid #222;
    font-size: 0.85rem;
  }
  .stat-row:last-child { border-bottom: none; margin-top: 0.5rem; }
  .stat-l { color: var(--muted); }
  .stat-v { font-family: 'Space Mono', monospace; color: var(--accent); }
  .diff-pill {
    display: inline-block; padding: 0.2rem 0.75rem;
    border-radius: 20px; font-size: 0.7rem;
    letter-spacing: 1px; text-transform: uppercase;
    font-family: 'Space Mono', monospace;
  }
  .pill-easy   { background:#152515; color:#6fcf97; border:1px solid #2a4a2a; }
  .pill-medium { background:#1f1a08; color:#f5c542; border:1px solid #4a3a08; }
  .pill-hard   { background:#2a1515; color:#eb5757; border:1px solid #4a2020; }

  /* ── Empty state ── */
  #emptyState {
    text-align: center; padding: 3rem 2rem; color: #444;
  }
  .empty-icon { font-size: 3rem; margin-bottom: 1rem; }
  .empty-text { font-family: 'Space Mono', monospace; font-size: 0.9rem; color: #555; }

  /* ── Win overlay ── */
  #winOverlay {
    display: none; position: fixed; inset: 0;
    background: rgba(13,13,20,0.93);
    z-index: 200; align-items: center;
    justify-content: center; flex-direction: column; gap: 1.5rem;
  }
  #winOverlay.show { display: flex; }
  .win-star { font-size: 4rem; }
  .win-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem; font-weight: 700;
    color: var(--accent); letter-spacing: -1px;
  }
  .win-sub { color: var(--muted); font-size: 0.9rem; }

  /* ── How to play ── */
  details {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    max-width: 680px; width: 100%;
    margin-top: 2rem;
  }
  summary {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem; letter-spacing: 2px;
    text-transform: uppercase; color: var(--muted);
    cursor: pointer;
  }
  details p { font-size: 0.88rem; color: #aaa; line-height: 1.7; margin-top: 0.75rem; }
  details ul { margin-top: 0.5rem; padding-left: 1.5rem; }
  details li { font-size: 0.85rem; color: #aaa; line-height: 1.9; }
</style>
</head>
<body>

<header>
  <div class="logo">KEN<span>KEN</span></div>
  <div class="tagline">Math &amp; Logic Puzzle</div>
</header>

<div class="controls">
  <span class="ctrl-label">Grid</span>
  <select id="sizeSelect">
    <option value="3">3 × 3</option>
    <option value="4" selected>4 × 4</option>
    <option value="5">5 × 5</option>
    <option value="6">6 × 6</option>
  </select>
  <span class="ctrl-label">Difficulty</span>
  <select id="diffSelect">
    <option value="easy">Easy</option>
    <option value="medium" selected>Medium</option>
    <option value="hard">Hard</option>
  </select>
  <button class="btn-primary" id="genBtn">Generate →</button>
  <button class="btn-secondary" id="checkBtn" style="display:none">Check</button>
  <button class="btn-secondary" id="solveBtn" style="display:none">Solve</button>
  <div class="status-badge" id="status">Ready</div>
</div>

<div id="gameArea">
  <div id="emptyState">
    <div class="empty-icon">◈</div>
    <div class="empty-text">Select a size and hit Generate</div>
  </div>
</div>

<div id="winOverlay">
  <div class="win-star">★</div>
  <div class="win-title">Puzzle Solved!</div>
  <div class="win-sub" id="winSub"></div>
  <button class="btn-primary" id="winNewBtn">New Puzzle →</button>
</div>

<details>
  <summary>How to play</summary>
  <p>KenKen is a math logic puzzle. Fill the grid so that:</p>
  <ul>
    <li>Each row contains the numbers <strong>1 to N</strong> exactly once.</li>
    <li>Each column contains the numbers <strong>1 to N</strong> exactly once.</li>
    <li>Each <strong>cage</strong> (bold-bordered group) satisfies its clue (e.g. <code>6×</code> means the cells multiply to 6).</li>
    <li>A single-cell cage shows its value directly.</li>
  </ul>
  <p>Click a cell to select it, then press a number key or use the numpad. Use <kbd>⌫ Backspace</kbd> to erase. Arrow keys navigate the grid.</p>
</details>

<script>
// ───────────────────────────── state
let puzzle = null, userGrid = [], sel = null;
let secs = 0, moves = 0, timerId = null;
let N = 4;

// ───────────────────────────── helpers
const $ = id => document.getElementById(id);
const cell = (r,c) => $(`c-${r}-${c}`);
const val  = (r,c) => $(`v-${r}-${c}`);

function setStatus(msg, cls='') {
  const el = $('status');
  el.textContent = msg;
  el.className = 'status-badge' + (cls ? ' '+cls : '');
}
function fmtTime(s) {
  const m = Math.floor(s/60);
  return m > 0 ? `${m}m ${s%60}s` : `${s}s`;
}
function startTimer() {
  if(timerId) clearInterval(timerId);
  secs = 0; moves = 0;
  timerId = setInterval(() => { secs++; updateStats(); }, 1000);
}
function updateStats() {
  const t = $('statTime'), mv = $('statMoves');
  if(t)  t.textContent = fmtTime(secs);
  if(mv) mv.textContent = moves;
}

// ───────────────────────────── puzzle generation
function latinSquare(n) {
  const g = [];
  for(let r=0;r<n;r++){
    const row=[];
    for(let c=0;c<n;c++) row.push((r+c)%n+1);
    g.push(row);
  }
  // shuffle rows
  for(let i=n-1;i>0;i--){
    const j=Math.floor(Math.random()*(i+1));
    [g[i],g[j]]=[g[j],g[i]];
  }
  // shuffle cols
  for(let i=n-1;i>0;i--){
    const j=Math.floor(Math.random()*(i+1));
    for(let r=0;r<n;r++) [g[r][i],g[r][j]]=[g[r][j],g[r][i]];
  }
  return g;
}

function buildCages(sol, n, diff) {
  const assigned = Array.from({length:n},()=>Array(n).fill(-1));
  const cages = [];
  let id = 0;
  const maxSz = diff==='easy'?2:diff==='medium'?3:4;

  const all = [];
  for(let r=0;r<n;r++) for(let c=0;c<n;c++) all.push([r,c]);
  for(let i=all.length-1;i>0;i--){
    const j=Math.floor(Math.random()*(i+1));
    [all[i],all[j]]=[all[j],all[i]];
  }

  const neighbors=(r,c)=>[[r-1,c],[r+1,c],[r,c-1],[r,c+1]]
    .filter(([nr,nc])=>nr>=0&&nr<n&&nc>=0&&nc<n);

  for(const [sr,sc] of all){
    if(assigned[sr][sc]>=0) continue;
    const cells=[[sr,sc]];
    assigned[sr][sc]=id;
    const sz=diff==='easy'?1+Math.floor(Math.random()*2):1+Math.floor(Math.random()*maxSz);
    for(let k=1;k<sz;k++){
      const cands=[];
      for(const [r,c] of cells)
        for(const [nr,nc] of neighbors(r,c))
          if(assigned[nr][nc]<0) cands.push([nr,nc]);
      if(!cands.length) break;
      const pick=cands[Math.floor(Math.random()*cands.length)];
      cells.push(pick);
      assigned[pick[0]][pick[1]]=id;
    }

    const vals=cells.map(([r,c])=>sol[r][c]);
    let op='', target=0;
    if(cells.length===1){
      target=vals[0];
    } else {
      const allowedOps = diff==='easy'?['+','-']:diff==='medium'?['+','-','×']:['+','-','×','÷'];
      const possible=['+'];
      if(vals.length===2){
        possible.push('-');
        possible.push('×');
        const [a,b]=[Math.max(...vals),Math.min(...vals)];
        if(b!==0&&a%b===0) possible.push('÷');
      } else {
        possible.push('×');
      }
      const choices=allowedOps.filter(o=>possible.includes(o));
      op=choices[Math.floor(Math.random()*choices.length)]||'+';
      if(op==='+') target=vals.reduce((a,b)=>a+b,0);
      else if(op==='×') target=vals.reduce((a,b)=>a*b,1);
      else if(op==='-'){
        const s=[...vals].sort((a,b)=>b-a);
        target=s[0]-s.slice(1).reduce((a,b)=>a+b,0);
        if(target<1){ op='+'; target=vals.reduce((a,b)=>a+b,0); }
      } else if(op==='÷'){
        const s=[...vals].sort((a,b)=>b-a);
        let t=s[0]; let ok=true;
        for(let i=1;i<s.length;i++){
          if(t%s[i]===0) t=t/s[i]; else { ok=false; break; }
        }
        if(ok&&t>=1){ target=t; }
        else { op='×'; target=vals.reduce((a,b)=>a*b,1); }
      }
    }
    cages.push({id,cells,op,target});
    id++;
  }
  return cages;
}

function makePuzzle(n, diff) {
  const sol = latinSquare(n);
  const cages = buildCages(sol, n, diff);
  return {sol, cages, n};
}

// ───────────────────────────── render
function render(p) {
  puzzle = p; N = p.n;
  userGrid = Array.from({length:N},()=>Array(N).fill(0));
  sel = null;

  const ga = $('gameArea');
  ga.innerHTML = '';

  // cage lookup
  const cageOf = Array.from({length:N},()=>Array(N).fill(null));
  for(const cage of p.cages) for(const [r,c] of cage.cells) cageOf[r][c]=cage;

  // grid
  const gridWrap = document.createElement('div');
  gridWrap.id='gridWrap';
  const grid = document.createElement('div');
  grid.id='grid';
  grid.style.gridTemplateColumns=`repeat(${N},70px)`;
  grid.style.gridTemplateRows=`repeat(${N},70px)`;

  for(let r=0;r<N;r++) for(let c=0;c<N;c++){
    const div=document.createElement('div');
    div.className='cell'; div.id=`c-${r}-${c}`;
    div.dataset.r=r; div.dataset.c=c;

    const cage=cageOf[r][c];
    if(cage){
      const has=(dr,dc)=>cage.cells.some(([cr,cc])=>cr===r+dr&&cc===c+dc);
      if(!has(-1,0)) div.classList.add('cbt');
      if(!has(1,0))  div.classList.add('cbb');
      if(!has(0,-1)) div.classList.add('cbl');
      if(!has(0,1))  div.classList.add('cbr');

      const sorted=[...cage.cells].sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
      if(sorted[0][0]===r&&sorted[0][1]===c){
        const hint=document.createElement('div');
        hint.className='cage-hint';
        hint.textContent=cage.op?cage.target+cage.op:cage.target;
        div.appendChild(hint);
      }
    }

    const vEl=document.createElement('div');
    vEl.className='cell-val'; vEl.id=`v-${r}-${c}`;
    div.appendChild(vEl);

    div.addEventListener('click',()=>selectCell(r,c));
    grid.appendChild(div);
  }
  gridWrap.appendChild(grid);
  ga.appendChild(gridWrap);

  // right panel
  const rp=document.createElement('div');
  rp.className='right-panel';

  // numpad
  const npWrap=document.createElement('div');
  const npTitle=document.createElement('div');
  npTitle.className='numpad-title'; npTitle.textContent='Numbers';
  npWrap.appendChild(npTitle);
  const npGrid=document.createElement('div');
  npGrid.id='numpad';
  npGrid.style.gridTemplateColumns=`repeat(${Math.min(N,4)},52px)`;
  for(let i=1;i<=N;i++){
    const btn=document.createElement('button');
    btn.className='num-btn'; btn.textContent=i;
    btn.addEventListener('click',()=>inputNum(i));
    npGrid.appendChild(btn);
  }
  npWrap.appendChild(npGrid);
  const erBtn=document.createElement('button');
  erBtn.className='erase-btn'; erBtn.textContent='⌫  ERASE';
  erBtn.addEventListener('click',()=>inputNum(0));
  npWrap.appendChild(erBtn);
  rp.appendChild(npWrap);

  // info
  const diff=$('diffSelect').value;
  const ip=document.createElement('div');
  ip.className='info-panel';
  ip.innerHTML=`
    <div class="info-title">Session</div>
    <div class="stat-row"><span class="stat-l">Time</span><span class="stat-v" id="statTime">0s</span></div>
    <div class="stat-row"><span class="stat-l">Moves</span><span class="stat-v" id="statMoves">0</span></div>
    <div class="stat-row"><span class="stat-l">Grid</span><span class="stat-v">${N}×${N}</span></div>
    <div class="stat-row"><span class="stat-l">Cages</span><span class="stat-v">${p.cages.length}</span></div>
    <div class="stat-row">
      <span class="diff-pill pill-${diff}">${diff}</span>
    </div>
  `;
  rp.appendChild(ip);
  ga.appendChild(rp);

  $('checkBtn').style.display='';
  $('solveBtn').style.display='';
  startTimer();
  setStatus('Playing','ok');
}

// ───────────────────────────── interaction
function selectCell(r,c){
  if(sel){
    cell(sel[0],sel[1]).classList.remove('selected');
  }
  sel=[r,c];
  cell(r,c).classList.add('selected');
}

function inputNum(n){
  if(!sel||!puzzle) return;
  const [r,c]=sel;
  userGrid[r][c]=n;
  moves++;
  const vEl=val(r,c);
  vEl.textContent=n||''; vEl.className='cell-val';
  cell(r,c).classList.remove('correct','wrong');
  updateStats();
  autoCheck();
}

function autoCheck(){
  for(let r=0;r<N;r++) for(let c=0;c<N;c++) if(userGrid[r][c]===0) return;
  let ok=true;
  for(let r=0;r<N;r++) for(let c=0;c<N;c++) if(userGrid[r][c]!==puzzle.sol[r][c]) ok=false;
  if(ok) showWin();
}

function checkPuzzle(){
  if(!puzzle) return;
  let good=0,bad=0;
  for(let r=0;r<N;r++) for(let c=0;c<N;c++){
    const v=userGrid[r][c]; if(!v) continue;
    const cEl=cell(r,c), vEl=val(r,c);
    if(v===puzzle.sol[r][c]){
      cEl.classList.add('correct'); cEl.classList.remove('wrong');
      vEl.className='cell-val user-ok'; good++;
    } else {
      cEl.classList.add('wrong'); cEl.classList.remove('correct');
      vEl.className='cell-val user-err'; bad++;
    }
  }
  setStatus(`✓${good}  ✗${bad}`, bad>0?'err':'ok');
}

function solvePuzzle(){
  if(!puzzle) return;
  for(let r=0;r<N;r++) for(let c=0;c<N;c++){
    userGrid[r][c]=puzzle.sol[r][c];
    const vEl=val(r,c); const cEl=cell(r,c);
    vEl.textContent=puzzle.sol[r][c]; vEl.className='cell-val user-ok';
    cEl.classList.remove('wrong'); cEl.classList.add('correct');
  }
  if(timerId) clearInterval(timerId);
  setStatus('Solved!','ok');
}

function showWin(){
  if(timerId) clearInterval(timerId);
  $('winSub').textContent=`Solved in ${fmtTime(secs)} · ${moves} moves`;
  $('winOverlay').classList.add('show');
}

// ───────────────────────────── events
$('genBtn').addEventListener('click',()=>{
  const n=parseInt($('sizeSelect').value);
  const d=$('diffSelect').value;
  setStatus('Generating…','loading');
  setTimeout(()=>{
    const p=makePuzzle(n,d);
    render(p);
    $('winOverlay').classList.remove('show');
  },60);
});

$('checkBtn').addEventListener('click', checkPuzzle);
$('solveBtn').addEventListener('click', solvePuzzle);
$('winNewBtn').addEventListener('click',()=>{ $('winOverlay').classList.remove('show'); $('genBtn').click(); });

document.addEventListener('keydown', e=>{
  if(!puzzle) return;
  const k=e.key;
  if(k>='1'&&k<=String(N)){ inputNum(parseInt(k)); return; }
  if(k==='Backspace'||k==='Delete'||k==='0'){ inputNum(0); return; }
  if(!sel) return;
  const[r,c]=sel;
  const dirs={ArrowUp:[-1,0],ArrowDown:[1,0],ArrowLeft:[0,-1],ArrowRight:[0,1]};
  if(dirs[k]){
    e.preventDefault();
    const[dr,dc]=dirs[k];
    const nr=Math.max(0,Math.min(N-1,r+dr));
    const nc=Math.max(0,Math.min(N-1,c+dc));
    selectCell(nr,nc);
  }
});

// auto-start
$('genBtn').click();
</script>
</body>
</html>"""


def main():
    # Write to a temp file and open in browser
    tmp = tempfile.NamedTemporaryFile(
        mode='w', suffix='.html', delete=False,
        prefix='kenken_', encoding='utf-8'
    )
    tmp.write(HTML)
    tmp.close()

    path = 'file://' + tmp.name
    print("=" * 50)
    print("  KenKen Puzzle")
    print("=" * 50)
    print(f"\n  Opening puzzle in your browser...")
    print(f"  File: {tmp.name}")
    print("\n  If it doesn't open automatically, copy the")
    print(f"  path above into your browser.\n")
    print("  Controls:")
    print("    • Click a cell, then press 1–N or use numpad")
    print("    • Arrow keys to navigate")
    print("    • Backspace to erase")
    print("    • Check / Solve buttons on the page")
    print("\n  Close this terminal window to quit.")
    print("=" * 50)

    webbrowser.open(path)

    try:
        input("\n  Press Enter to exit and clean up...\n")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


if __name__ == '__main__':
    main()
