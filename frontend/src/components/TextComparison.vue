<script setup lang="ts">
import { ref } from 'vue';
import { Copy, Check, Columns, Layers, FileText, ShieldAlert, Sparkles } from 'lucide-vue-next';

const props = defineProps<{
  originalText: string;
  censoredText: string;
  neutralizedText: string;
}>();

const viewMode = ref<'columns' | 'tabs'>('columns');
const activeTab = ref<'original' | 'censored' | 'neutralized'>('neutralized');
const copiedTarget = ref<string | null>(null);

async function copyToClipboard(text: string, id: string) {
  try {
    await navigator.clipboard.writeText(text);
    copiedTarget.value = id;
    setTimeout(() => {
      if (copiedTarget.value === id) {
        copiedTarget.value = null;
      }
    }, 2000);
  } catch {
    copiedTarget.value = null;
  }
}

function renderCensoredTokens(text: string) {
  const parts = text.split(/(\[[^\]]+\])/g);
  return parts.map((part) => {
    const isToken = part.startsWith('[') && part.endsWith(']');
    return {
      text: part,
      isToken,
    };
  });
}
</script>

<template>
  <div class="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 sm:p-6 shadow-xl backdrop-blur">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
      <div>
        <h3 class="text-base sm:text-lg font-semibold text-white flex items-center gap-2">
          <FileText class="w-5 h-5 text-cyan-400" />
          <span>Porównanie Wariantów Tekstu</span>
        </h3>
        <p class="text-xs text-slate-400">Oryginalna treść vs Wersja z usuniętą toksycznością vs Neutralna korekta faktograficzna</p>
      </div>

      <div class="flex items-center gap-1.5 p-1 rounded-xl bg-slate-950 border border-slate-800 self-start sm:self-auto">
        <button
          type="button"
          @click="viewMode = 'columns'"
          :class="[
            'px-2.5 py-1 text-xs font-medium rounded-lg flex items-center gap-1.5 transition-all',
            viewMode === 'columns' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
          ]"
        >
          <Columns class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">3 kolumny</span>
        </button>

        <button
          type="button"
          @click="viewMode = 'tabs'"
          :class="[
            'px-2.5 py-1 text-xs font-medium rounded-lg flex items-center gap-1.5 transition-all',
            viewMode === 'tabs' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
          ]"
        >
          <Layers class="w-3.5 h-3.5" />
          <span>Zakładki</span>
        </button>
      </div>
    </div>

    <div v-if="viewMode === 'tabs'" class="mb-4 flex items-center gap-2 border-b border-slate-800 pb-3">
      <button
        type="button"
        @click="activeTab = 'original'"
        :class="[
          'px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all',
          activeTab === 'original' ? 'bg-slate-800 text-slate-100 border border-slate-700' : 'text-slate-400 hover:text-slate-200'
        ]"
      >
        <span class="w-2 h-2 rounded-full bg-slate-400"></span>
        Oryginał
      </button>

      <button
        type="button"
        @click="activeTab = 'censored'"
        :class="[
          'px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all',
          activeTab === 'censored' ? 'bg-rose-950/70 text-rose-300 border border-rose-800' : 'text-slate-400 hover:text-slate-200'
        ]"
      >
        <span class="w-2 h-2 rounded-full bg-rose-500"></span>
        Ocenzurowany
      </button>

      <button
        type="button"
        @click="activeTab = 'neutralized'"
        :class="[
          'px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all',
          activeTab === 'neutralized' ? 'bg-emerald-950/70 text-emerald-300 border border-emerald-800' : 'text-slate-400 hover:text-slate-200'
        ]"
      >
        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
        Korekta merytoryczna
      </button>
    </div>

    <div
      v-if="viewMode === 'columns'"
      class="grid grid-cols-1 lg:grid-cols-3 gap-4"
    >
      <div class="rounded-xl border border-slate-800 bg-slate-950/70 p-4 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3 pb-2 border-b border-slate-800/80">
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-slate-400"></span>
              Oryginalny wpis (X)
            </span>
            <button
              @click="copyToClipboard(originalText, 'orig-col')"
              class="text-[11px] text-slate-400 hover:text-slate-200 flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-800 transition-colors"
            >
              <Check v-if="copiedTarget === 'orig-col'" class="w-3 h-3 text-emerald-400" />
              <Copy v-else class="w-3 h-3" />
              <span>{{ copiedTarget === 'orig-col' ? 'Skopiowano' : 'Kopiuj' }}</span>
            </button>
          </div>
          <p class="text-sm text-slate-200 leading-relaxed font-normal whitespace-pre-wrap">
            {{ originalText }}
          </p>
        </div>
        <div class="mt-4 pt-3 border-t border-slate-800/60 text-[11px] text-slate-500 flex justify-between">
          <span>Format: Wejściowy</span>
          <span>{{ originalText.length }} znaków</span>
        </div>
      </div>

      <div class="rounded-xl border border-rose-900/40 bg-gradient-to-b from-rose-950/20 to-slate-950/70 p-4 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3 pb-2 border-b border-rose-900/50">
            <span class="text-xs font-semibold uppercase tracking-wider text-rose-300 flex items-center gap-1.5">
              <ShieldAlert class="w-3.5 h-3.5 text-rose-400" />
              Wersja ocenzurowana
            </span>
            <button
              @click="copyToClipboard(censoredText, 'cens-col')"
              class="text-[11px] text-slate-400 hover:text-slate-200 flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-800 transition-colors"
            >
              <Check v-if="copiedTarget === 'cens-col'" class="w-3 h-3 text-emerald-400" />
              <Copy v-else class="w-3 h-3" />
              <span>{{ copiedTarget === 'cens-col' ? 'Skopiowano' : 'Kopiuj' }}</span>
            </button>
          </div>
          <div class="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
            <template v-for="(seg, idx) in renderCensoredTokens(censoredText)" :key="idx">
              <span
                v-if="seg.isToken"
                class="inline-block px-1.5 py-0.5 mx-0.5 text-xs font-bold font-mono rounded bg-rose-900/80 text-rose-200 border border-rose-700/80 shadow-sm"
              >
                {{ seg.text }}
              </span>
              <span v-else>{{ seg.text }}</span>
            </template>
          </div>
        </div>
        <div class="mt-4 pt-3 border-t border-rose-950/60 text-[11px] text-rose-400/80 flex justify-between">
          <span>Filtr toksyczności</span>
          <span>Bezpieczny podgląd</span>
        </div>
      </div>

      <div class="rounded-xl border border-emerald-800/50 bg-gradient-to-b from-emerald-950/20 to-slate-950/70 p-4 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3 pb-2 border-b border-emerald-900/50">
            <span class="text-xs font-semibold uppercase tracking-wider text-emerald-300 flex items-center gap-1.5">
              <Sparkles class="w-3.5 h-3.5 text-emerald-400" />
              Neutralna korekta
            </span>
            <button
              @click="copyToClipboard(neutralizedText, 'neut-col')"
              class="text-[11px] text-slate-400 hover:text-slate-200 flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-800 transition-colors"
            >
              <Check v-if="copiedTarget === 'neut-col'" class="w-3 h-3 text-emerald-400" />
              <Copy v-else class="w-3 h-3" />
              <span>{{ copiedTarget === 'neut-col' ? 'Skopiowano' : 'Kopiuj' }}</span>
            </button>
          </div>
          <p class="text-sm text-emerald-100/90 leading-relaxed font-normal whitespace-pre-wrap">
            {{ neutralizedText }}
          </p>
        </div>
        <div class="mt-4 pt-3 border-t border-emerald-950/60 text-[11px] text-emerald-400/80 flex justify-between">
          <span>Zweryfikowany fakt</span>
          <span>Styl neutralny</span>
        </div>
      </div>
    </div>

    <div v-else class="rounded-xl border border-slate-800 bg-slate-950/80 p-5">
      <div v-if="activeTab === 'original'" class="space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
          <span class="text-xs font-semibold text-slate-400">Oryginalna treść posta</span>
          <button
            @click="copyToClipboard(originalText, 'orig-tab')"
            class="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 px-2.5 py-1 rounded bg-slate-900 border border-slate-800"
          >
            <Check v-if="copiedTarget === 'orig-tab'" class="w-3 h-3 text-emerald-400" />
            <Copy v-else class="w-3 h-3" />
            <span>{{ copiedTarget === 'orig-tab' ? 'Skopiowano' : 'Kopiuj' }}</span>
          </button>
        </div>
        <p class="text-sm sm:text-base text-slate-200 leading-relaxed whitespace-pre-wrap">{{ originalText }}</p>
      </div>

      <div v-else-if="activeTab === 'censored'" class="space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-rose-900/60">
          <span class="text-xs font-semibold text-rose-300">Wersja po odfiltrowaniu wulgaryzmów i mowy nienawiści</span>
          <button
            @click="copyToClipboard(censoredText, 'cens-tab')"
            class="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 px-2.5 py-1 rounded bg-slate-900 border border-slate-800"
          >
            <Check v-if="copiedTarget === 'cens-tab'" class="w-3 h-3 text-emerald-400" />
            <Copy v-else class="w-3 h-3" />
            <span>{{ copiedTarget === 'cens-tab' ? 'Skopiowano' : 'Kopiuj' }}</span>
          </button>
        </div>
        <div class="text-sm sm:text-base text-slate-200 leading-relaxed whitespace-pre-wrap">
          <template v-for="(seg, idx) in renderCensoredTokens(censoredText)" :key="idx">
            <span
              v-if="seg.isToken"
              class="inline-block px-1.5 py-0.5 mx-0.5 text-xs font-bold font-mono rounded bg-rose-900/80 text-rose-200 border border-rose-700/80 shadow-sm"
            >
              {{ seg.text }}
            </span>
            <span v-else>{{ seg.text }}</span>
          </template>
        </div>
      </div>

      <div v-else class="space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-emerald-900/60">
          <span class="text-xs font-semibold text-emerald-300">Zneutralizowana korekta faktograficzna</span>
          <button
            @click="copyToClipboard(neutralizedText, 'neut-tab')"
            class="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1 px-2.5 py-1 rounded bg-slate-900 border border-slate-800"
          >
            <Check v-if="copiedTarget === 'neut-tab'" class="w-3 h-3 text-emerald-400" />
            <Copy v-else class="w-3 h-3" />
            <span>{{ copiedTarget === 'neut-tab' ? 'Skopiowano' : 'Kopiuj' }}</span>
          </button>
        </div>
        <p class="text-sm sm:text-base text-emerald-100 leading-relaxed whitespace-pre-wrap">{{ neutralizedText }}</p>
      </div>
    </div>
  </div>
</template>
