import React from "react";
import { cn } from "./cn";

export function Card(props: React.HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return <div className={cn("surface", className)} {...rest} />;
}

export function CardHeader(props: React.HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return <div className={cn("px-6 pt-6", className)} {...rest} />;
}

export function CardBody(props: React.HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return <div className={cn("px-6 pb-6", className)} {...rest} />;
}

