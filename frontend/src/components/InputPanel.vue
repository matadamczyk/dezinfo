<script setup lang="ts">
import { computed } from 'vue';
import { Send, Sparkles, AlertCircle, CheckCircle2, HelpCircle, Flame, BarChart3, RefreshCw, X } from 'lucide-vue-next';
import { POLISH_POLITICAL_USE_CASES } from '../mock/mockData';
import type { UseCase } from '../types/analysis';

const props = defineProps<{
  modelValue: string;
  isLoading: boolean;
  errorMessage: string | null;
  useMock: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'submit'): void;
  (e: 'enableMockAndSubmit'): void;
  (e: 'clear'): void;
}>();

const characterCount = computed(() => props.modelValue.length);

function selectUseCase(useCase: UseCase) {
  emit('update:modelValue', useCase.text);
}

function getUseCaseIcon(id: string) {
  if (id === 'toxic-fake-news') return Flame;
  if (id === 'statistic-manipulation') return BarChart3;
  if (id === 'neutral-truth') return CheckCircle2;
  return HelpCircle;
}

function getUseCaseColorClass(id: string) {
  if (id === 'toxic-fake-news') return 'border-rose-900/60 bg-rose-950/30 hover:border-rose-700 text-rose-300';
  if (id === 'statistic-manipulation') return 'border-amber-900/60 bg-amber-950/30 hover:border-amber-700 text-amber-300';
  if (id === 'neutral-truth') return 'border-emerald-900/60 bg-emerald-950/30 hover:border-emerald-700 text-emerald-300';
  return 'border-slate-800 bg-slate-900/50 hover:border-slate-700 text-slate-300';
}
</script>

<template>
  <div class="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 sm:p-6 shadow-xl backdrop-blur">
    <div class="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
      <div>
        <h2 class="text-base sm:text-lg font-semibold text-white flex items-center gap-2">
          <span>Weryfikacja wypowiedzi / posta</span>
          <span class="text-xs font-normal text-slate-400"> (X/Twitter, portale, cytaty)</span>
        </h2>
        <p class="text-xs text-slate-400">Wprowadź tekst do analizy stylu, sentymentu, toksyczności oraz weryfikacji w grafie wiedzy.</p>
      </div>

      <div class="flex items-center gap-2">
        <span class="text-xs text-slate-400 font-mono">{{ characterCount }} znaków</span>
        <button
          v-if="modelValue"
          @click="emit('clear')"
          type="button"
          class="text-xs text-slate-400 hover:text-slate-200 px-2 py-1 rounded bg-slate-800/60 hover:bg-slate-800 transition-colors flex items-center gap-1"
        >
          <X class="w-3 h-3" />
          Wyczyść
        </button>
      </div>
    </div>

    <div class="mb-5">
      <div class="text-xs font-medium text-slate-400 mb-2.5 flex items-center gap-1.5">
        <Sparkles class="w-3.5 h-3.5 text-cyan-400" />
        Szybki test (Przykłady / Use Cases z polskiej debaty publicznej):
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        <button
          v-for="useCase in POLISH_POLITICAL_USE_CASES"
          :key="useCase.id"
          type="button"
          @click="selectUseCase(useCase)"
          :class="[
            'text-left p-3 rounded-xl border transition-all text-xs flex flex-col justify-between group relative overflow-hidden',
            getUseCaseColorClass(useCase.id),
            modelValue === useCase.text ? 'ring-2 ring-cyan-500 shadow-md' : ''
          ]"
        >
          <div class="flex items-center justify-between gap-1 mb-1.5">
            <span class="font-semibold flex items-center gap-1.5 text-slate-100">
              <component :is="getUseCaseIcon(useCase.id)" class="w-3.5 h-3.5 shrink-0" />
              {{ useCase.title }}
            </span>
          </div>
          <span class="text-[11px] opacity-80 line-clamp-2 leading-relaxed">
            {{ useCase.description }}
          </span>
          <div class="mt-2 flex items-center justify-between text-[10px] text-slate-400">
            <span class="px-1.5 py-0.5 rounded bg-slate-900/60 font-mono border border-slate-800/80">{{ useCase.expectedVerdict }}</span>
            <span class="group-hover:translate-x-0.5 transition-transform text-cyan-400 font-medium">Użyj &rarr;</span>
          </div>
        </button>
      </div>
    </div>

    <form @submit.prevent="emit('submit')" class="space-y-4">
      <div class="relative">
        <textarea
          :value="modelValue"
          @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
          rows="4"
          placeholder="Wklej treść wpisu z platformy X, wypowiedź polityka lub oświadczenie..."
          class="w-full bg-slate-950/80 border border-slate-800 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 rounded-xl p-4 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:outline-none resize-y min-h-[110px]"
          :disabled="isLoading"
        ></textarea>
      </div>

      <div v-if="errorMessage" class="p-3.5 rounded-xl border border-rose-900/80 bg-rose-950/40 text-xs text-rose-300 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-start gap-2.5">
          <AlertCircle class="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <div>
            <div class="font-semibold text-rose-200">Błąd komunikacji</div>
            <div class="text-rose-300/90 leading-relaxed">{{ errorMessage }}</div>
          </div>
        </div>
        <button
          v-if="!useMock"
          type="button"
          @click="emit('enableMockAndSubmit')"
          class="shrink-0 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold transition-colors flex items-center justify-center gap-1.5 text-xs shadow"
        >
          <Sparkles class="w-3.5 h-3.5" />
          Włącz tryb Mock i analizuj
        </button>
      </div>

      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 pt-1">
        <div class="text-xs text-slate-400 flex items-center gap-2">
          <span class="inline-block w-2 h-2 rounded-full" :class="useMock ? 'bg-amber-400' : 'bg-cyan-400'"></span>
          <span>Analiza przez: <strong :class="useMock ? 'text-amber-300' : 'text-cyan-300'">{{ useMock ? 'Lokalny silnik symulacji (Mock)' : 'API FastAPI (http://localhost:8000)' }}</strong></span>
        </div>

        <button
          type="submit"
          :disabled="isLoading || !modelValue.trim()"
          class="w-full sm:w-auto px-6 py-2.5 rounded-xl font-semibold text-sm transition-all flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-cyan-500/20 active:scale-[0.98]"
        >
          <RefreshCw v-if="isLoading" class="w-4 h-4 animate-spin" />
          <Send v-else class="w-4 h-4" />
          <span>{{ isLoading ? 'Analizowanie wpisu...' : 'Analizuj wpis' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>
