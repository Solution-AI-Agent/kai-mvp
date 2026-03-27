// frontend/src/App.jsx
import { useState } from "react";
import FileUpload from "./components/FileUpload";
import ResultView from "./components/ResultView";

const MODELS = [
  { id: "openai/gpt-4o-mini", name: "GPT-4o Mini" },
  { id: "openai/gpt-4o", name: "GPT-4o" },
  { id: "anthropic/claude-sonnet-4", name: "Claude Sonnet 4" },
  { id: "anthropic/claude-haiku-4", name: "Claude Haiku 4" },
  { id: "google/gemini-2.5-flash-preview", name: "Gemini 2.5 Flash" },
  { id: "meta-llama/llama-4-maverick", name: "Llama 4 Maverick" },
];

function App() {
  const [file, setFile] = useState(null);
  const [model, setModel] = useState(MODELS[0].id);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!file) return;

    setIsLoading(true);
    setError("");
    setResult(null);
    setStatus("STT 변환 중...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setStatus("회의록 생성 중...");
      const response = await fetch(`/api/generate?model=${encodeURIComponent(model)}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let message = "서버 오류가 발생했습니다.";
        try {
          const err = await response.json();
          message = err.detail || message;
        } catch {
          message = await response.text() || message;
        }
        throw new Error(message);
      }

      const data = await response.json();
      setResult(data);
      setStatus("");
    } catch (err) {
      setError(err.message);
      setStatus("");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result?.markdown) return;
    const blob = new Blob([result.markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "회의록.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-dark-900 text-gray-100">
      <header className="border-b border-dark-700 px-6 py-4">
        <h1 className="text-2xl font-bold text-emerald-400">KAI 회의록</h1>
      </header>

      <main className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <FileUpload onFileSelect={setFile} file={file} isLoading={isLoading} />
          </div>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            disabled={isLoading}
            className="px-4 py-3 bg-dark-800 border border-dark-700 rounded-lg text-gray-100 focus:border-emerald-500 focus:outline-none"
          >
            {MODELS.map((m) => (
              <option key={m.id} value={m.id}>{m.name}</option>
            ))}
          </select>
          <button
            onClick={handleGenerate}
            disabled={!file || isLoading}
            className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-dark-700 disabled:text-gray-500 rounded-lg font-semibold transition-colors"
          >
            {isLoading ? status : "회의록 생성"}
          </button>
        </div>

        {error && (
          <div className="bg-red-900/30 border border-red-700 text-red-300 rounded-lg p-4">
            {error}
          </div>
        )}

        {result && (
          <>
            <ResultView result={result} />
            <div className="flex justify-center">
              <button
                onClick={handleDownload}
                className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 rounded-lg font-semibold transition-colors"
              >
                마크다운 다운로드
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
