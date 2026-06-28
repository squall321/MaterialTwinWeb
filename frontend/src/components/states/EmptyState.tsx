// 빈 상태(§14.6.1) — "초대"이지 "사과"가 아니다. 중앙 760px, 1차 액션, 한국어 마침표 종결.
import * as React from "react";
import { cn } from "../../lib/utils";

type Props = {
  /** 얇은 라인 아이콘(lucide). */
  icon?: React.ReactNode;
  title: string;
  description?: string;
  /** primary 액션. */
  action?: React.ReactNode;
  /** 2차 링크/액션. */
  secondary?: React.ReactNode;
  className?: string;
};

export function EmptyState({ icon, title, description, action, secondary, className }: Props) {
  return (
    <div
      className={cn(
        "mx-auto flex max-w-[760px] flex-col items-center px-6 py-16 text-center",
        className,
      )}
    >
      {icon && <div className="mb-5 text-text-tertiary">{icon}</div>}
      <h3 className="text-[1.25rem] font-semibold text-text-primary">{title}</h3>
      {description && (
        <p className="mt-2 max-w-[44ch] text-[0.875rem] leading-relaxed text-text-secondary">
          {description}
        </p>
      )}
      {action && <div className="mt-6">{action}</div>}
      {secondary && <div className="mt-3 text-[0.8125rem] text-text-tertiary">{secondary}</div>}
    </div>
  );
}
