export type JobListItem = {
  id: string;
  title: string;
  companyName: string;
  location?: string | null;
  workMode?: "REMOTE" | "HYBRID" | "ONSITE" | null;
  summary: string;
};

export type SemanticSearchResult = JobListItem & {
  score: number;
};

export type ResumeAnalysisResult = {
  atsScore: number;
  matchPercentage: number;
  missingSkills: string[];
  suggestions: string[];
};
