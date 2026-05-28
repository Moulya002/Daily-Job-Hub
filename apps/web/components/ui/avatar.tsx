import { cn } from "@/lib/utils";

type AvatarProps = {
  name: string;
  image?: string | null;
  className?: string;
};

export function Avatar({ name, image, className }: AvatarProps) {
  const initials = name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className={cn("inline-flex h-9 w-9 items-center justify-center rounded-full bg-slate-800 text-xs font-semibold", className)}>
      {image ? <img src={image} alt={name} className="h-full w-full rounded-full object-cover" /> : initials || "U"}
    </div>
  );
}
