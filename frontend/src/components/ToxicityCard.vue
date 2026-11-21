<script setup lang="ts">
import { computed } from 'vue';
import { Flame, ShieldCheck, Activity, Frown, Meh, Smile } from 'lucide-vue-next';

const props = defineProps<{
  toxicityScore: number;
  sentiment: string;
  isToxic: boolean;
}>();

const scorePercent = computed(() => {
  const raw = props.toxicityScore;
  const val = raw > 1 ? raw : raw * 100;
  return Math.min(100, Math.max(0, Math.round(val)));
});

const toxicityLevel = computed(() => {
  if (scorePercent.value >= 70) {
    return {
      label: 'Wysoka toksyczność',
      color: 'text-rose-400',
      barColor: 'from-amber-500 to-rose-500',
      badgeBg: 'bg-rose-950/60 text-rose-300 border-rose-800/80',
    };
  }
  if (scorePercent.value >= 35) {
    return {
      label: 'Umiarkowana toksyczność',
      color: 'text-amber-400',
      barColor: 'from-emerald-500 via-yellow-500 to-amber-500',
      badgeBg: 'bg-amber-950/60 text-amber-300 border-amber-800/80',
    };
  }
  return {
    label: 'Niska / Brak toksyczności',
    color: 'text-emerald-400',
    barColor: 'from-emerald-500 to-teal-400',
    badgeBg: 'bg-emerald-950/60 text-emerald-300 border-emerald-800/80',
  };
});

const sentimentConfig = computed(() => {
  const s = props.sentiment.toLowerCase();
  if (s.includes('neg') || s === 'negative') {
    return {
      label: 'Negatywny',
      icon: Frown,
      badge: 'bg-rose-950/50 text-rose-300 border-rose-800/60',
      color: 'text-rose-400',
    };
  }
  if (s.includes('pos') || s === 'positive') {
    return {
      label: 'Pozytywny',
      icon: Smile,
      badge: 'bg-emerald-950/50 text-emerald-300 border-emerald-800/60',
      color: 'text-emerald-400',
    };
  }
  return {
    label: 'Neutralny',
    icon: Meh,
    badge: 'bg-slate-800/60 text-slate-300 border-slate-700/60',
    color: 'text-cyan-400',
  };
});
</script>

<template>
  <div class="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 sm:p-6 shadow-xl backdrop-blur flex flex-col justify-between space-y-5">
    <div>
      <div class="flex items-center justify-between">
        <span class="text-xs uppercase font-mono tracking-wider text-slate-400 font-semibold flex items-center gap-1.5">
          <Activity class="w-4 h-4 text-cyan-400" />
          Styl i Wydźwięk Emocjonalny
        </span>

        <span
          v-if="isToxic"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40"
        >
          <Flame class="w-3.5 h-3.5 text-rose-400" />
          Wykryto toksyczność
        </span>
        <span
          v-else
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
        >
          <ShieldCheck class="w-3.5 h-3.5 text-emerald-400" />
          Brak toksyczności
        </span>
      </div>

      <div class="mt-4">
        <div class="flex items-end justify-between mb-2">
          <div>
            <div class="text-xs text-slate-400">Wskaźnik Toksyczności (Toxicity Score)</div>
            <div class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-baseline gap-2">
              <span>{{ scorePercent }}%</span>
              <span class="text-xs font-medium" :class="toxicityLevel.color">
                ({{ toxicityLevel.label }})
              </span>
            </div>
          </div>
        </div>

        <div class="w-full bg-slate-950 rounded-full h-3.5 p-0.5 border border-slate-800 overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-700 bg-gradient-to-r"
            :class="toxicityLevel.barColor"
            :style="{ width: `${scorePercent}%` }"
          ></div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3 pt-3 border-t border-slate-800/80">
      <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800/70">
        <div class="text-[11px] text-slate-400 uppercase tracking-wider font-mono">Sentyment</div>
        <div class="mt-1 flex items-center gap-2">
          <component :is="sentimentConfig.icon" class="w-4 h-4" :class="sentimentConfig.color" />
          <span class="text-sm font-semibold text-white">{{ sentimentConfig.label }}</span>
        </div>
      </div>

      <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800/70">
        <div class="text-[11px] text-slate-400 uppercase tracking-wider font-mono">Flaga Toksyczności</div>
        <div class="mt-1 flex items-center gap-2">
          <span
            class="text-sm font-semibold"
            :class="isToxic ? 'text-rose-400' : 'text-emerald-400'"
          >
            {{ isToxic ? 'Pozytywna (Toksyczny)' : 'Negatywna (Czysty)' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
