<script setup lang="ts">
import { Shield, Sparkles, Zap } from 'lucide-vue-next';

defineProps<{
  useMock: boolean;
  backendOnline: boolean | null;
}>();

const emit = defineEmits<{
  (e: 'update:useMock', value: boolean): void;
  (e: 'reset'): void;
}>();
</script>

<template>
  <header class="border-b border-[#E6E8E2] bg-white/95 backdrop-blur-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="h-9 w-9 rounded-xl bg-[#EDF2E7] text-[#3F5E2A] border border-[#DCE5D5] flex items-center justify-center">
          <Shield class="w-5 h-5" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-base sm:text-lg font-bold tracking-tight text-[#181A17]">Dezinfo Guard</span>
            <span class="px-2 py-0.5 text-xs font-semibold rounded-full bg-[#EDF2E7] text-[#3F5E2A] border border-[#DCE5D5] flex items-center gap-1">
              <Sparkles class="w-3 h-3 text-[#3F5E2A]" />
              Hybrid GraphRAG
            </span>
          </div>
          <p class="text-xs text-[#646A61] hidden sm:block">Detekcja dezinformacji, mowy nienawiści i fact-checking wpisów politycznych</p>
        </div>
      </div>

      <div class="flex items-center gap-3 sm:gap-4">
        <div class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#E6E8E2] bg-[#FAFBF9] text-xs">
          <span class="text-[#646A61]">Backend:</span>
          <span v-if="backendOnline === true" class="flex items-center gap-1.5 text-[#2D5A27] font-medium">
            <span class="w-2 h-2 rounded-full bg-[#2D5A27] animate-pulse"></span>
            Online
          </span>
          <span v-else-if="backendOnline === false" class="flex items-center gap-1.5 text-[#B91C1C] font-medium">
            <span class="w-2 h-2 rounded-full bg-[#B91C1C]"></span>
            Offline
          </span>
          <span v-else class="flex items-center gap-1.5 text-[#646A61] font-medium">
            <span class="w-2 h-2 rounded-full bg-[#9CA3AF]"></span>
            Sprawdzanie...
          </span>
        </div>

        <label class="flex items-center gap-2 cursor-pointer bg-white border border-[#E6E8E2] hover:border-[#D1D5DB] px-3 py-1.5 rounded-full transition-all shadow-xs">
          <div class="relative inline-flex items-center">
            <input
              type="checkbox"
              :checked="useMock"
              @change="emit('update:useMock', ($event.target as HTMLInputElement).checked)"
              class="sr-only peer"
            />
            <div class="w-8 h-4.5 bg-[#E6E8E2] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-3.5 after:w-3.5 after:transition-all peer-checked:bg-[#3F5E2A]"></div>
          </div>
          <div class="flex items-center gap-1.5 text-xs select-none">
            <Zap class="w-3.5 h-3.5" :class="useMock ? 'text-[#3F5E2A]' : 'text-[#646A61]'" />
            <span :class="useMock ? 'text-[#3F5E2A] font-semibold' : 'text-[#646A61]'">Tryb Mock (offline)</span>
          </div>
        </label>

        <button
          @click="emit('reset')"
          class="text-xs text-[#646A61] hover:text-[#181A17] px-3 py-1.5 rounded-full border border-[#E6E8E2] hover:bg-[#F6F7F4] transition-colors font-medium"
          title="Wyczyść formularz i wyniki"
        >
          Reset
        </button>
      </div>
    </div>
  </header>
</template>
