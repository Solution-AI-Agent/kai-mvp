// frontend/src/components/MinutesPanel.jsx
export default function MinutesPanel({ summary, discussions, decisions, actionItems }) {
  return (
    <div className="bg-dark-800 rounded-lg p-5 h-full overflow-y-auto space-y-5">
      <section>
        <h2 className="text-lg font-semibold text-emerald-400 mb-2">요약</h2>
        <p className="text-gray-300">{summary}</p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-emerald-400 mb-2">주요 논의사항</h2>
        <ul className="list-disc list-inside text-gray-300 space-y-1">
          {discussions.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-emerald-400 mb-2">결정사항</h2>
        <ul className="list-disc list-inside text-gray-300 space-y-1">
          {decisions.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-emerald-400 mb-2">액션아이템</h2>
        <ul className="list-disc list-inside text-gray-300 space-y-1">
          {actionItems.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
