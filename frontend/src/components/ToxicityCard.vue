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
      color: 'text-[#B91C1C]',
      barColor: 'bg-[#B91C1C]',
    };
  }
  if (scorePercent.value >= 35) {
    return {
      label: 'Umiarkowana toksyczność',
      color: 'text-[#B45309]',
      barColor: 'bg-[#B45309]',
    };
  }
  return {
    label: 'Niska / Brak toksyczności',
    color: 'text-[#2D5A27]',
    barColor: 'bg-[#2D5A27]',
  };
});

const sentimentConfig = computed(() => {
  const s = props.sentiment.toLowerCase();
  if (s.includes('neg') || s === 'negative') {
    return {
      label: 'Negatywny',
      icon: Frown,
      color: 'text-[#B91C1C]',
    };
  }
  if (s.includes('pos') || s === 'positive') {
    return {
      label: 'Pozytywny',
      icon: Smile,
      color: 'text-[#2D5A27]',
    };
  }
  return {
    label: 'Neutralny',
    icon: Meh,
    color: 'text-[#646A61]',
  };
});
</script>

<template>
  <div class="rounded-2xl border border-[#E6E8E2] bg-white p-5 sm:p-6 shadow-xs flex flex-col justify-between space-y-5">
    <div>
      <div class="flex items-center justify-between">
        <span class="text-xs uppercase font-mono tracking-wider text-[#646A61] font-semibold flex items-center gap-1.5">
          <Activity class="w-4 h-4 text-[#3F5E2A]" />
          Styl i Wydźwięk Emocjonalny
        </span>

        <span
          v-if="isToxic"
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#FDF2F2] text-[#B91C1C] border border-[#FECACA]"
        >
          <Flame class="w-3.5 h-3.5 text-[#B91C1C]" />
          Wykryto toksyczność
        </span>
        <span
          v-else
          class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#ECF5E8] text-[#2D5A27] border border-[#C8E0BE]"
        >
          <ShieldCheck class="w-3.5 h-3.5 text-[#2D5A27]" />
          Brak toksyczności
        </span>
      </div>

      <div class="mt-4">
        <div class="flex items-end justify-between mb-2">
          <div>
            <div class="text-xs text-[#646A61]">Wskaźnik Toksyczności (Toxicity Score)</div>
            <div class="text-2xl sm:text-3xl font-extrabold text-[#181A17] tracking-tight flex items-baseline gap-2">
              <span>{{ scorePercent }}%</span>
              <span class="text-xs font-medium" :class="toxicityLevel.color">
                ({{ toxicityLevel.label }})
              </span>
            </div>
          </div>
        </div>

        <div class="w-full bg-[#F6F7F4] rounded-full h-3 p-0.5 border border-[#E6E8E2] overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-700"
            :class="toxicityLevel.barColor"
            :style="{ width: `${scorePercent}%` }"
          ></div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3 pt-3 border-t border-[#E6E8E2]">
      <div class="p-3 rounded-xl bg-[#FAFBF9] border border-[#E6E8E2]">
        <div class="text-[11px] text-[#646A61] uppercase tracking-wider font-mono">Sentyment</div>
        <div class="mt-1 flex items-center gap-2">
          <component :is="sentimentConfig.icon" class="w-4 h-4" :class="sentimentConfig.color" />
          <span class="text-sm font-semibold text-[#181A17]">{{ sentimentConfig.label }}</span>
        </div>
      </div>

      <div class="p-3 rounded-xl bg-[#FAFBF9] border border-[#E6E8E2]">
        <div class="text-[11px] text-[#646A61] uppercase tracking-wider font-mono">Flaga Toksyczności</div>
        <div class="mt-1 flex items-center gap-2">
          <span
            class="text-sm font-semibold"
            :class="isToxic ? 'text-[#B91C1C]' : 'text-[#2D5A27]'"
          >
            {{ isToxic ? 'Pozytywna (Toksyczny)' : 'Negatywna (Czysty)' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
