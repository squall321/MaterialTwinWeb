// 다중파일 드롭존(§14.3.1·§14.5.2). react-dropzone + dragover 글로우 모션(CSS .dropzone).
import * as React from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, X } from "lucide-react";
import { cn } from "../lib/utils";

type Props = {
  /** 드롭/선택된 파일을 부모로 전달. */
  onFiles: (files: File[]) => void;
  /** 현재 선택된 파일(칩 표시). 부모가 상태 소유. */
  files?: File[];
  onRemove?: (index: number) => void;
  accept?: Record<string, string[]>;
  multiple?: boolean;
};

export function UploadDropzone({ onFiles, files = [], onRemove, accept, multiple = true }: Props) {
  const onDrop = React.useCallback((accepted: File[]) => onFiles(accepted), [onFiles]);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        data-state={isDragActive ? "dragover" : "idle"}
        className={cn(
          "dropzone flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg bg-inset px-6 py-12 text-center",
        )}
        role="button"
        tabIndex={0}
        aria-label="인장시험 파일 업로드"
      >
        <input {...getInputProps()} />
        <UploadCloud className="h-7 w-7 text-text-tertiary" aria-hidden />
        <p className="text-[0.875rem] text-text-secondary">
          파일을 여기로 끌어다 놓거나 클릭해 선택하세요.
        </p>
        <p className="text-[0.6875rem] text-text-tertiary">CSV · TXT (testXpert / 일반 CSV)</p>
      </div>

      {files.length > 0 && (
        <ul className="mt-3 space-y-1.5">
          {files.map((f, i) => (
            <li
              key={`${f.name}-${i}`}
              className="flex items-center gap-2 rounded-md border border-border-subtle bg-surface px-3 py-2"
            >
              <FileText className="h-4 w-4 shrink-0 text-text-tertiary" aria-hidden />
              <span className="min-w-0 flex-1 truncate text-[0.8125rem] text-text-primary">{f.name}</span>
              <span className="tnum shrink-0 text-[0.6875rem] text-text-tertiary">
                {(f.size / 1024).toFixed(1)} KB
              </span>
              {onRemove && (
                <button
                  type="button"
                  onClick={() => onRemove(i)}
                  className="shrink-0 rounded-sm p-0.5 text-text-tertiary transition-colors hover:text-danger"
                  aria-label={`${f.name} 제거`}
                >
                  <X className="h-3.5 w-3.5" aria-hidden />
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
