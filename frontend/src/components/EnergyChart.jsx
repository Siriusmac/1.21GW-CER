import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function EnergyChart({ data }) {
  const chartData = data.map((point) => ({
    time: new Date(point.timestamp).toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" }),
    produzione: point.production_kwh,
    consumo: point.consumption_kwh,
    condivisa: point.shared_energy_kwh,
  }));

  return (
    <div className="chart-panel">
      <ResponsiveContainer width="100%" height={310}>
        <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#d9e2e7" />
          <XAxis dataKey="time" tick={{ fill: "#47616d", fontSize: 12 }} />
          <YAxis tick={{ fill: "#47616d", fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey="produzione" stroke="#0f9f6e" strokeWidth={3} dot={false} />
          <Line type="monotone" dataKey="consumo" stroke="#2457a6" strokeWidth={3} dot={false} />
          <Line type="monotone" dataKey="condivisa" stroke="#d08700" strokeWidth={3} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
