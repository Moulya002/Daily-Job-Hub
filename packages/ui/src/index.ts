import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

export function PrimaryButton({
  children,
  className = "",
  ...props
}: PropsWithChildren<ButtonHTMLAttributes<HTMLButtonElement>>) {
  return (
    <button
      className={`rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500 ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
