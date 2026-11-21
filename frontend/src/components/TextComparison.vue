<script setup lang="ts">
import { ref } from 'vue';
import { Copy, Check, Columns, Layers, FileText, ShieldAlert, Sparkles } from 'lucide-vue-next';

defineProps<{
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
  <div class="rounded-2xl border border-[#E6E8E2] bg-white p-5 sm:p-6 shadow-xs">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
      <div>
        <h3 class="text-base sm:text-lg font-bold text-[#181A17] flex items-center gap-2">
          <FileText class="w-5 h-5 text-[#3F5E2A]" />
          <span>Porównanie Wariantów Tekstu</span>
        </h3>
        <p class="text-xs text-[#646A61]">Oryginalna treść vs Wersja z usuniętą toksycznością vs Neutralna korekta faktograficzna</p>
      </div>

      <div class="flex items-center gap-1.5 p-1 rounded-xl bg-[#F6F7F4] border border-[#E6E8E2] self-start sm:self-auto">
        <button
          type="button"
          @click="viewMode = 'columns'"
          :class="[
            'px-2.5 py-1 text-xs font-medium rounded-lg flex items-center gap-1.5 transition-all',
            viewMode === 'columns' ? 'bg-[#3F5E2A] text-white shadow-xs' : 'text-[#646A61] hover:text-[#181A17]'
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
            viewMode === 'tabs' ? 'bg-[#3F5E2A] text-white shadow-xs' : 'text-[#646A61] hover:text-[#181A17]'
          ]"
        >
          <Layers class="w-3.5 h-3.5" />
          <span>Zakładki</span>
        </button>
      </div>
    </div>

    <div v-if="viewMode === 'tabs'" class="mb-4 flex items-center gap-2 border-b border-[#E6E8E2] pb-3">
      <button
        type="button"
        @click="activeTab = 'original'"
        :class="[
          'px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all',
          activeTab === 'original' ? 'bg-[#F6F7F4] text-[#181A17] border border-[#E6E8E2]' : 'text-[#646A61] hover:text-[#181A17]'
        ]"
      >
        <span class="w-2 h-2 rounded-full bg-[#646A61]"></span>
        Oryginał
      </button>

      <button
        type="button"
        @click="activeTab = 'censored'"
        :class="[
          'px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all',
          activeTab === 'censored' ? 'bg-[#FDF2F2] text-[#B91C1C] border border-[#FECACA]' : 'text-[#646A61] hover:text-[#181A17]'
        ]"
      >
        <span class="w-2 h-2 rounded-full bg-[#B91C1C]"></span>
        Ocenzurowany
      </button>

      <button
        type="button"
        @click="activeTab = 'neutralized'"
        :class="[
          'px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all',
          activeTab === 'neutralized' ? 'bg-[#ECF5E8] text-[#2D5A27] border border-[#C8E0BE]' : 'text-[#646A61] hover:text-[#181A17]'
        ]"
      >
        <span class="w-2 h-2 rounded-full bg-[#2D5A27]"></span>
        Korekta merytoryczna
      </button>
    </div>

    <div
      v-if="viewMode === 'columns'"
      class="grid grid-cols-1 lg:grid-cols-3 gap-4"
    >
      <div class="rounded-xl border border-[#E6E8E2] border-t-2 border-t-[#646A61] bg-[#FAFBF9] p-4 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3 pb-2 border-b border-[#E6E8E2]">
            <span class="text-xs font-semibold uppercase tracking-wider text-[#646A61] flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-[#646A61]"></span>
              Oryginalny wpis (X)
            </span>
            <button
              @click="copyToClipboard(originalText, 'orig-col')"
              class="text-[11px] text-[#646A61] hover:text-[#181A17] flex items-center gap-1 px-2 py-0.5 rounded bg-white border border-[#E6E8E2] transition-colors"
            >
              <Check v-if="copiedTarget === 'orig-col'" class="w-3 h-3 text-[#2D5A27]" />
              <Copy v-else class="w-3 h-3" />
              <span>{{ copiedTarget === 'orig-col' ? 'Skopiowano' : 'Kopiuj' }}</span>
            </button>
          </div>
          <p class="text-sm text-[#181A17] leading-relaxed font-normal whitespace-pre-wrap">
            {{ originalText }}
          </p>
        </div>
        <div class="mt-4 pt-3 border-t border-[#E6E8E2] text-[11px] text-[#646A61] flex justify-between">
          <span>Format: Wejściowy</span>
          <span>{{ originalText.length }} znaków</span>
        </div>
      </div>

      <div class="rounded-xl border border-[#FECACA] border-t-2 border-t-[#B91C1C] bg-[#FAFBF9] p-4 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3 pb-2 border-b border-[#FECACA]/60">
            <span class="text-xs font-semibold uppercase tracking-wider text-[#B91C1C] flex items-center gap-1.5">
              <ShieldAlert class="w-3.5 h-3.5 text-[#B91C1C]" />
              Wersja ocenzurowana
            </span>
            <button
              @click="copyToClipboard(censoredText, 'cens-col')"
              class="text-[11px] text-[#646A61] hover:text-[#181A17] flex items-center gap-1 px-2 py-0.5 rounded bg-white border border-[#E6E8E2] transition-colors"
            >
              <Check v-if="copiedTarget === 'cens-col'" class="w-3 h-3 text-[#2D5A27]" />
              <Copy v-else class="w-3 h-3" />
              <span>{{ copiedTarget === 'cens-col' ? 'Skopiowano' : 'Kopiuj' }}</span>
            </button>
          </div>
          <div class="text-sm text-[#181A17] leading-relaxed whitespace-pre-wrap">
            <template v-for="(seg, idx) in renderCensoredTokens(censoredText)" :key="idx">
              <span
                v-if="seg.isToken"
                class="inline-block px-1.5 py-0.5 mx-0.5 text-xs font-bold font-mono rounded bg-[#FDF2F2] text-[#B91C1C] border border-[#FECACA]"
              >
                {{ seg.text }}
              </span>
              <span v-else>{{ seg.text }}</span>
            </template>
          </div>
        </div>
        <div class="mt-4 pt-3 border-t border-[#FECACA]/60 text-[11px] text-[#B91C1C] flex justify-between">
          <span>Filtr toksyczności</span>
          <span>Bezpieczny podgląd</span>
        </div>
      </div>

      <div class="rounded-xl border border-[#C8E0BE] border-t-2 border-t-[#3F5E2A] bg-[#FAFBF9] p-4 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3 pb-2 border-b border-[#C8E0BE]/60">
            <span class="text-xs font-semibold uppercase tracking-wider text-[#2D5A27] flex items-center gap-1.5">
              <Sparkles class="w-3.5 h-3.5 text-[#3F5E2A]" />
              Neutralna korekta
            </span>
            <button
              @click="copyToClipboard(neutralizedText, 'neut-col')"
              class="text-[11px] text-[#646A61] hover:text-[#181A17] flex items-center gap-1 px-2 py-0.5 rounded bg-white border border-[#E6E8E2] transition-colors"
            >
              <Check v-if="copiedTarget === 'neut-col'" class="w-3 h-3 text-[#2D5A27]" />
              <Copy v-else class="w-3 h-3" />
              <span>{{ copiedTarget === 'neut-col' ? 'Skopiowano' : 'Kopiuj' }}</span>
            </button>
          </div>
          <p class="text-sm text-[#181A17] leading-relaxed font-normal whitespace-pre-wrap">
            {{ neutralizedText }}
          </p>
        </div>
        <div class="mt-4 pt-3 border-t border-[#C8E0BE]/60 text-[11px] text-[#2D5A27] flex justify-between">
          <span>Zweryfikowany fakt</span>
          <span>Styl neutralny</span>
        </div>
      </div>
    </div>

    <div v-else class="rounded-xl border border-[#E6E8E2] bg-[#FAFBF9] p-5">
      <div v-if="activeTab === 'original'" class="space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-[#E6E8E2]">
          <span class="text-xs font-semibold text-[#646A61]">Oryginalna treść posta</span>
          <button
            @click="copyToClipboard(originalText, 'orig-tab')"
            class="text-xs text-[#646A61] hover:text-[#181A17] flex items-center gap-1 px-2.5 py-1 rounded bg-white border border-[#E6E8E2]"
          >
            <Check v-if="copiedTarget === 'orig-tab'" class="w-3 h-3 text-[#2D5A27]" />
            <Copy v-else class="w-3 h-3" />
            <span>{{ copiedTarget === 'orig-tab' ? 'Skopiowano' : 'Kopiuj' }}</span>
          </button>
        </div>
        <p class="text-sm sm:text-base text-[#181A17] leading-relaxed whitespace-pre-wrap">{{ originalText }}</p>
      </div>

      <div v-else-if="activeTab === 'censored'" class="space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-[#FECACA]/60">
          <span class="text-xs font-semibold text-[#B91C1C]">Wersja po odfiltrowaniu wulgaryzmów i mowy nienawiści</span>
          <button
            @click="copyToClipboard(censoredText, 'cens-tab')"
            class="text-xs text-[#646A61] hover:text-[#181A17] flex items-center gap-1 px-2.5 py-1 rounded bg-white border border-[#E6E8E2]"
          >
            <Check v-if="copiedTarget === 'cens-tab'" class="w-3 h-3 text-[#2D5A27]" />
            <Copy v-else class="w-3 h-3" />
            <span>{{ copiedTarget === 'cens-tab' ? 'Skopiowano' : 'Kopiuj' }}</span>
          </button>
        </div>
        <div class="text-sm sm:text-base text-[#181A17] leading-relaxed whitespace-pre-wrap">
          <template v-for="(seg, idx) in renderCensoredTokens(censoredText)" :key="idx">
            <span
              v-if="seg.isToken"
              class="inline-block px-1.5 py-0.5 mx-0.5 text-xs font-bold font-mono rounded bg-[#FDF2F2] text-[#B91C1C] border border-[#FECACA]"
            >
              {{ seg.text }}
            </span>
            <span v-else>{{ seg.text }}</span>
          </template>
        </div>
      </div>

      <div v-else class="space-y-3">
        <div class="flex items-center justify-between pb-2 border-b border-[#C8E0BE]/60">
          <span class="text-xs font-semibold text-[#2D5A27]">Zneutralizowana korekta faktograficzna</span>
          <button
            @click="copyToClipboard(neutralizedText, 'neut-tab')"
            class="text-xs text-[#646A61] hover:text-[#181A17] flex items-center gap-1 px-2.5 py-1 rounded bg-white border border-[#E6E8E2]"
          >
            <Check v-if="copiedTarget === 'neut-tab'" class="w-3 h-3 text-[#2D5A27]" />
            <Copy v-else class="w-3 h-3" />
            <span>{{ copiedTarget === 'neut-tab' ? 'Skopiowano' : 'Kopiuj' }}</span>
          </button>
        </div>
        <p class="text-sm sm:text-base text-[#181A17] leading-relaxed whitespace-pre-wrap">{{ neutralizedText }}</p>
      </div>
    </div>
  </div>
</template>
