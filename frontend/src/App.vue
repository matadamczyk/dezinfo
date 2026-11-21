<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Navbar from './components/Navbar.vue';
import InputPanel from './components/InputPanel.vue';
import VerdictCard from './components/VerdictCard.vue';
import ToxicityCard from './components/ToxicityCard.vue';
import TextComparison from './components/TextComparison.vue';
import SubgraphGraph from './components/SubgraphGraph.vue';
import { analyzeText, checkBackendHealth } from './services/api';
import { POLISH_POLITICAL_USE_CASES } from './mock/mockData';
import type { AnalysisResponse } from './types/analysis';
import { Shield, Sparkles, ArrowDown } from 'lucide-vue-next';

const currentText = ref<string>(POLISH_POLITICAL_USE_CASES[0].text);
const analysisResult = ref<AnalysisResponse | null>(null);
const isLoading = ref<boolean>(false);
const errorMessage = ref<string | null>(null);
const useMock = ref<boolean>(false);
const backendOnline = ref<boolean | null>(null);

async function refreshBackendStatus() {
  const isUp = await checkBackendHealth();
  backendOnline.value = isUp;
  if (!isUp && !analysisResult.value) {
    useMock.value = true;
  }
}

onMounted(async () => {
  await refreshBackendStatus();
});

async function runAnalysis() {
  if (!currentText.value.trim() || isLoading.value) return;

  isLoading.value = true;
  errorMessage.value = null;

  try {
    const result = await analyzeText(currentText.value, useMock.value);
    analysisResult.value = result;
  } catch (err: unknown) {
    analysisResult.value = null;
    if (err instanceof Error) {
      errorMessage.value = err.message;
    } else {
      errorMessage.value = 'Wystąpił nieoczekiwany błąd podczas weryfikacji wpisu.';
    }
  } finally {
    isLoading.value = false;
  }
}

async function handleEnableMockAndSubmit() {
  useMock.value = true;
  errorMessage.value = null;
  await runAnalysis();
}

function handleReset() {
  currentText.value = '';
  analysisResult.value = null;
  errorMessage.value = null;
}

function handleClear() {
  currentText.value = '';
  errorMessage.value = null;
}
</script>

<template>
  <div class="min-h-screen bg-[#F6F7F4] text-[#181A17] flex flex-col font-sans selection:bg-[#EDF2E7] selection:text-[#3F5E2A]">
    <Navbar
      v-model:useMock="useMock"
      :backendOnline="backendOnline"
      @reset="handleReset"
    />

    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
      <div class="relative overflow-hidden rounded-2xl sm:rounded-3xl bg-white border border-[#E6E8E2] p-6 sm:p-8 shadow-xs">
        <div class="relative z-10 max-w-3xl space-y-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#EDF2E7] text-[#3F5E2A] border border-[#DCE5D5]">
            <Sparkles class="w-3.5 h-3.5 text-[#3F5E2A]" />
            Platforma Detekcji Dezinformacji i Analizy Stylu
          </div>
          <h1 class="text-2xl sm:text-4xl font-extrabold tracking-tight text-[#181A17] leading-tight">
            Weryfikacja wypowiedzi politycznych metodą <span class="text-[#3F5E2A]">Hybrid GraphRAG</span>
          </h1>
          <p class="text-sm sm:text-base text-[#646A61] leading-relaxed">
            Wielopoziomowa ocena wiarygodności: klasyfikacja sentymentu i toksyczności, weryfikacja faktów na podgrafie referencyjnym oraz automatyczna neutralizacja stylu wypowiedzi.
          </p>
        </div>
      </div>

      <InputPanel
        v-model="currentText"
        :isLoading="isLoading"
        :errorMessage="errorMessage"
        :useMock="useMock"
        @submit="runAnalysis"
        @enableMockAndSubmit="handleEnableMockAndSubmit"
        @clear="handleClear"
      />

      <div v-if="analysisResult" class="space-y-6 animate-in fade-in duration-500">
        <div class="flex items-center gap-2 pt-2">
          <span class="h-px flex-1 bg-[#E6E8E2]"></span>
          <span class="text-xs font-mono uppercase tracking-widest text-[#646A61] px-3 py-1 rounded-full bg-white border border-[#E6E8E2] flex items-center gap-1.5 shadow-xs">
            <ArrowDown class="w-3.5 h-3.5 text-[#3F5E2A]" />
            Wyniki analizy i weryfikacji
          </span>
          <span class="h-px flex-1 bg-[#E6E8E2]"></span>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <VerdictCard
            :verdict="analysisResult.fact_check.verdict"
            :explanation="analysisResult.fact_check.explanation"
          />

          <ToxicityCard
            :toxicityScore="analysisResult.style.toxicity_score"
            :sentiment="analysisResult.style.sentiment"
            :isToxic="analysisResult.style.is_toxic"
          />
        </div>

        <TextComparison
          :originalText="analysisResult.original_text || currentText"
          :censoredText="analysisResult.fact_check.censored_text"
          :neutralizedText="analysisResult.fact_check.neutralized_text"
        />

        <SubgraphGraph
          :edges="analysisResult.fact_check.subgraph_edges"
        />
      </div>
    </main>

    <footer class="mt-auto border-t border-[#E6E8E2] bg-white py-6 text-center text-xs text-[#646A61]">
      <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="flex items-center gap-2 text-[#646A61]">
          <Shield class="w-4 h-4 text-[#3F5E2A]" />
          <span class="font-semibold text-[#181A17]">Dezinfo Guard</span>
          <span>&mdash; WSEI NLP / Hybrid GraphRAG Disinformation Project</span>
        </div>
        <div class="flex items-center gap-4 text-[#646A61]">
          <span>Vue 3 + TypeScript + Tailwind CSS</span>
          <span>FastAPI Backend</span>
        </div>
      </div>
    </footer>
  </div>
</template>
