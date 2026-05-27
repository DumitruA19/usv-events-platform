import React from "react";

export function PageHeader(props: { title: string; subtitle?: string; actions?: React.ReactNode }) {
  const { title, subtitle, actions } = props;
  return (
    <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-ink dark:text-white">{title}</h1>
        {subtitle ? <p className="mt-2 text-sm muted">{subtitle}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}
