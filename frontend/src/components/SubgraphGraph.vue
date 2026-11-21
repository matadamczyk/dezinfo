<script setup lang="ts">
import { ref, computed } from 'vue';
import { Network, Table, Eye } from 'lucide-vue-next';

const props = defineProps<{
  edges: [string, string, string][];
}>();

const activeView = ref<'svg' | 'table'>('svg');
const hoveredNode = ref<string | null>(null);
const selectedNode = ref<string | null>(null);

const uniqueNodes = computed(() => {
  const set = new Set<string>();
  props.edges.forEach(([src, , tgt]) => {
    if (src) set.add(src);
    if (tgt) set.add(tgt);
  });
  return Array.from(set);
});

const nodeDegrees = computed(() => {
  const counts: Record<string, number> = {};
  uniqueNodes.value.forEach((node) => {
    counts[node] = 0;
  });
  props.edges.forEach(([src, , tgt]) => {
    if (counts[src] !== undefined) counts[src] += 1;
    if (counts[tgt] !== undefined) counts[tgt] += 1;
  });
  return counts;
});

const sortedNodes = computed(() => {
  return [...uniqueNodes.value].sort((a, b) => (nodeDegrees.value[b] || 0) - (nodeDegrees.value[a] || 0));
});

const nodePositions = computed(() => {
  const positions: Record<string, { x: number; y: number; isCenter: boolean }> = {};
  const nodes = sortedNodes.value;
  const count = nodes.length;

  if (count === 0) return positions;

  const width = 820;
  const height = 440;
  const cx = width / 2;
  const cy = height / 2;

  if (count === 1) {
    positions[nodes[0]] = { x: cx, y: cy, isCenter: true };
    return positions;
  }

  if (count === 2) {
    positions[nodes[0]] = { x: cx - 180, y: cy, isCenter: false };
    positions[nodes[1]] = { x: cx + 180, y: cy, isCenter: false };
    return positions;
  }

  const primaryDegree = nodeDegrees.value[nodes[0]] || 0;
  const secondaryDegree = nodeDegrees.value[nodes[1]] || 0;
  const hasDistinctHub = primaryDegree >= 3 && primaryDegree > secondaryDegree;

  if (hasDistinctHub) {
    positions[nodes[0]] = { x: cx, y: cy, isCenter: true };
    const remaining = nodes.slice(1);
    const rx = 290;
    const ry = 150;
    remaining.forEach((node, idx) => {
      const angle = (idx * 2 * Math.PI) / remaining.length - Math.PI / 2;
      positions[node] = {
        x: cx + rx * Math.cos(angle),
        y: cy + ry * Math.sin(angle),
        isCenter: false,
      };
    });
  } else {
    const rx = 290;
    const ry = 155;
    nodes.forEach((node, idx) => {
      const angle = (idx * 2 * Math.PI) / count - Math.PI / 2;
      positions[node] = {
        x: cx + rx * Math.cos(angle),
        y: cy + ry * Math.sin(angle),
        isCenter: false,
      };
    });
  }

  return positions;
});

function getRelationColor(relation: string) {
  const rel = relation.toLowerCase();
  if (rel.includes('sprzecz') || rel.includes('błęd') || rel.includes('kłam') || rel.includes('manip')) {
    return {
      stroke: '#f43f5e',
      bg: '#4c0519',
      border: '#be123c',
      text: '#fda4af',
      marker: 'url(#arrow-rose)',
    };
  }
  if (rel.includes('gwarant') || rel.includes('oficjal') || rel.includes('zgodn') || rel.includes('finans') || rel.includes('potwierdz')) {
    return {
      stroke: '#10b981',
      bg: '#022c22',
      border: '#047857',
      text: '#6ee7b7',
      marker: 'url(#arrow-emerald)',
    };
  }
  return {
    stroke: '#38bdf8',
    bg: '#082f49',
    border: '#0284c7',
    text: '#7dd3fc',
    marker: 'url(#arrow-cyan)',
  };
}

function getNodeStyle(node: string) {
  const pos = nodePositions.value[node];
  const isSelected = selectedNode.value === node;
  const isHovered = hoveredNode.value === node;
  const isSubject = node.toLowerCase().includes('wpis') || node.toLowerCase().includes('tweet') || node.toLowerCase().includes('post') || pos?.isCenter;

  if (isSelected || isHovered) {
    return {
      fill: '#1e293b',
      stroke: '#38bdf8',
      strokeWidth: 2.5,
      textColor: '#f8fafc',
    };
  }

  if (isSubject) {
    return {
      fill: '#0f2942',
      stroke: '#0284c7',
      strokeWidth: 2,
      textColor: '#e0f2fe',
    };
  }

  return {
    fill: '#0f172a',
    stroke: '#334155',
    strokeWidth: 1.5,
    textColor: '#cbd5e1',
  };
}

function formatNodeLabel(name: string) {
  return name.replace(/_/g, ' ');
}

function formatRelationLabel(name: string) {
  return name.replace(/_/g, ' ');
}

function computeEdgeCurve(src: string, tgt: string, index: number) {
  const p1 = nodePositions.value[src];
  const p2 = nodePositions.value[tgt];
  if (!p1 || !p2) return null;

  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist === 0) return null;

  const nodeRadius = 55;
  const startX = p1.x + (dx / dist) * nodeRadius;
  const startY = p1.y + (dy / dist) * 22;
  const endX = p2.x - (dx / dist) * (nodeRadius + 6);
  const endY = p2.y - (dy / dist) * 22;

  const curvature = (index % 2 === 0 ? 1 : -1) * 20;
  const midX = (startX + endX) / 2;
  const midY = (startY + endY) / 2;
  const nx = -dy / dist;
  const ny = dx / dist;

  const ctrlX = midX + nx * curvature;
  const ctrlY = midY + ny * curvature;

  const labelX = (startX + 2 * ctrlX + endX) / 4;
  const labelY = (startY + 2 * ctrlY + endY) / 4;

  const path = `M ${startX.toFixed(1)} ${startY.toFixed(1)} Q ${ctrlX.toFixed(1)} ${ctrlY.toFixed(1)} ${endX.toFixed(1)} ${endY.toFixed(1)}`;

  return {
    path,
    labelX,
    labelY,
  };
}

function handleNodeClick(node: string) {
  if (selectedNode.value === node) {
    selectedNode.value = null;
  } else {
    selectedNode.value = node;
  }
}
</script>

<template>
  <div class="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 sm:p-6 shadow-xl backdrop-blur">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
      <div>
        <h3 class="text-base sm:text-lg font-semibold text-white flex items-center gap-2">
          <Network class="w-5 h-5 text-cyan-400" />
          <span>Wizualizacja Podgrafu Faktograficznego (Hybrid GraphRAG)</span>
        </h3>
        <p class="text-xs text-slate-400">Powiązania semantyczne z bazy wiedzy wykorzystane do fact-checkingu twierdzeń</p>
      </div>

      <div class="flex items-center gap-2 self-start sm:self-auto">
        <div class="flex items-center gap-1.5 p-1 rounded-xl bg-slate-950 border border-slate-800 text-xs">
          <button
            type="button"
            @click="activeView = 'svg'"
            :class="[
              'px-2.5 py-1 font-medium rounded-lg flex items-center gap-1.5 transition-all',
              activeView === 'svg' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            ]"
          >
            <Eye class="w-3.5 h-3.5" />
            <span>Graf SVG</span>
          </button>
          <button
            type="button"
            @click="activeView = 'table'"
            :class="[
              'px-2.5 py-1 font-medium rounded-lg flex items-center gap-1.5 transition-all',
              activeView === 'table' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            ]"
          >
            <Table class="w-3.5 h-3.5" />
            <span>Krawędzie ({{ edges.length }})</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="edges.length === 0" class="py-12 text-center rounded-xl border border-slate-800/60 bg-slate-950/40">
      <Network class="w-10 h-10 text-slate-600 mx-auto mb-2" />
      <p class="text-sm text-slate-400">Brak powiązanych krawędzi w podgrafie dla tego wpisu.</p>
    </div>

    <div v-else-if="activeView === 'svg'" class="space-y-3">
      <div class="relative w-full overflow-hidden rounded-xl border border-slate-800/90 bg-slate-950/90 shadow-inner">
        <svg
          viewBox="0 0 820 440"
          class="w-full h-auto min-h-[340px] max-h-[520px] select-none"
        >
          <defs>
            <marker
              id="arrow-cyan"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#38bdf8" />
            </marker>

            <marker
              id="arrow-rose"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#f43f5e" />
            </marker>

            <marker
              id="arrow-emerald"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#10b981" />
            </marker>
          </defs>

          <g>
            <template v-for="(edge, idx) in edges" :key="`edge-${idx}`">
              <template v-if="computeEdgeCurve(edge[0], edge[2], idx)">
                <path
                  :d="computeEdgeCurve(edge[0], edge[2], idx)!.path"
                  fill="none"
                  :stroke="getRelationColor(edge[1]).stroke"
                  :stroke-width="selectedNode && (selectedNode === edge[0] || selectedNode === edge[2]) ? 3 : 1.7"
                  :stroke-opacity="selectedNode && (selectedNode !== edge[0] && selectedNode !== edge[2]) ? 0.2 : 0.85"
                  :marker-end="getRelationColor(edge[1]).marker"
                  class="transition-all duration-300"
                />

                <g
                  :transform="`translate(${computeEdgeCurve(edge[0], edge[2], idx)!.labelX}, ${computeEdgeCurve(edge[0], edge[2], idx)!.labelY})`"
                  class="cursor-pointer"
                >
                  <rect
                    :x="-Math.max(38, formatRelationLabel(edge[1]).length * 3.6)"
                    y="-10"
                    :width="Math.max(76, formatRelationLabel(edge[1]).length * 7.2)"
                    height="20"
                    rx="6"
                    :fill="getRelationColor(edge[1]).bg"
                    :stroke="getRelationColor(edge[1]).border"
                    stroke-width="1"
                    class="shadow"
                  />
                  <text
                    x="0"
                    y="0"
                    text-anchor="middle"
                    dominant-baseline="central"
                    :fill="getRelationColor(edge[1]).text"
                    font-size="9.5"
                    font-family="monospace"
                    font-weight="600"
                  >
                    {{ formatRelationLabel(edge[1]) }}
                  </text>
                </g>
              </template>
            </template>
          </g>

          <g>
            <g
              v-for="node in uniqueNodes"
              :key="`node-${node}`"
              :transform="`translate(${nodePositions[node]?.x || 0}, ${nodePositions[node]?.y || 0})`"
              class="cursor-pointer"
              @mouseenter="hoveredNode = node"
              @mouseleave="hoveredNode = null"
              @click="handleNodeClick(node)"
            >
              <rect
                x="-65"
                y="-20"
                width="130"
                height="40"
                rx="10"
                :fill="getNodeStyle(node).fill"
                :stroke="getNodeStyle(node).stroke"
                :stroke-width="getNodeStyle(node).strokeWidth"
                class="transition-all duration-200"
              />

              <circle
                x="-52"
                cx="-48"
                cy="0"
                r="4"
                :fill="node.toLowerCase().includes('wpis') ? '#38bdf8' : '#10b981'"
              />

              <text
                x="4"
                y="0"
                text-anchor="middle"
                dominant-baseline="central"
                :fill="getNodeStyle(node).textColor"
                font-size="11"
                font-weight="600"
              >
                {{ formatNodeLabel(node).length > 17 ? formatNodeLabel(node).slice(0, 16) + '…' : formatNodeLabel(node) }}
              </text>
            </g>
          </g>
        </svg>

        <div class="absolute bottom-2.5 right-3 flex items-center gap-3 text-[10px] text-slate-400 bg-slate-900/90 border border-slate-800/80 px-2.5 py-1 rounded-lg backdrop-blur">
          <span class="flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-cyan-400"></span> Węzeł zapytania
          </span>
          <span class="flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span> Fakt referencyjny
          </span>
          <span class="flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-rose-400"></span> Sprzeczność
          </span>
        </div>
      </div>

      <div class="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>Kliknij węzeł na grafie, aby wyróżnić jego połączenia i krawędzie.</span>
        <span>Liczba węzłów: <strong class="text-slate-200">{{ uniqueNodes.length }}</strong>, relacji: <strong class="text-slate-200">{{ edges.length }}</strong></span>
      </div>
    </div>

    <div v-else class="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60">
      <table class="w-full text-left text-xs">
        <thead class="bg-slate-900/90 text-slate-400 uppercase tracking-wider font-mono border-b border-slate-800">
          <tr>
            <th class="px-4 py-3">Źródło (Węzeł A)</th>
            <th class="px-4 py-3">Relacja (Krawędź)</th>
            <th class="px-4 py-3">Cel (Węzeł B)</th>
            <th class="px-4 py-3 text-right">Typ powiązania</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60 text-slate-300">
          <tr v-for="(edge, idx) in edges" :key="idx" class="hover:bg-slate-900/40 transition-colors">
            <td class="px-4 py-3 font-semibold text-slate-100 font-mono">
              {{ formatNodeLabel(edge[0]) }}
            </td>
            <td class="px-4 py-3">
              <span
                class="px-2 py-0.5 rounded text-[11px] font-mono border"
                :style="{
                  backgroundColor: getRelationColor(edge[1]).bg,
                  color: getRelationColor(edge[1]).text,
                  borderColor: getRelationColor(edge[1]).border
                }"
              >
                {{ formatRelationLabel(edge[1]) }}
              </span>
            </td>
            <td class="px-4 py-3 font-semibold text-slate-100 font-mono">
              {{ formatNodeLabel(edge[2]) }}
            </td>
            <td class="px-4 py-3 text-right text-slate-400">
              <span v-if="edge[1].toLowerCase().includes('sprzecz') || edge[1].toLowerCase().includes('błęd')" class="text-rose-400 font-medium">Sprzeczność</span>
              <span v-else-if="edge[1].toLowerCase().includes('gwarant') || edge[1].toLowerCase().includes('oficjal')" class="text-emerald-400 font-medium">Potwierdzenie</span>
              <span v-else class="text-cyan-400 font-medium">Semantyka</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
