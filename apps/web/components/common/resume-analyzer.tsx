"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type AnalysisPayload = {
  ats_score: number;
  match_percentage: number;
  missing_skills: string[];
  suggestions: string[];
};

export function ResumeAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] = useState<AnalysisPayload | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please select a PDF resume.");
      return;
    }
    if (!jobDescription.trim()) {
      setError("Please enter a job description.");
      return;
    }

    setError(null);
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const uploadRes = await fetch(`${API_BASE_URL}/ai/resume/upload`, {
        method: "POST",
        body: formData
      });
      if (!uploadRes.ok) throw new Error("Resume upload failed.");
      const uploadData = (await uploadRes.json()) as { text: string };

      const analyzeRes = await fetch(`${API_BASE_URL}/ai/resume/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "demo-user",
          resume_id: "demo-resume",
          job_id: null,
          resume_text: uploadData.text,
          job_description: jobDescription
        })
      });
      if (!analyzeRes.ok) throw new Error("Resume analysis failed.");
      setAnalysis((await analyzeRes.json()) as AnalysisPayload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload and Analyze Resume</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input type="file" accept="application/pdf" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
        <textarea
          className="min-h-36 w-full rounded-md border border-slate-700 bg-slate-950 p-3 text-sm text-slate-100"
          placeholder="Paste job description here..."
          value={jobDescription}
          onChange={(event) => setJobDescription(event.target.value)}
        />
        <Button onClick={handleAnalyze} disabled={isLoading}>
          {isLoading ? "Analyzing..." : "Analyze Resume"}
        </Button>
        {error ? <p className="text-sm text-red-400">{error}</p> : null}
        {analysis ? (
          <div className="rounded-md border border-slate-800 p-3 text-sm">
            <p>ATS Score: {analysis.ats_score}</p>
            <p>Match Percentage: {analysis.match_percentage}%</p>
            <p className="mt-2 font-medium">Missing Skills</p>
            <ul className="list-disc pl-5 text-slate-300">
              {analysis.missing_skills.map((skill) => (
                <li key={skill}>{skill}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
