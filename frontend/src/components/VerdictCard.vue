<script setup lang="ts">
import { computed } from 'vue';
import { CheckCircle2, AlertOctagon, AlertTriangle, HelpCircle, ShieldAlert, Quote } from 'lucide-vue-next';
import type { VerdictType } from '../types/analysis';

const props = defineProps<{
  verdict: VerdictType;
  explanation: string;
}>();

const normalized = computed(() => {
  const v = props.verdict.trim();
  const upper = v.toUpperCase();
  if (upper === 'PRAWDA') return 'Prawda';
  if (upper === 'FAŁSZ' || upper === 'FALSZ') return 'Fałsz';
  if (upper === 'MANIPULACJA') return 'Manipulacja';
  return 'Brak danych';
});

const config = computed(() => {
  switch (normalized.value) {
    case 'Prawda':
      return {
        label: 'Prawda',
        sublabel: 'Informacja w pełni zweryfikowana i zgodna ze źródłami referencyjnymi',
        badgeBg: 'bg-[#ECF5E8] text-[#2D5A27] border-[#C8E0BE]',
        icon: CheckCircle2,
        iconColor: 'text-[#2D5A27]',
      };
    case 'Fałsz':
      return {
        label: 'Fałsz',
        sublabel: 'Informacja niezgodna ze stanem faktycznym, dezinformacja lub fake news',
        badgeBg: 'bg-[#FDF2F2] text-[#B91C1C] border-[#FECACA]',
        icon: AlertOctagon,
        iconColor: 'text-[#B91C1C]',
      };
    case 'Manipulacja':
      return {
        label: 'Manipulacja',
        sublabel: 'Wypowiedź zniekształca fakty, wyrywa dane z kontekstu lub wprowadza w błąd',
        badgeBg: 'bg-[#FEF7EC] text-[#B45309] border-[#FDE68A]',
        icon: AlertTriangle,
        iconColor: 'text-[#B45309]',
      };
    default:
      return {
        label: props.verdict || 'Brak danych',
        sublabel: 'Brak wystarczających źródeł w grafie wiedzy do jednoznacznej weryfikacji',
        badgeBg: 'bg-[#F3F4F6] text-[#4B5563] border-[#E5E7EB]',
        icon: HelpCircle,
        iconColor: 'text-[#4B5563]',
      };
  }
});
</script>

<template>
  <div class="rounded-2xl border border-[#E6E8E2] bg-white p-5 sm:p-6 shadow-xs flex flex-col justify-between h-full space-y-4">
    <div class="flex items-start justify-between gap-4">
      <div>
        <span class="text-xs uppercase font-mono tracking-wider text-[#646A61] font-semibold">Werdykt Fact-Checkingu</span>
        <div class="mt-2 flex items-center gap-3">
          <span :class="['inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-lg sm:text-xl font-bold border shadow-xs', config.badgeBg]">
            <component :is="config.icon" class="w-5 h-5 shrink-0" />
            {{ config.label }}
          </span>
        </div>
        <p class="text-xs text-[#646A61] mt-1.5">{{ config.sublabel }}</p>
      </div>

      <div class="hidden sm:flex p-3 rounded-xl bg-[#FAFBF9] border border-[#E6E8E2]">
        <ShieldAlert class="w-6 h-6" :class="config.iconColor" />
      </div>
    </div>

    <div class="mt-4 pt-4 border-t border-[#E6E8E2]">
      <div class="flex items-start gap-2.5">
        <Quote class="w-4 h-4 text-[#646A61] shrink-0 mt-0.5" />
        <div class="space-y-1">
          <h4 class="text-xs font-semibold uppercase tracking-wider text-[#646A61]">Uzasadnienie merytoryczne</h4>
          <p class="text-sm text-[#181A17] leading-relaxed">
            {{ explanation || 'Brak dodatkowego uzasadnienia tekstowego ze strony silnika weryfikacji.' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
