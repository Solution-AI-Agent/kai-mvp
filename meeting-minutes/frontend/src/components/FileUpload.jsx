// frontend/src/components/FileUpload.jsx
import { useCallback } from "react";

export default function FileUpload({ onFileSelect, file, isLoading }) {
  const handleChange = useCallback(
    (e) => {
      const selected = e.target.files?.[0];
      if (selected) onFileSelect(selected);
    },
    [onFileSelect]
  );

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      const dropped = e.dataTransfer.files?.[0];
      if (dropped) onFileSelect(dropped);
    },
    [onFileSelect]
  );

  return (
    <div className="flex items-center gap-4">
      <label
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="flex-1 flex items-center justify-center border-2 border-dashed border-dark-700 rounded-lg p-6 cursor-pointer hover:border-emerald-500 transition-colors"
      >
        <input
          type="file"
          accept=".mp3,.wav"
          onChange={handleChange}
          className="hidden"
          disabled={isLoading}
        />
        <span className="text-gray-400">
          {file ? file.name : "오디오 파일을 드래그하거나 클릭하여 선택 (mp3, wav)"}
        </span>
      </label>
    </div>
  );
}
