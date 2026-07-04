const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API error ${response.status}`);
  }
  return response.json();
}

export async function getCommunity() {
  return request("/api/v1/cer");
}

export async function getAdminDashboard(params = {}) {
  const search = new URLSearchParams();
  if (params.start) search.set("start", params.start);
  if (params.end) search.set("end", params.end);
  const query = search.toString();
  return request(`/api/v1/dashboard/admin${query ? `?${query}` : ""}`);
}

export async function getMemberDashboard(memberId) {
  return request(`/api/v1/dashboard/member/${memberId}`);
}

export async function getMonthlyReport(year, month) {
  return request(`/api/v1/reports/monthly?year=${year}&month=${month}`);
}
