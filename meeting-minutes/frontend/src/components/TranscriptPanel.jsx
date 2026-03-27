// frontend/src/components/TranscriptPanel.jsx
export default function TranscriptPanel({ transcript }) {
  return (
    <div className="bg-dark-800 rounded-lg p-5 h-full overflow-y-auto">
      <h2 className="text-lg font-semibold text-emerald-400 mb-3">
        STT 원문
      </h2>
      <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">
        {transcript}
      </p>
    </div>
  );
}
