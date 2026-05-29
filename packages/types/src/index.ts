export type JobCategory = "FAANG+" | "Quant" | "Other";

export type JobLevel = "INTERN" | "NEW_GRAD" | "FULL_TIME" | "CONTRACT";

export type JobListItem = {
  id: string;
  title: string;
  companyName: string;
  location?: string | null;
  workMode?: "REMOTE" | "HYBRID" | "ONSITE" | null;
  summary: string;
  jobType?: JobLevel | null;
  category?: JobCategory;
  salaryMin?: number | null;
  salaryMax?: number | null;
  currency?: string | null;
  applyUrl?: string | null;
  postedAt?: string | null;
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
