export function MemberTable({ members }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Membro</th>
            <th>Consumo</th>
            <th>Quota condivisa</th>
            <th>Beneficio stimato</th>
          </tr>
        </thead>
        <tbody>
          {members.map((member) => (
            <tr key={member.member_id}>
              <td>{member.member_name}</td>
              <td>{member.consumption_kwh.toFixed(2)} kWh</td>
              <td>{member.shared_energy_kwh.toFixed(2)} kWh</td>
              <td>{member.estimated_benefit_eur.toFixed(2)} EUR</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
