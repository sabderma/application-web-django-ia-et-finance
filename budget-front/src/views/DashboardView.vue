<template>
  <AppLayout>
    <h2>Dashboard</h2>

    <!-- ❌ supprimé : bouton Charger dashboard -->
    <p v-if="finance.loading" class="muted">Chargement...</p>

    <p v-if="finance.error" class="err">{{ errText(finance.error) }}</p>

    <div v-if="dash" class="cards">
      <div class="card"><b>Mois</b><div>{{ dash.month }}</div></div>
      <div class="card"><b>Salaire</b><div>{{ dash.profile.salaire_mensuel }} €</div></div>
      <div class="card"><b>Solde</b><div>{{ dash.profile.solde }} €</div></div>
      <div class="card">
        <b>Capacité épargne</b>
        <div :class="{ bad: Number(dash.totals.capacite_epargne) <= 0 }">
          {{ dash.totals.capacite_epargne }} €
        </div>
      </div>
    </div>

    <!-- Graph 1 : NORMAL + ABONNEMENTS empilés par catégorie -->
    <div class="card big" v-if="dash">
      <h3>Graph dépenses (variables + abonnements) par catégorie</h3>

      <div v-if="dash.by_category?.length">
        <canvas ref="chartCategoryEl"></canvas>
      </div>

      <p v-else class="muted">Aucune donnée sur ce mois.</p>
    </div>

    <!-- Graph 2 : camembert (répartition mensuelle) -->
    <div class="card big" v-if="dash">
      <h3>Répartition mensuelle</h3>

      <div class="grid2">
        <div>
          <canvas ref="chartBreakdownEl"></canvas>
        </div>

        <div class="kpis">
          <div class="kpi">
            <span>Dépenses fixes</span>
            <b>{{ dash.profile.depenses_fixes }} €</b>
          </div>
          <div class="kpi">
            <span>Dépenses variables</span>
            <b>{{ dash.totals.depenses_variables }} €</b>
          </div>
          <div class="kpi">
            <span>Abonnements</span>
            <b>{{ dash.totals.abonnements }} €</b>
          </div>
          <div class="kpi">
            <span>Épargne estimée</span>
            <b>{{ dash.totals.capacite_epargne }} €</b>
          </div>
        </div>
      </div>

      <p v-if="Number(dash.totals.capacite_epargne) < 0" class="muted" style="margin-top:10px">
        ⚠️ Épargne négative : le camembert affiche l’épargne à 0 (sinon Chart.js bug avec les valeurs négatives).
      </p>
    </div>

    <!-- Top 5 dépenses -->
    <div class="card big" v-if="dash">
      <h3>Top 5 dépenses</h3>

      <div v-if="dash.top_expenses?.length" class="tableWrap">
        <table class="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Catégorie</th>
              <th>Description</th>
              <th class="right">Montant (€)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in dash.top_expenses" :key="e.id">
              <td>{{ e.date }}</td>
              <td>{{ e.category }}</td>
              <td class="desc">{{ e.description || "—" }}</td>
              <td class="right"><b>{{ e.amount }}</b></td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-else class="muted">Aucune dépense variable ce mois.</p>
    </div>

    <!-- ML -->
    <div class="card big" v-if="dash">
      <div class="row">
        <h3>Prédiction ML</h3>
        <button class="btn" @click="predict" :disabled="finance.loading">
          {{ finance.loading ? "..." : "Prédire" }}
        </button>
      </div>

      <p v-if="finance.mlPrediction !== null" class="ok">
        Dépense mensuelle prédite : <b>{{ finance.mlPrediction }} €</b>
      </p>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { Chart } from "chart.js/auto";
import AppLayout from "../components/AppLayout.vue";
import { useFinanceStore } from "../stores/finance";

const finance = useFinanceStore();
const dash = computed(() => finance.dashboard);

const chartCategoryEl = ref(null);
const chartBreakdownEl = ref(null);

let chartCategory = null;
let chartBreakdown = null;

function errText(e){
  if(!e) return "";
  if(typeof e === "string") return e;
  return Object.entries(e)
    .map(([k,v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
    .join(" | ");
}

async function load(){
  await finance.fetchDashboard();
  await nextTick();
  renderCharts();
}

// ✅ CHARGEMENT AUTOMATIQUE AU MONTAGE
onMounted(() => {
  load();
});

function renderCharts(){
  renderCategoryChart();
  renderBreakdownChart();
}

function renderCategoryChart(){
  if(!chartCategoryEl.value || !dash.value?.by_category?.length) return;

  const labels = dash.value.by_category.map(x => x.category);
  const normal = dash.value.by_category.map(x => Number(x.normal_total || 0));
  const abonnements = dash.value.by_category.map(x => Number(x.abonnement_total || 0));

  if(chartCategory) chartCategory.destroy();

  chartCategory = new Chart(chartCategoryEl.value, {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "Variables (NORMAL)", data: normal },
        { label: "Abonnements", data: abonnements },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: true } },
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true },
      },
    },
  });
}

function renderBreakdownChart(){
  if(!chartBreakdownEl.value || !dash.value) return;

  const fixes = Number(dash.value.profile?.depenses_fixes || 0);
  const variables = Number(dash.value.totals?.depenses_variables || 0);
  const abonnements = Number(dash.value.totals?.abonnements || 0);
  const epargne = Number(dash.value.totals?.capacite_epargne || 0);

  const safeEpargne = Math.max(0, epargne);

  const labels = ["Fixes", "Variables", "Abonnements", "Épargne"];
  const data = [fixes, variables, abonnements, safeEpargne];

  if(chartBreakdown) chartBreakdown.destroy();

  chartBreakdown = new Chart(chartBreakdownEl.value, {
    type: "doughnut",
    data: { labels, datasets: [{ label: "Répartition (€)", data }] },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.label}: ${ctx.raw} €`,
          },
        },
      },
    },
  });
}

async function predict(){
  await finance.predictML();
}

onBeforeUnmount(()=>{
  if(chartCategory) chartCategory.destroy();
  if(chartBreakdown) chartBreakdown.destroy();
});
</script>

<style scoped>
h2,
h3 {
  color: #ffffff;
  margin: 0;
}

.btn {
  margin: 10px 0;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid #dcdcdc;
  background: #ffffff;
  color: #1f1f1f;
  cursor: pointer;
  font-weight: 600;
}

.btn:hover {
  background: #f5f5f5;
}

.err {
  color: #ff6b6b;
  margin-top: 10px;
}

.ok {
  color: #22c55e;
  margin-top: 10px;
}

.cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 18px 0;
}

.card {
  border: 1px solid #e8e8e8;
  border-radius: 18px;
  padding: 18px;
  background: #ffffff;
  color: #1f1f1f;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card b,
.card div,
.card span,
.card p,
.card td,
.card th,
.card h3 {
  color: #1f1f1f;
}

.big {
  margin-top: 18px;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.muted {
  opacity: 0.75;
  color: #666 !important;
}

.bad {
  color: #b00020 !important;
  font-weight: 700;
}

.cards .card {
  min-height: 110px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.cards .card b {
  display: block;
  font-size: 0.95rem;
  margin-bottom: 8px;
  color: #666;
}

.cards .card div {
  font-size: 1.6rem;
  font-weight: 700;
  color: #111;
}

.grid2 {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
  align-items: center;
}

.kpis {
  display: grid;
  gap: 12px;
}

.kpi {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #ededed;
  border-radius: 12px;
  padding: 12px 14px;
  background: #fafafa;
  color: #1f1f1f;
}

.kpi span {
  color: #666;
}

.kpi b {
  color: #111;
}

.tableWrap {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  color: #1f1f1f;
}

.table th,
.table td {
  padding: 12px 10px;
  border-bottom: 1px solid #eeeeee;
  text-align: left;
  color: #1f1f1f;
}

.table th {
  color: #666;
  font-weight: 600;
}

.table .right {
  text-align: right;
}

.desc {
  max-width: 420px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

canvas {
  max-width: 100%;
}

@media (max-width: 1100px) {
  .cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .grid2 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .cards {
    grid-template-columns: 1fr;
  }

  .row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>