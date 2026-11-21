import type { AnalysisResponse, RawBackendResponse, VerdictType } from '../types/analysis';
import { generateCustomMockResponse } from '../mock/mockData';

const API_BASE_URL = 'http://localhost:8000';

function normalizeVerdict(rawVerdict: string | undefined): VerdictType {
  if (!rawVerdict) return 'Brak danych';
  const upper = rawVerdict.trim().toUpperCase();
  if (upper === 'PRAWDA') return 'Prawda';
  if (upper === 'FAŁSZ' || upper === 'FALSZ') return 'Fałsz';
  if (upper === 'MANIPULACJA') return 'Manipulacja';
  if (upper === 'BRAK DANYCH' || upper === 'NIEZWERYFIKOWANE' || upper === 'BRAK_DANYCH') return 'Brak danych';
  return rawVerdict;
}

export function normalizeAnalysisResponse(raw: RawBackendResponse, originalText?: string): AnalysisResponse {
  if (raw.style && raw.fact_check) {
    return {
      style: {
        sentiment: raw.style.sentiment || 'neutral',
        toxicity_score: typeof raw.style.toxicity_score === 'number' ? raw.style.toxicity_score : 0,
        is_toxic: Boolean(raw.style.is_toxic),
      },
      fact_check: {
        verdict: normalizeVerdict(raw.fact_check.verdict),
        explanation: raw.fact_check.explanation || '',
        censored_text: raw.fact_check.censored_text || originalText || '',
        neutralized_text: raw.fact_check.neutralized_text || originalText || '',
        subgraph_edges: Array.isArray(raw.fact_check.subgraph_edges) ? raw.fact_check.subgraph_edges : [],
      },
      original_text: originalText || raw.text || '',
    };
  }

  return {
    style: {
      sentiment: raw.sentiment || 'neutral',
      toxicity_score: typeof raw.toxicity_score === 'number' ? raw.toxicity_score : 0,
      is_toxic: Boolean(raw.is_toxic),
    },
    fact_check: {
      verdict: normalizeVerdict(raw.verdict),
      explanation: raw.explanation || '',
      censored_text: raw.censored_text || originalText || raw.text || '',
      neutralized_text: raw.neutralized_text || originalText || raw.text || '',
      subgraph_edges: Array.isArray(raw.subgraph_edges) ? raw.subgraph_edges : [],
    },
    original_text: originalText || raw.text || '',
  };
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response.ok;
  } catch {
    return false;
  }
}

export async function analyzeText(text: string, useMock: boolean): Promise<AnalysisResponse> {
  const trimmed = text.trim();
  if (!trimmed) {
    throw new Error('Treść tekstu do analizy nie może być pusta.');
  }

  if (useMock) {
    await new Promise((resolve) => setTimeout(resolve, 450));
    const mock = generateCustomMockResponse(trimmed);
    mock.original_text = trimmed;
    return mock;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: trimmed }),
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => '');
      throw new Error(`Serwer zwrócił błąd HTTP ${response.status}: ${errorText || response.statusText}`);
    }

    const data: RawBackendResponse = await response.json();
    return normalizeAnalysisResponse(data, trimmed);
  } catch (error: unknown) {
    if (error instanceof Error && error.message.includes('HTTP')) {
      throw error;
    }
    throw new Error('Nie można połączyć się z backendem FastAPI (http://localhost:8000). Uruchom backend lub przełącz aplikację w tryb Mock (offline).');
  }
}
