/* The Green Tank TIME on static GitHub Pages: read-only calls to the public Site API. */
(() => {
  "use strict";
  const API = "https://the-green-tank.alexiscoderpenguy.chatgpt.site";
  const PREFIX = "/Thegreentank-deployment-2";
  const PLACES = [{"group":"United Kingdom","country":"United Kingdom","city":"London","zone":"Europe/London","lat":51.507,"lon":-0.128},{"group":"Canada","country":"Canada · Pacific","city":"Vancouver","zone":"America/Vancouver","lat":49.282,"lon":-123.12},{"group":"Canada","country":"Canada · Mountain","city":"Edmonton","zone":"America/Edmonton","lat":53.546,"lon":-113.49},{"group":"Canada","country":"Canada · Central","city":"Winnipeg","zone":"America/Winnipeg","lat":49.895,"lon":-97.139},{"group":"Canada","country":"Canada · Eastern","city":"Toronto","zone":"America/Toronto","lat":43.653,"lon":-79.383},{"group":"Canada","country":"Canada · Atlantic","city":"Halifax","zone":"America/Halifax","lat":44.648,"lon":-63.575},{"group":"Canada","country":"Canada · Newfoundland","city":"St. John's","zone":"America/St_Johns","lat":47.561,"lon":-52.712},{"group":"Brazil","country":"Brazil · Fernando de Noronha","city":"Fernando de Noronha","zone":"America/Noronha","lat":-3.854,"lon":-32.423},{"group":"Brazil","country":"Brazil · Brasília","city":"Brasília","zone":"America/Sao_Paulo","lat":-15.794,"lon":-47.882},{"group":"Brazil","country":"Brazil · Amazon","city":"Manaus","zone":"America/Manaus","lat":-3.12,"lon":-60.021},{"group":"Brazil","country":"Brazil · Acre","city":"Rio Branco","zone":"America/Rio_Branco","lat":-9.975,"lon":-67.81},{"group":"Mexico","country":"Mexico · Pacific border","city":"Tijuana","zone":"America/Tijuana","lat":32.514,"lon":-117.038},{"group":"Mexico","country":"Mexico · Sonora","city":"Hermosillo","zone":"America/Hermosillo","lat":29.073,"lon":-110.955},{"group":"Mexico","country":"Mexico · Central","city":"Mexico City","zone":"America/Mexico_City","lat":19.432,"lon":-99.133},{"group":"Mexico","country":"Mexico · Quintana Roo","city":"Cancún","zone":"America/Cancun","lat":21.161,"lon":-86.851},{"group":"Other requested","country":"Venezuela","city":"Caracas","zone":"America/Caracas","lat":10.48,"lon":-66.904},{"group":"Other requested","country":"Egypt","city":"Cairo","zone":"Africa/Cairo","lat":30.044,"lon":31.236},{"group":"Other requested","country":"Iran","city":"Tehran","zone":"Asia/Tehran","lat":35.689,"lon":51.389},{"group":"European Union","country":"Austria","city":"Vienna","zone":"Europe/Vienna","lat":48.208,"lon":16.374},{"group":"European Union","country":"Belgium","city":"Brussels","zone":"Europe/Brussels","lat":50.85,"lon":4.352},{"group":"European Union","country":"Bulgaria","city":"Sofia","zone":"Europe/Sofia","lat":42.698,"lon":23.322},{"group":"European Union","country":"Croatia","city":"Zagreb","zone":"Europe/Zagreb","lat":45.815,"lon":15.982},{"group":"European Union","country":"Cyprus","city":"Nicosia","zone":"Asia/Nicosia","lat":35.186,"lon":33.382},{"group":"European Union","country":"Czechia","city":"Prague","zone":"Europe/Prague","lat":50.076,"lon":14.438},{"group":"European Union","country":"Denmark","city":"Copenhagen","zone":"Europe/Copenhagen","lat":55.676,"lon":12.568},{"group":"European Union","country":"Estonia","city":"Tallinn","zone":"Europe/Tallinn","lat":59.437,"lon":24.753},{"group":"European Union","country":"Finland","city":"Helsinki","zone":"Europe/Helsinki","lat":60.17,"lon":24.938},{"group":"European Union","country":"France","city":"Paris","zone":"Europe/Paris","lat":48.857,"lon":2.352},{"group":"European Union","country":"Germany","city":"Berlin","zone":"Europe/Berlin","lat":52.52,"lon":13.405},{"group":"European Union","country":"Greece","city":"Athens","zone":"Europe/Athens","lat":37.984,"lon":23.728},{"group":"European Union","country":"Hungary","city":"Budapest","zone":"Europe/Budapest","lat":47.497,"lon":19.04},{"group":"European Union","country":"Ireland","city":"Dublin","zone":"Europe/Dublin","lat":53.35,"lon":-6.26},{"group":"European Union","country":"Italy","city":"Rome","zone":"Europe/Rome","lat":41.903,"lon":12.496},{"group":"European Union","country":"Latvia","city":"Riga","zone":"Europe/Riga","lat":56.95,"lon":24.105},{"group":"European Union","country":"Lithuania","city":"Vilnius","zone":"Europe/Vilnius","lat":54.687,"lon":25.28},{"group":"European Union","country":"Luxembourg","city":"Luxembourg","zone":"Europe/Luxembourg","lat":49.611,"lon":6.131},{"group":"European Union","country":"Malta","city":"Valletta","zone":"Europe/Malta","lat":35.9,"lon":14.514},{"group":"European Union","country":"Netherlands","city":"Amsterdam","zone":"Europe/Amsterdam","lat":52.368,"lon":4.904},{"group":"European Union","country":"Poland","city":"Warsaw","zone":"Europe/Warsaw","lat":52.23,"lon":21.012},{"group":"European Union","country":"Portugal","city":"Lisbon","zone":"Europe/Lisbon","lat":38.722,"lon":-9.139},{"group":"European Union","country":"Romania","city":"Bucharest","zone":"Europe/Bucharest","lat":44.427,"lon":26.102},{"group":"European Union","country":"Slovakia","city":"Bratislava","zone":"Europe/Bratislava","lat":48.148,"lon":17.107},{"group":"European Union","country":"Slovenia","city":"Ljubljana","zone":"Europe/Ljubljana","lat":46.057,"lon":14.506},{"group":"European Union","country":"Spain","city":"Madrid","zone":"Europe/Madrid","lat":40.417,"lon":-3.703},{"group":"European Union","country":"Sweden","city":"Stockholm","zone":"Europe/Stockholm","lat":59.329,"lon":18.068},{"group":"Additional zones","country":"Spain · Canary Islands","city":"Las Palmas","zone":"Atlantic/Canary","lat":28.124,"lon":-15.436},{"group":"Additional zones","country":"Portugal · Azores","city":"Ponta Delgada","zone":"Atlantic/Azores","lat":37.742,"lon":-25.676},{"group":"Additional zones","country":"Portugal · Madeira","city":"Funchal","zone":"Atlantic/Madeira","lat":32.65,"lon":-16.909},{"group":"Additional zones","country":"France · Réunion","city":"Saint-Denis","zone":"Indian/Reunion","lat":-20.879,"lon":55.448}];
  const home = document.querySelector(".home-utc-clock");
  const page = document.querySelector(".time-page");
  const embed = document.querySelector(".time-embed");
  if (!home && !page && !embed) return;
  let sample = null;
  let failed = false;
  let extraZones = [];
  let lastResult = null;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const iso = ms => new Date(ms).toISOString();
  const display = (ms, suffix) => ms === null ? "--:--:--" : `${iso(ms).slice(11, 19)} ${suffix}`;

  async function oneSample() {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    const wall0 = Date.now(), perf0 = performance.now();
    try {
      const response = await fetch(`${API}/v1/now`, { cache: "no-store", signal: controller.signal });
      const snapshot = await response.json();
      const perf3 = performance.now(), wall3 = Date.now();
      if (!response.ok || !Number.isFinite(snapshot.server_send_unix_ms) || !Number.isFinite(snapshot.server_receive_unix_ms)) throw Error("Time source unavailable");
      const roundTrip = perf3 - perf0;
      const serverMid = (snapshot.server_receive_unix_ms + snapshot.server_send_unix_ms) / 2;
      return { snapshot, anchorEpoch: serverMid + roundTrip / 2, anchorPerf: perf3,
        sampledAt: perf3, deviceOffset: serverMid - (wall0 + wall3) / 2,
        networkBound: Math.max(0, roundTrip - Math.max(0, snapshot.server_send_unix_ms - snapshot.server_receive_unix_ms)) / 2 };
    } finally { clearTimeout(timeout); }
  }
  async function refresh() {
    const responses = await Promise.allSettled([oneSample(), oneSample(), oneSample()]);
    const good = responses.filter(r => r.status === "fulfilled").map(r => r.value).sort((a, b) => a.networkBound - b.networkBound);
    sample = good[0] || null;
    failed = !sample;
    render();
  }
  function current() {
    const fresh = sample && performance.now() - sample.sampledAt < 90000;
    const snapshot = fresh ? sample.snapshot : null;
    const utc = fresh ? sample.anchorEpoch + performance.now() - sample.anchorPerf : null;
    const ready = snapshot?.data_state?.leap === "current_notice";
    const delta = ready ? snapshot.tai_minus_utc_seconds : null;
    const tai = utc !== null && delta !== null ? utc + delta * 1000 : null;
    const status = !fresh ? (failed ? "UNAVAILABLE" : "WAITING FOR SERVER") :
      snapshot.data_state.leap === "update_required" ? "DATA UPDATE REQUIRED" : "UNVERIFIED SERVER ESTIMATE";
    return { utc, tai, delta, status, sample: fresh ? sample : null };
  }
  function set(selector, value, root = document) { const node = $(selector, root); if (node) node.textContent = value; }
  function render() {
    const clock = current();
    if (home) {
      set("strong", display(clock.utc, "Z"), home);
      set("small", clock.status, home);
    }
    if (embed) {
      const times = $$(".time-embed-clocks strong", embed);
      if (times[0]) times[0].textContent = display(clock.utc, "Z");
      if (times[1]) times[1].textContent = display(clock.tai, "TAI");
      const foot = $$("footer span", embed);
      if (foot[0]) foot[0].textContent = clock.status;
      if (foot[1]) foot[1].textContent = `TAI−UTC ${clock.delta === null ? "unavailable" : `+${clock.delta} s`}`;
    }
    if (page) {
      const times = $$(".time-clock strong", page);
      if (times[0]) times[0].textContent = display(clock.utc, "Z");
      if (times[1]) times[1].textContent = display(clock.tai, "TAI");
      const health = $$(".time-health > *", page);
      const values = [clock.status, `TAI − UTC: ${clock.delta === null ? "unavailable" : `+${clock.delta} s`}`,
        `Source: ${clock.sample ? "hosting server clock" : "not available"}`,
        `Network timing bound: ${clock.sample ? `±${Math.ceil(clock.sample.networkBound)} ms` : "unknown"}`,
        "Absolute UTC uncertainty: unknown"];
      health.forEach((node, i) => { if (i < values.length) node.textContent = values[i]; });
      set(".time-device-value", clock.sample ? `${clock.sample.deviceOffset >= 0 ? "+" : ""}${Math.round(clock.sample.deviceOffset)} ms` : "No comparison yet", page);
      renderWorld(clock.utc);
    }
  }
  function localParts(ms, zone) {
    const date = new Date(ms);
    const parts = Object.fromEntries(new Intl.DateTimeFormat("en-GB", { timeZone: zone, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23" }).formatToParts(date).map(p => [p.type, p.value]));
    const local = `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}:${parts.second}`;
    const offset = Math.round((Date.parse(`${local}Z`) - Math.floor(ms / 1000) * 1000) / 1000);
    const magnitude = Math.abs(offset);
    const utcOffset = `UTC${offset >= 0 ? "+" : "−"}${String(Math.floor(magnitude / 3600)).padStart(2, "0")}:${String(Math.floor(magnitude % 3600 / 60)).padStart(2, "0")}`;
    const name = new Intl.DateTimeFormat("en-GB", { timeZone: zone, timeZoneName: "long" }).formatToParts(date).find(p => p.type === "timeZoneName")?.value || "";
    const daylight = /summer|daylight/i.test(name) ? "daylight saving" : /standard|mean time|greenwich mean/i.test(name) ? "standard" : "not labelled by runtime";
    return { local, utcOffset, daylight };
  }
  function twilight(ms, lat, lon) {
    const d = new Date(ms), year = d.getUTCFullYear();
    const n = Math.floor((Date.UTC(year, d.getUTCMonth(), d.getUTCDate()) - Date.UTC(year, 0, 1)) / 86400000) + 1;
    const days = new Date(Date.UTC(year, 1, 29)).getUTCMonth() === 1 ? 366 : 365;
    const hours = d.getUTCHours() + d.getUTCMinutes() / 60 + d.getUTCSeconds() / 3600;
    const g = 2 * Math.PI / days * (n - 1 + (hours - 12) / 24);
    const eq = 229.18 * (0.000075 + 0.001868 * Math.cos(g) - 0.032077 * Math.sin(g) - 0.014615 * Math.cos(2*g) - 0.040849 * Math.sin(2*g));
    const decl = 0.006918 - 0.399912*Math.cos(g) + 0.070257*Math.sin(g) - 0.006758*Math.cos(2*g) + 0.000907*Math.sin(2*g) - 0.002697*Math.cos(3*g) + 0.00148*Math.sin(3*g);
    const minute = d.getUTCHours()*60 + d.getUTCMinutes() + d.getUTCSeconds()/60;
    const hourAngle = ((((minute + eq + 4*lon) % 1440 + 1440) % 1440) / 4 - 180) * Math.PI/180;
    const latitude = lat*Math.PI/180;
    const altitude = 90 - Math.acos(Math.max(-1, Math.min(1, Math.sin(latitude)*Math.sin(decl) + Math.cos(latitude)*Math.cos(decl)*Math.cos(hourAngle)))) * 180/Math.PI;
    return altitude >= -0.833 ? "daylight" : altitude >= -6 ? "civil twilight" : altitude >= -12 ? "nautical twilight" : altitude >= -18 ? "astronomical twilight" : "night";
  }
  function renderWorld(utc) {
    const list = $(".time-world-list", page);
    if (!list) return;
    const group = $(".time-world-controls select", page)?.value || "United Kingdom";
    const query = $(".time-world-controls input[placeholder='Search all locations']", page)?.value.toLowerCase().trim() || "";
    const selected = PLACES.filter(p => query ? `${p.country} ${p.city} ${p.zone}`.toLowerCase().includes(query) : p.group === group);
    for (const zone of extraZones) if (!selected.some(p => p.zone === zone)) selected.push({ country: "Custom zone", city: zone.split("/").at(-1).replaceAll("_", " "), zone });
    list.replaceChildren();
    for (const p of selected) {
      const article = document.createElement("article"), heading = document.createElement("div");
      const country = document.createElement("strong"), city = document.createElement("span"), time = document.createElement("b"), detail = document.createElement("small");
      country.textContent = p.country; city.textContent = `${p.city} · ${p.zone}`;
      heading.append(country, city); article.append(heading, time, detail);
      try {
        const civil = utc === null ? null : localParts(utc, p.zone);
        time.textContent = civil ? civil.local.slice(11) : "--:--:--";
        detail.textContent = civil ? `${civil.local.slice(0, 10)} · ${civil.utcOffset} · ${civil.daylight} · ${Number.isFinite(p.lat) ? twilight(utc, p.lat, p.lon) : "location not supplied"}` : "Server reference unavailable";
      } catch { time.textContent = "--:--:--"; detail.textContent = "Time zone rule unavailable"; }
      list.append(article);
    }
  }
  function resultNode(tag, value, parent, className) {
    const node = document.createElement(tag);
    node.textContent = value;
    if (className) node.className = className;
    parent.append(node);
    return node;
  }
  function renderResult(result) {
    const section = $(".time-reconstruct", page);
    if (!section) return;
    $(".time-result", section)?.remove();
    const box = document.createElement("div"); box.className = "time-result"; box.setAttribute("role", "status"); box.setAttribute("aria-live", "polite");
    if (result.error) {
      resultNode("h3", "Needs another input", box);
      resultNode("p", result.error, box);
      for (const candidate of result.candidates || []) resultNode("p", `${candidate.utc} · ${candidate.civil.utc_offset}`, box);
    } else if (result.calculated && result.assessment) {
      resultNode("span", result.assessment.status, box, "time-result-state");
      resultNode("h3", "Conditions at the claimed instant", box);
      const c = result.calculated, dl = document.createElement("dl"); box.append(dl);
      const fields = [["UTC", c.utc], ["TAI-aligned", c.tai || "Offset not confirmed for this date"],
        ["Local civil time", `${c.civil.local} · ${c.civil.utc_offset}`],
        ["Solar altitude / azimuth", `${c.solar.altitude_degrees}° / ${c.solar.azimuth_degrees}°`],
        ["Sky phase", c.solar.twilight],
        ["Sunrise · noon · sunset (UTC)", `${c.solar.sunrise_utc || "none"} · ${c.solar.solar_noon_utc || "none"} · ${c.solar.sunset_utc || "none"}`],
        ["Capture to publication", c.capture_to_publication_seconds === null ? "not supplied" : `${c.capture_to_publication_seconds} seconds`]];
      for (const [name, value] of fields) { const row = document.createElement("div"); resultNode("dt", name, row); resultNode("dd", value, row); dl.append(row); }
      for (const finding of result.assessment.findings || []) resultNode("p", finding, box);
      resultNode("p", result.assessment.caution, box, "time-caution");
      resultNode("p", `Receipt SHA-256: ${result.receipt_sha256}`, box, "time-digest");
      const actions = document.createElement("div"); actions.className = "time-actions"; box.append(actions);
      const feedback = resultNode("span", "", actions);
      for (const [label, value] of [["Copy verification receipt", () => JSON.stringify(result, null, 2)], ["Copy shareable URL", () => location.href]]) {
        const button = resultNode("button", label, actions); button.type = "button";
        button.addEventListener("click", async () => { try { await navigator.clipboard.writeText(value()); feedback.textContent = "Copied"; } catch { feedback.textContent = "Select and copy the visible text instead."; } });
      }
    } else resultNode("p", "Result unavailable.", box);
    section.append(box);
  }
  const utcField = value => `${value.length === 16 ? `${value}:00` : value}Z`;
  const fromUtcField = value => (value || "").replace(/Z$/, "").slice(0, 19);
  function formParams(form) {
    const dateFields = $$("input[type='datetime-local']", form);
    const numbers = $$("input[type='number']", form);
    const selects = $$("select", form);
    const zone = $("input[list='time-zones']", form);
    const radios = $$("input[type='radio']", form);
    const mode = radios[1]?.checked ? "utc" : "local";
    const q = new URLSearchParams({ zone: zone.value, lat: numbers[0].value, lon: numbers[1].value,
      place: selects[0].value, observed_light: selects[1].value });
    q.set(mode, mode === "utc" ? utcField(dateFields[0].value) : dateFields[0].value);
    if (dateFields[1].value) q.set("published_utc", utcField(dateFields[1].value));
    if (dateFields[2].value) q.set("reposted_utc", utcField(dateFields[2].value));
    const notes = $("textarea", form).value.trim();
    if (notes) q.set("notes", notes.slice(0, 500));
    return q;
  }
  async function reconstruct(q) {
    try {
      const response = await fetch(`${API}/v1/reconstruct?${q}`, { cache: "no-store" });
      lastResult = await response.json();
      renderResult(lastResult);
    } catch { renderResult({ error: "Reconstruction service unavailable." }); }
  }
  function initializePage() {
    const form = $(".time-form", page);
    const controls = $(".time-world-controls", page);
    $(".time-device button", page)?.addEventListener("click", () => void refresh());
    $("select", controls)?.addEventListener("change", () => renderWorld(current().utc));
    $("input[placeholder='Search all locations']", controls)?.addEventListener("input", () => renderWorld(current().utc));
    const custom = $("input[list='time-zones']", controls);
    custom?.addEventListener("input", () => {});
    $("button", controls)?.addEventListener("click", () => {
      try { new Intl.DateTimeFormat("en-GB", { timeZone: custom.value });
        if (!extraZones.includes(custom.value)) extraZones.push(custom.value);
        custom.value = ""; renderWorld(current().utc);
      } catch { custom.value = "Invalid IANA zone"; }
    });
    const dataList = $("#time-zones", page);
    if (dataList && typeof Intl.supportedValuesOf === "function") for (const zone of Intl.supportedValuesOf("timeZone")) {
      const option = document.createElement("option"); option.value = zone; dataList.append(option);
    }
    const formPlace = $("select", form);
    formPlace?.addEventListener("change", () => {
      const place = PLACES.find(p => p.city === formPlace.value);
      if (!place) return;
      $("input[list='time-zones']", form).value = place.zone;
      const numbers = $$("input[type='number']", form);
      numbers[0].value = place.lat; numbers[1].value = place.lon;
    });
    const radios = $$("input[type='radio']", form);
    for (const radio of radios) radio.addEventListener("change", () => {
      radios.forEach(other => { if (other !== radio) other.checked = false; });
      const label = $("input[type='datetime-local']", form)?.parentElement;
      if (label?.firstChild?.nodeType === Node.TEXT_NODE) label.firstChild.textContent = radio === radios[1] ? "Claimed UTC date and time" : "Claimed local date and time";
    });
    form?.addEventListener("submit", event => {
      event.preventDefault();
      const q = formParams(form), share = new URLSearchParams(q); share.set("reconstruct", "1");
      history.replaceState({}, "", `${PREFIX}/time/?${share}`);
      void reconstruct(q);
    });
    const shared = new URLSearchParams(location.search);
    if (shared.get("reconstruct") === "1") {
      const q = new URLSearchParams(shared); q.delete("reconstruct");
      const dates = $$("input[type='datetime-local']", form), numbers = $$("input[type='number']", form), selects = $$("select", form);
      const utcMode = q.has("utc"); radios[utcMode ? 1 : 0].click();
      dates[0].value = fromUtcField(q.get("utc") || q.get("local"));
      dates[1].value = fromUtcField(q.get("published_utc")); dates[2].value = fromUtcField(q.get("reposted_utc"));
      $("input[list='time-zones']", form).value = q.get("zone") || "Europe/London";
      numbers[0].value = q.get("lat") || "51.507"; numbers[1].value = q.get("lon") || "-0.128";
      selects[0].value = q.get("place") || ""; selects[1].value = q.get("observed_light") || "unspecified";
      $("textarea", form).value = q.get("notes") || "";
      void reconstruct(q);
    }
    const embedCode = `<iframe src="${location.origin}${PREFIX}/time/embed/" title="Green Tank UTC and TAI reference" loading="lazy" style="width:100%;max-width:620px;height:230px;border:0"></iframe>`;
    const adopt = $(".time-adopt", page);
    if (adopt) {
      const textarea = $("textarea", adopt); if (textarea) textarea.value = embedCode;
      $("button", adopt)?.addEventListener("click", async () => {
        try { await navigator.clipboard.writeText(embedCode); $("button", adopt).textContent = "Embed copied"; }
        catch { $("button", adopt).textContent = "Select and copy the code above"; }
      });
    }
  }
  if (page) initializePage();
  render();
  void refresh();
  setInterval(render, 1000);
  setInterval(() => void refresh(), 30000);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") void refresh(); });
})();
