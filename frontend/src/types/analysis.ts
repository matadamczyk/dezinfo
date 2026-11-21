export type VerdictType = 'Prawda' | 'Fałsz' | 'Manipulacja' | 'Brak danych' | string;

export interface StyleAnalysis {
  sentiment: string;
  toxicity_score: number;
  is_toxic: boolean;
}

export interface FactCheckAnalysis {
  verdict: VerdictType;
  explanation: string;
  censored_text: string;
  neutralized_text: string;
  subgraph_edges: [string, string, string][];
}

export interface AnalysisResponse {
  style: StyleAnalysis;
  fact_check: FactCheckAnalysis;
  original_text?: string;
}

export interface RawBackendResponse {
  text?: string;
  sentiment?: string;
  toxicity_score?: number;
  is_toxic?: boolean;
  verdict?: string;
  explanation?: string;
  censored_text?: string;
  neutralized_text?: string;
  subgraph_edges?: [string, string, string][];
  style?: StyleAnalysis;
  fact_check?: FactCheckAnalysis;
}

export interface UseCase {
  id: string;
  title: string;
  badge: string;
  description: string;
  text: string;
  expectedVerdict: VerdictType;
  mockResponse: AnalysisResponse;
}
