"use client";

import { useParams } from "next/navigation";
import { Header } from "@/components/layout/Header";
import { BriefingRoom } from "@/components/briefing/BriefingRoom";

export default function BriefingPage() {
  const params = useParams();
  const slug = params.slug as string;

  return (
    <div className="min-h-screen">
      <Header />
      <main className="mx-auto max-w-4xl px-4 py-6">
        <BriefingRoom dossierSlug={slug} />
      </main>
    </div>
  );
}
