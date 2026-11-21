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
  <header class="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20 ring-1 ring-cyan-400/30">
          <Shield class="w-5 h-5" />
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-lg font-bold tracking-tight text-white">Dezinfo Guard</span>
            <span class="px-2 py-0.5 text-xs font-semibold rounded-full bg-cyan-950/80 text-cyan-300 border border-cyan-800/60 flex items-center gap-1">
              <Sparkles class="w-3 h-3 text-cyan-400" />
              Hybrid GraphRAG
            </span>
          </div>
          <p class="text-xs text-slate-400 hidden sm:block">Detekcja dezinformacji, mowy nienawiści i fact-checking wpisów politycznych</p>
        </div>
      </div>

      <div class="flex items-center gap-3 sm:gap-4">
        <div class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/60 text-xs">
          <span class="text-slate-400">Backend:</span>
          <span v-if="backendOnline === true" class="flex items-center gap-1.5 text-emerald-400 font-medium">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Online
          </span>
          <span v-else-if="backendOnline === false" class="flex items-center gap-1.5 text-rose-400 font-medium">
            <span class="w-2 h-2 rounded-full bg-rose-500"></span>
            Offline
          </span>
          <span v-else class="flex items-center gap-1.5 text-slate-400 font-medium">
            <span class="w-2 h-2 rounded-full bg-slate-500"></span>
            Sprawdzanie...
          </span>
        </div>

        <label class="flex items-center gap-2 cursor-pointer bg-slate-900/90 border border-slate-800 hover:border-slate-700 px-3 py-1.5 rounded-xl transition-all">
          <div class="relative inline-flex items-center">
            <input
              type="checkbox"
              :checked="useMock"
              @change="emit('update:useMock', ($event.target as HTMLInputElement).checked)"
              class="sr-only peer"
            />
            <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-amber-500"></div>
          </div>
          <div class="flex items-center gap-1.5 text-xs select-none">
            <Zap class="w-3.5 h-3.5" :class="useMock ? 'text-amber-400' : 'text-slate-400'" />
            <span :class="useMock ? 'text-amber-300 font-semibold' : 'text-slate-300'">Tryb Mock (offline)</span>
          </div>
        </label>

        <button
          @click="emit('reset')"
          class="text-xs text-slate-400 hover:text-slate-200 px-2.5 py-1.5 rounded-lg border border-slate-800 hover:bg-slate-800/60 transition-colors"
          title="Wyczyść formularz i wyniki"
        >
          Reset
        </button>
      </div>
    </div>
  </header>
</template>
