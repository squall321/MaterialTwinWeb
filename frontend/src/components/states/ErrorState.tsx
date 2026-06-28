// 전역 에러 상태(§14.6.3) — 760px 중앙, 다시 시도 + 접을 수 있는 기술 상세(<details> mono).
import { TriangleAlert } from "lucide-react";
import { cn } from "../../lib/utils";

type Props = {
  title?: string;
  message?: string;
  /** 기술 상세(스택/에러 detail). <details> 안에 mono 로. */
  detail?: string;
  onRetry?: () => void;
  className?: string;
};

export function ErrorState({
  title = "예상치 못한 오류",
  message = "데이터를 불러오지 못했습니다. 잠시 후 다시 시도하세요.",
  detail,
  onRetry,
  className,
}: Props) {
  return (
    <div
      className={cn("mx-auto flex max-w-[760px] flex-col items-center px-6 py-16 text-center", className)}
      role="alert"
    >
      <TriangleAlert className="mb-4 h-8 w-8 text-danger" aria-hidden />
      <h3 className="text-[1.25rem] font-semibold text-text-primary">{title}</h3>
      <p className="mt-2 max-w-[44ch] text-[0.875rem] text-text-secondary">{message}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-6 rounded-md bg-primary px-4 py-2 text-[0.875rem] font-medium text-primary-fg transition-colors hover:bg-primary-hover"
        >
          다시 시도
        </button>
      )}
      {detail && (
        <details className="mt-4 w-full max-w-[44ch] text-left">
          <summary className="cursor-pointer text-[0.75rem] text-text-tertiary">기술 상세</summary>
          <pre className="mt-2 overflow-x-auto rounded-md bg-inset p-3 font-mono text-[0.6875rem] text-text-secondary">
            {detail}
          </pre>
        </details>
      )}
    </div>
  );
}
