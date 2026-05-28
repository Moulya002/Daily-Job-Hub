"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function SearchForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initial = searchParams.get("q") ?? "remote AI internships with sponsorship";
  const [query, setQuery] = useState(initial);

  return (
    <form
      className="flex flex-col gap-3 md:flex-row"
      onSubmit={(event) => {
        event.preventDefault();
        router.push(`/search?q=${encodeURIComponent(query)}`);
      }}
    >
      <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="remote AI internships with sponsorship" />
      <Button type="submit">Search</Button>
    </form>
  );
}
