// frontend/src/components/ResultView.jsx
import TranscriptPanel from "./TranscriptPanel";
import MinutesPanel from "./MinutesPanel";

export default function ResultView({ result }) {
  return (
    <div className="grid grid-cols-2 gap-4 h-[60vh]">
      <TranscriptPanel transcript={result.transcript} />
      <MinutesPanel
        summary={result.summary}
        discussions={result.discussions}
        decisions={result.decisions}
        actionItems={result.actionItems}
      />
    </div>
  );
}
