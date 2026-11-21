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
</script>

<template>
  <div class="bg-white border border-[#E6E8E2] rounded-2xl p-5 sm:p-6 shadow-xs">
    <div class="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
      <div>
        <h2 class="text-base sm:text-lg font-bold text-[#181A17] flex items-center gap-2">
          <span>Weryfikacja wypowiedzi / posta</span>
          <span class="text-xs font-normal text-[#646A61]"> (X/Twitter, portale, cytaty)</span>
        </h2>
        <p class="text-xs text-[#646A61]">Wprowadź tekst do analizy stylu, sentymentu, toksyczności oraz weryfikacji w grafie wiedzy.</p>
      </div>

      <div class="flex items-center gap-2">
        <span class="text-xs text-[#646A61] font-mono">{{ characterCount }} znaków</span>
        <button
          v-if="modelValue"
          @click="emit('clear')"
          type="button"
          class="text-xs text-[#646A61] hover:text-[#181A17] px-2.5 py-1 rounded-lg bg-[#F6F7F4] hover:bg-[#EDF2E7] border border-[#E6E8E2] transition-colors flex items-center gap-1"
        >
          <X class="w-3 h-3" />
          Wyczyść
        </button>
      </div>
    </div>

    <div class="mb-5">
      <div class="text-xs font-semibold text-[#181A17] mb-2.5 flex items-center gap-1.5">
        <Sparkles class="w-3.5 h-3.5 text-[#3F5E2A]" />
        Szybki test (Przykłady / Use Cases z polskiej debaty publicznej):
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        <button
          v-for="useCase in POLISH_POLITICAL_USE_CASES"
          :key="useCase.id"
          type="button"
          @click="selectUseCase(useCase)"
          :class="[
            'text-left p-3.5 rounded-xl border transition-all text-xs flex flex-col justify-between group cursor-pointer',
            modelValue === useCase.text
              ? 'border-[#3F5E2A] bg-[#EDF2E7] ring-1 ring-[#3F5E2A]'
              : 'border-[#E6E8E2] bg-[#F6F7F4] hover:bg-[#EDF2E7] hover:border-[#DCE5D5]'
          ]"
        >
          <div class="flex items-center justify-between gap-1 mb-1.5">
            <span class="font-semibold flex items-center gap-1.5 text-[#181A17]">
              <component :is="getUseCaseIcon(useCase.id)" class="w-3.5 h-3.5 shrink-0 text-[#3F5E2A]" />
              {{ useCase.title }}
            </span>
          </div>
          <span class="text-[11px] text-[#646A61] line-clamp-2 leading-relaxed">
            {{ useCase.description }}
          </span>
          <div class="mt-2.5 flex items-center justify-between text-[10px]">
            <span class="px-1.5 py-0.5 rounded bg-white font-mono border border-[#E6E8E2] text-[#646A61]">{{ useCase.expectedVerdict }}</span>
            <span class="group-hover:translate-x-0.5 transition-transform text-[#3F5E2A] font-semibold">Użyj &rarr;</span>
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
          class="w-full bg-[#FAFBF9] border border-[#E6E8E2] focus:border-[#3F5E2A] focus:ring-1 focus:ring-[#3F5E2A] rounded-xl p-4 text-sm text-[#181A17] placeholder-[#9CA3AF] transition-colors focus:outline-none resize-y min-h-[110px]"
          :disabled="isLoading"
        ></textarea>
      </div>

      <div v-if="errorMessage" class="p-3.5 rounded-xl border border-[#FECACA] bg-[#FDF2F2] text-xs text-[#B91C1C] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-start gap-2.5">
          <AlertCircle class="w-4 h-4 text-[#B91C1C] shrink-0 mt-0.5" />
          <div>
            <div class="font-semibold text-[#B91C1C]">Błąd komunikacji</div>
            <div class="text-[#B91C1C]/90 leading-relaxed">{{ errorMessage }}</div>
          </div>
        </div>
        <button
          v-if="!useMock"
          type="button"
          @click="emit('enableMockAndSubmit')"
          class="shrink-0 px-3 py-1.5 rounded-lg bg-[#3F5E2A] hover:bg-[#324B21] text-white font-semibold transition-colors flex items-center justify-center gap-1.5 text-xs shadow-xs"
        >
          <Sparkles class="w-3.5 h-3.5" />
          Włącz tryb Mock i analizuj
        </button>
      </div>

      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 pt-1">
        <div class="text-xs text-[#646A61] flex items-center gap-2">
          <span class="inline-block w-2 h-2 rounded-full bg-[#3F5E2A]"></span>
          <span>Analiza przez: <strong class="text-[#181A17]">{{ useMock ? 'Lokalny silnik symulacji (Mock)' : 'API FastAPI (http://localhost:8000)' }}</strong></span>
        </div>

        <button
          type="submit"
          :disabled="isLoading || !modelValue.trim()"
          class="w-full sm:w-auto px-6 py-2.5 rounded-xl font-semibold text-sm transition-all flex items-center justify-center gap-2 shadow-xs disabled:opacity-50 disabled:cursor-not-allowed bg-[#3F5E2A] hover:bg-[#324B21] text-white active:scale-[0.98]"
        >
          <RefreshCw v-if="isLoading" class="w-4 h-4 animate-spin" />
          <Send v-else class="w-4 h-4" />
          <span>{{ isLoading ? 'Analizowanie wpisu...' : 'Analizuj wpis' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>
