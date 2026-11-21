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
        badgeBg: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 ring-1 ring-emerald-500/30',
        cardBorder: 'border-emerald-800/60 bg-gradient-to-br from-emerald-950/30 via-slate-900/60 to-slate-950',
        glowBg: 'bg-emerald-500/10',
        icon: CheckCircle2,
        iconColor: 'text-emerald-400',
        textColor: 'text-emerald-300',
      };
    case 'Fałsz':
      return {
        label: 'Fałsz',
        sublabel: 'Informacja niezgodna ze stanem faktycznym, dezinformacja lub fake news',
        badgeBg: 'bg-rose-500/20 text-rose-300 border-rose-500/40 ring-1 ring-rose-500/30',
        cardBorder: 'border-rose-800/60 bg-gradient-to-br from-rose-950/30 via-slate-900/60 to-slate-950',
        glowBg: 'bg-rose-500/10',
        icon: AlertOctagon,
        iconColor: 'text-rose-400',
        textColor: 'text-rose-300',
      };
    case 'Manipulacja':
      return {
        label: 'Manipulacja',
        sublabel: 'Wypowiedź zniekształca fakty, wyrywa dane z kontekstu lub wprowadza w błąd',
        badgeBg: 'bg-amber-500/20 text-amber-300 border-amber-500/40 ring-1 ring-amber-500/30',
        cardBorder: 'border-amber-800/60 bg-gradient-to-br from-amber-950/30 via-slate-900/60 to-slate-950',
        glowBg: 'bg-amber-500/10',
        icon: AlertTriangle,
        iconColor: 'text-amber-400',
        textColor: 'text-amber-300',
      };
    default:
      return {
        label: props.verdict || 'Brak danych',
        sublabel: 'Brak wystarczających źródeł w grafie wiedzy do jednoznacznej weryfikacji',
        badgeBg: 'bg-slate-700/30 text-slate-300 border-slate-600/40 ring-1 ring-slate-600/30',
        cardBorder: 'border-slate-800 bg-gradient-to-br from-slate-900/60 via-slate-900/40 to-slate-950',
        glowBg: 'bg-slate-700/10',
        icon: HelpCircle,
        iconColor: 'text-slate-400',
        textColor: 'text-slate-300',
      };
  }
});
</script>

<template>
  <div :class="['rounded-2xl border p-5 sm:p-6 relative overflow-hidden shadow-xl backdrop-blur transition-all', config.cardBorder]">
    <div :class="['absolute -top-12 -right-12 w-48 h-48 rounded-full blur-3xl pointer-events-none', config.glowBg]"></div>

    <div class="relative z-10 flex flex-col justify-between h-full space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div>
          <span class="text-xs uppercase font-mono tracking-wider text-slate-400 font-semibold">Werdykt Fact-Checkingu</span>
          <div class="mt-2 flex items-center gap-3">
            <span :class="['inline-flex items-center gap-2 px-4 py-2 rounded-xl text-lg sm:text-xl font-bold border shadow-sm', config.badgeBg]">
              <component :is="config.icon" class="w-6 h-6 shrink-0" />
              {{ config.label }}
            </span>
          </div>
          <p class="text-xs text-slate-400 mt-1.5">{{ config.sublabel }}</p>
        </div>

        <div class="hidden sm:flex p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-slate-400">
          <ShieldAlert class="w-6 h-6" :class="config.iconColor" />
        </div>
      </div>

      <div class="mt-4 pt-4 border-t border-slate-800/80">
        <div class="flex items-start gap-2.5">
          <Quote class="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
          <div class="space-y-1">
            <h4 class="text-xs font-semibold uppercase tracking-wider text-slate-400">Uzasadnienie merytoryczne</h4>
            <p class="text-sm text-slate-200 leading-relaxed">
              {{ explanation || 'Brak dodatkowego uzasadnienia tekstowego ze strony silnika weryfikacji.' }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
