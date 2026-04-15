(function(){const o=document.createElement("link").relList;if(o&&o.supports&&o.supports("modulepreload"))return;for(const n of document.querySelectorAll('link[rel="modulepreload"]'))t(n);new MutationObserver(n=>{for(const d of n)if(d.type==="childList")for(const m of d.addedNodes)m.tagName==="LINK"&&m.rel==="modulepreload"&&t(m)}).observe(document,{childList:!0,subtree:!0});function r(n){const d={};return n.integrity&&(d.integrity=n.integrity),n.referrerPolicy&&(d.referrerPolicy=n.referrerPolicy),n.crossOrigin==="use-credentials"?d.credentials="include":n.crossOrigin==="anonymous"?d.credentials="omit":d.credentials="same-origin",d}function t(n){if(n.ep)return;n.ep=!0;const d=r(n);fetch(n.href,d)}})();let p={user:null,token:null};const f=[];function C(){f.forEach(a=>a(p))}function T(){return{...p}}function H(a){return f.push(a),()=>{f.splice(f.indexOf(a),1)}}function A(a,o){p.token=a,p.user=o,a&&(localStorage.setItem("token",a),localStorage.setItem("user",JSON.stringify(o))),C()}function D(){const a=localStorage.getItem("token"),o=localStorage.getItem("user");a&&o&&(p.token=a,p.user=JSON.parse(o))}let x=window.location.hash.slice(1)||"/";const E=[];function B(a){window.location.hash=a}function R(){return x}function P(a){return E.push(a),()=>{E.splice(E.indexOf(a),1)}}window.addEventListener("hashchange",()=>{x=window.location.hash.slice(1)||"/",E.forEach(a=>a(x))});const w=window.location.origin+"/api";async function b(a,o={}){const r=localStorage.getItem("token"),t={Authorization:r?`Bearer ${r}`:"",...o.headers},n=await fetch(`${w}${a}`,{method:"GET",headers:t,...o});if(!n.ok)throw{status:n.status,message:await n.text()};return n}async function M(a,o={},r={}){const t=localStorage.getItem("token"),n={"Content-Type":"application/json",Authorization:t?`Bearer ${t}`:"",...r.headers},d=await fetch(`${w}${a}`,{method:"POST",headers:n,body:JSON.stringify(o),...r});if(!d.ok)throw{status:d.status,message:await d.text()};return d}async function O(a,o={}){const r=localStorage.getItem("token"),t={Authorization:r?`Bearer ${r}`:"",...o.headers},n=await fetch(`${w}${a}`,{headers:t,...o});if(!n.ok)throw{status:n.status,message:await n.text()};return n}async function j(){const a=document.getElementById("root");a.innerHTML=`
    <main class="login-shell">
      <section class="card login-card">
        <h1>S&OP Forecasting System</h1>
        <p>Sign in to your dashboard</p>
        <form id="login-form">
          <label>
            Username
            <input id="username" type="text" required />
          </label>
          <label>
            Password
            <input id="password" type="password" required />
          </label>
          <button type="submit">Sign In</button>
          <div id="login-error"></div>
        </form>
        <div style="margin-top: 16px; font-size: 0.9rem;">
          <p><strong>Demo Accounts:</strong></p>
          <p>Account Manager: john.wicks / password123</p>
          <p>Segment Head: rachel / password123</p>
          <p>Factory Head: abhinav / password123</p>
        </div>
      </section>
    </main>
  `,document.getElementById("login-form").addEventListener("submit",async r=>{r.preventDefault();const t=document.getElementById("username").value,n=document.getElementById("password").value,d=document.getElementById("login-error");try{d.textContent="";const g=await(await M("/auth/login",{username:t,password:n})).json();A(g.token,g.user),B("/")}catch{d.textContent="Invalid credentials"}})}async function N(){const a=document.getElementById("root");a.innerHTML=`
    <main class="app-shell">
      <header class="topbar">
        <h1>Intelligent S&OP Forecasting & Data Governance</h1>
        <div class="row">
          <span id="user-name"></span>
          <button id="logout-btn">Logout</button>
        </div>
      </header>

      <div class="stack">
        <section class="card">
          <h2>John Wicks - Account Manager</h2>
          <p>Forecast input and generation workspace.</p>
          <div class="grid-2">
            <label>
              Bearing designation
              <input id="designation" type="text" />
            </label>
            <label>
              Forecasted volume/month
              <input id="volume" type="number" />
            </label>
            <label>
              Factory
              <input id="factory" type="text" />
            </label>
            <label>
              Month
              <input id="month" type="text" placeholder="YYYY-MM" />
            </label>
            <label>
              Growth % (+/-)
              <input id="growth" type="number" />
            </label>
          </div>
          <div class="row">
            <button id="gen-history">Generate by Sales History</button>
            <button id="gen-growth">Generate by User % Input</button>
            <button id="gen-market">Generate by Market Intelligence</button>
          </div>
          <div class="row">
            <button id="export-csv">Export CSV</button>
            <button id="export-xlsx">Export XLSX</button>
          </div>
          <div id="status-message"></div>
        </section>

        <section class="card">
          <h3>Customer Month-on-Month Forecast</h3>
          <table id="summary-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Month</th>
                <th>Forecast Volume</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </section>

        <section class="card">
          <h3>Market Intelligence (Your Customers)</h3>
          <ul id="news-list"></ul>
        </section>
      </div>
    </main>
  `;let o=[],r=[],t={designation:"6205-2RS",volume:1e3,factory:"Pune",month:"2026-05",growth:10};async function n(){try{const[i,l]=await Promise.all([b("/dashboards/account-manager"),b("/market-intelligence")]),e=await i.json(),s=await l.json();o=e.customerMonthly,r=s.items.map(u=>u.title),document.getElementById("user-name").textContent="john.wicks",d()}catch{document.getElementById("status-message").textContent="Failed to load dashboard",document.getElementById("status-message").className="error"}}function d(){const i=document.querySelector("#summary-table tbody");i.innerHTML=o.map(e=>`
      <tr>
        <td>${e.customer}</td>
        <td>${e.month}</td>
        <td>${e.forecastVolume}</td>
      </tr>
    `).join("");const l=document.getElementById("news-list");l.innerHTML=r.map(e=>`<li>${e}</li>`).join("")}document.getElementById("designation").value=t.designation,document.getElementById("volume").value=t.volume,document.getElementById("factory").value=t.factory,document.getElementById("month").value=t.month,document.getElementById("growth").value=t.growth,document.getElementById("designation").addEventListener("change",i=>{t.designation=i.target.value}),document.getElementById("volume").addEventListener("change",i=>{t.volume=Number(i.target.value)}),document.getElementById("factory").addEventListener("change",i=>{t.factory=i.target.value}),document.getElementById("month").addEventListener("change",i=>{t.month=i.target.value}),document.getElementById("growth").addEventListener("change",i=>{t.growth=Number(i.target.value)});async function m(i){const l=document.getElementById("status-message");l.textContent="Generating forecast...",l.className="status";try{const e=await M("/forecasts/generate",{mode:i,growthPercent:t.growth,inputs:[{customerId:1,productDesignation:t.designation,factory:t.factory,month:t.month,volume:t.volume}]});l.textContent="Forecast generated and saved",await n()}catch{l.textContent="Failed to generate forecast",l.className="error"}}document.getElementById("gen-history").addEventListener("click",()=>m("history")),document.getElementById("gen-growth").addEventListener("click",()=>m("user_growth")),document.getElementById("gen-market").addEventListener("click",()=>m("market_intelligence"));async function g(i){try{const e=await(await b(`/exports/forecasts.${i}`)).blob(),s=document.createElement("a");s.href=URL.createObjectURL(e),s.download=`forecast-export.${i}`,s.click(),URL.revokeObjectURL(s.href)}catch{document.getElementById("status-message").textContent="Export failed",document.getElementById("status-message").className="error"}}document.getElementById("export-csv").addEventListener("click",()=>g("csv")),document.getElementById("export-xlsx").addEventListener("click",()=>g("xlsx")),document.getElementById("logout-btn").addEventListener("click",()=>{localStorage.removeItem("token"),localStorage.removeItem("user"),window.location.hash="#/login"}),n()}async function V(){const a=document.getElementById("root");a.innerHTML=`
    <main class="app-shell">
      <header class="topbar">
        <h1>Intelligent S&OP Forecasting & Data Governance</h1>
        <div class="row">
          <span id="user-name"></span>
          <button id="logout-btn">Logout</button>
        </div>
      </header>

      <div class="segment-shell">
        <section class="card segment-hero">
          <h2>Rachel - Segment Head Intelligence Dashboard</h2>
          <p>Monitor team performance, monthly trend shifts, and live market signals across product lines.</p>

          <div class="segment-kpis">
            <div class="kpi-card">
              <span>Filtered Forecast Volume</span>
              <strong id="kpi-total">0</strong>
            </div>
            <div class="kpi-card">
              <span>Rows in Scope</span>
              <strong id="kpi-rows">0</strong>
            </div>
            <div class="kpi-card">
              <span>Active Team Members</span>
              <strong id="kpi-team">0</strong>
            </div>
          </div>

          <div class="segment-filters">
            <input id="filter-customer" placeholder="Filter Customer" />
            <input id="filter-designation" placeholder="Filter Designation" />
            <input id="filter-factory" placeholder="Filter Factory" />
            <input id="filter-month" placeholder="Filter Month (YYYY-MM)" />
          </div>

          <div class="team-filter-wrap">
            <strong>Filter Team Members</strong>
            <div class="team-filter-list" id="team-filter-list"></div>
          </div>

          <div class="row">
            <button id="export-csv" type="button">Export Filtered CSV</button>
            <button id="export-xlsx" type="button">Export Filtered XLSX</button>
          </div>
          <div id="status-message"></div>
        </section>

        <section class="card chart-card">
          <h3>Trend per Product Line per Month</h3>
          <div class="chart-list" id="chart-list"></div>
        </section>

        <section class="card">
          <h3>Volume per Designation per Month</h3>
          <table id="designation-table">
            <thead>
              <tr>
                <th>Month</th>
                <th>Designation</th>
                <th>Total Volume Received</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </section>

        <section class="card">
          <h3>Filtered Team Data</h3>
          <table id="team-table">
            <thead>
              <tr>
                <th>Account Manager</th>
                <th>Customer</th>
                <th>Designation</th>
                <th>Product Line</th>
                <th>Factory</th>
                <th>Month</th>
                <th>Forecast Volume</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </section>

        <section class="card">
          <h3>Live Market Intelligence</h3>
          <div class="intelligence-grid" id="intel-grid"></div>
        </section>
      </div>
    </main>
  `;let o={rows:[],teamMembers:[],designationMonthlyVolume:[],productLineMonthlyTrend:[],liveMarketIntelligence:[]},r=[],t={customer:"",designation:"",factory:"",month:""};try{o=await(await b("/dashboards/segment-head")).json(),document.getElementById("user-name").textContent="rachel"}catch{document.getElementById("status-message").textContent="Failed to load dashboard",document.getElementById("status-message").className="error";return}function n(){const e=document.getElementById("team-filter-list");if(e.innerHTML=o.teamMembers.map(s=>`
      <button type="button" class="team-chip ${r.includes(s)?"active":""}"
              data-member="${s}">
        ${s}
      </button>
    `).join(""),r.length>0){const s=document.createElement("button");s.type="button",s.className="team-chip clear",s.textContent="Clear",s.addEventListener("click",()=>{r=[],i()}),e.appendChild(s)}e.querySelectorAll("[data-member]").forEach(s=>{s.addEventListener("click",()=>{const u=s.dataset.member;r.includes(u)?r=r.filter(y=>y!==u):r=[...r,u],i()})})}function d(){const e=new Set(r);return o.rows.filter(s=>(!t.customer||s.customer.includes(t.customer))&&(!t.designation||s.designation.includes(t.designation))&&(!t.factory||s.factory.includes(t.factory))&&(!t.month||s.month.includes(t.month))&&(!e.size||e.has(s.accountManager)))}function m(){return o.productLineMonthlyTrend.filter(e=>!t.month||e.month.includes(t.month))}function g(){return o.designationMonthlyVolume.filter(e=>!t.month||e.month.includes(t.month))}function i(){const e=d(),s=e.reduce((c,F)=>c+F.forecastVolume,0),u=r.length||o.teamMembers.length;document.getElementById("kpi-total").textContent=s,document.getElementById("kpi-rows").textContent=e.length,document.getElementById("kpi-team").textContent=u,n();const y=m(),I=Math.max(1,...y.map(c=>c.totalVolume)),h=y.map(c=>`
      <div class="chart-row">
        <div class="chart-label">${c.month} | ${c.productLine}</div>
        <div class="chart-bar">
          <span style="width: ${Math.max(8,c.totalVolume/I*100)}%"></span>
        </div>
        <strong>${c.totalVolume}</strong>
      </div>
    `).join("");document.getElementById("chart-list").innerHTML=h||"<p>No trend data available</p>";const k=g().map(c=>`
      <tr>
        <td>${c.month}</td>
        <td>${c.designation}</td>
        <td>${c.totalVolume}</td>
      </tr>
    `).join("");document.querySelector("#designation-table tbody").innerHTML=k;const S=e.map(c=>`
      <tr>
        <td>${c.accountManager}</td>
        <td>${c.customer}</td>
        <td>${c.designation}</td>
        <td>${c.productLine}</td>
        <td>${c.factory}</td>
        <td>${c.month}</td>
        <td>${c.forecastVolume}</td>
      </tr>
    `).join("");document.querySelector("#team-table tbody").innerHTML=S;const $=o.liveMarketIntelligence.map(c=>`
      <article class="intel-card">
        <h4>${c.title}</h4>
        <p><strong>Impacted Customers:</strong> ${c.impactedCustomers}</p>
        <p><strong>Impact:</strong> ${c.impactPercent}%</p>
        <p class="intel-time">Observed: ${new Date(c.observedAt).toLocaleString()}</p>
      </article>
    `).join("");document.getElementById("intel-grid").innerHTML=$}document.getElementById("filter-customer").addEventListener("change",e=>{t.customer=e.target.value,i()}),document.getElementById("filter-designation").addEventListener("change",e=>{t.designation=e.target.value,i()}),document.getElementById("filter-factory").addEventListener("change",e=>{t.factory=e.target.value,i()}),document.getElementById("filter-month").addEventListener("change",e=>{t.month=e.target.value,i()}),document.getElementById("logout-btn").addEventListener("click",()=>{localStorage.removeItem("token"),localStorage.removeItem("user"),window.location.hash="#/login"});async function l(e){document.getElementById("export-csv").disabled=!0,document.getElementById("export-xlsx").disabled=!0,document.getElementById("export-csv").textContent="Exporting...",document.getElementById("export-xlsx").textContent="Exporting...";try{const s=d(),u=new URLSearchParams({customer:t.customer,designation:t.designation,factory:t.factory,month:t.month,teamMembers:r.join(",")}),I=await(await O(`/exports/segment-head.${e}?${u}`,{responseType:"blob"})).blob(),h=document.createElement("a");h.href=URL.createObjectURL(I),h.download=`segment-head-export.${e}`,h.click(),URL.revokeObjectURL(h.href);const v=document.getElementById("status-message");v.textContent=`Successfully exported ${e.toUpperCase()} (${s.length} rows)`,v.className="success",setTimeout(()=>{v.textContent="",v.className=""},4e3)}catch{document.getElementById("status-message").textContent="Unable to export view",document.getElementById("status-message").className="error"}finally{document.getElementById("export-csv").disabled=!1,document.getElementById("export-xlsx").disabled=!1,document.getElementById("export-csv").textContent="Export Filtered CSV",document.getElementById("export-xlsx").textContent="Export Filtered XLSX"}}document.getElementById("export-csv").addEventListener("click",()=>l("csv")),document.getElementById("export-xlsx").addEventListener("click",()=>l("xlsx")),i()}async function U(){const a=document.getElementById("root");a.innerHTML=`
    <main class="app-shell">
      <header class="topbar">
        <h1>Intelligent S&OP Forecasting & Data Governance</h1>
        <div class="row">
          <span id="user-name"></span>
          <button id="logout-btn">Logout</button>
        </div>
      </header>

      <div class="stack">
        <section class="card">
          <h2>Abhinav - Factory Head Dashboard</h2>
          <p>Factory-level view for planning and demand visibility.</p>
        </section>
        <section class="card">
          <table id="data-table">
            <thead>
              <tr>
                <th>Factory</th>
                <th>Month</th>
                <th>Designation</th>
                <th>Forecast Volume</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </section>
      </div>
    </main>
  `;try{const r=await(await b("/dashboards/factory-head")).json();document.getElementById("user-name").textContent="abhinav";const t=document.querySelector("#data-table tbody");t.innerHTML=r.rows.map(n=>`
      <tr>
        <td>${n.factory}</td>
        <td>${n.month}</td>
        <td>${n.designation}</td>
        <td>${n.forecastVolume}</td>
      </tr>
    `).join("")}catch{document.querySelector("#data-table tbody").innerHTML="<tr><td colspan='4'>Failed to load data</td></tr>"}document.getElementById("logout-btn").addEventListener("click",()=>{localStorage.removeItem("token"),localStorage.removeItem("user"),window.location.hash="#/login"})}D();async function L(){const a=R(),o=T();if(!o.user&&a!=="/login"){B("/login");return}a==="/login"?await j():o.user&&(o.user.role==="ACCOUNT_MANAGER"?await N():o.user.role==="SEGMENT_HEAD"?await V():o.user.role==="FACTORY_HEAD"&&await U())}H(()=>{L()});P(()=>{L()});L();
