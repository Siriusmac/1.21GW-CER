import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { CalendarDays, CircleUserRound, Gauge, Upload } from "lucide-react";

import { EnergyChart } from "./components/EnergyChart.jsx";
import { Kpi } from "./components/Kpi.jsx";
import { MemberTable } from "./components/MemberTable.jsx";
import { getAdminDashboard, getCommunity, getMemberDashboard } from "./lib/api.js";
import "./styles/app.css";

function App() {
  const [community, setCommunity] = useState(null);
  const [summary, setSummary] = useState(null);
  const [memberSummary, setMemberSummary] = useState(null);
  const [selectedMember, setSelectedMember] = useState("m-001");
  const [period, setPeriod] = useState("day");
  const [customRange, setCustomRange] = useState({ start: "", end: "" });
  const [error, setError] = useState("");

  const queryRange = useMemo(() => {
    if (period !== "custom") return {};
    return {
      start: customRange.start ? new Date(customRange.start).toISOString() : undefined,
      end: customRange.end ? new Date(customRange.end).toISOString() : undefined,
    };
  }, [period, customRange]);

  useEffect(() => {
    Promise.all([getCommunity(), getAdminDashboard(queryRange)])
      .then(([communityData, summaryData]) => {
        setCommunity(communityData);
        setSummary(summaryData);
        setError("");
      })
      .catch((err) => setError(err.message));
  }, [queryRange]);

  useEffect(() => {
    getMemberDashboard(selectedMember)
      .then((data) => setMemberSummary(data))
      .catch((err) => setError(err.message));
  }, [selectedMember]);

  if (!community || !summary) {
    return <main className="loading">Caricamento dashboard CER...</main>;
  }

  const member = memberSummary?.members?.[0];

  return (
    <main>
      <header className="topbar">
        <div>
          <p className="eyebrow">Comunità Energetica Rinnovabile</p>
          <h1>{community.name}</h1>
          <p className="subtle">{community.primary_substation}</p>
        </div>
        <span className="status">{summary.label}</span>
      </header>

      {error ? <div className="alert">{error}</div> : null}

      <section className="toolbar">
        <div className="tabs" aria-label="Filtri periodo">
          {["day", "month", "year", "custom"].map((item) => (
            <button key={item} className={period === item ? "active" : ""} onClick={() => setPeriod(item)}>
              <CalendarDays size={16} />
              {item === "day" ? "Giorno" : item === "month" ? "Mese" : item === "year" ? "Anno" : "Intervallo"}
            </button>
          ))}
        </div>
        {period === "custom" ? (
          <div className="range">
            <input type="datetime-local" value={customRange.start} onChange={(event) => setCustomRange({ ...customRange, start: event.target.value })} />
            <input type="datetime-local" value={customRange.end} onChange={(event) => setCustomRange({ ...customRange, end: event.target.value })} />
          </div>
        ) : null}
      </section>

      <section className="kpi-grid">
        <Kpi label="Produzione totale" value={summary.production_kwh.toFixed(2)} unit="kWh" />
        <Kpi label="Consumo totale" value={summary.consumption_kwh.toFixed(2)} unit="kWh" />
        <Kpi label="Energia condivisa stimata" value={summary.shared_energy_kwh.toFixed(2)} unit="kWh" />
        <Kpi label="Incentivo stimato" value={summary.estimated_value_eur.toFixed(2)} unit="EUR" />
      </section>

      <section className="main-grid">
        <div>
          <div className="section-title">
            <Gauge size={19} />
            <h2>Andamento energetico</h2>
          </div>
          <EnergyChart data={summary.series} />
        </div>

        <aside className="member-panel">
          <div className="section-title">
            <CircleUserRound size={19} />
            <h2>Vista membro</h2>
          </div>
          <select value={selectedMember} onChange={(event) => setSelectedMember(event.target.value)}>
            {community.members.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
          <div className="member-metrics">
            <Kpi label="Consumo periodo" value={(member?.consumption_kwh ?? 0).toFixed(2)} unit="kWh" />
            <Kpi label="Quota condivisa" value={(member?.shared_energy_kwh ?? 0).toFixed(2)} unit="kWh" />
            <Kpi label="Beneficio stimato" value={(member?.estimated_benefit_eur ?? 0).toFixed(2)} unit="EUR" />
          </div>
        </aside>
      </section>

      <section>
        <div className="section-title">
          <Upload size={19} />
          <h2>Ripartizione benefici</h2>
        </div>
        <MemberTable members={summary.members} />
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
