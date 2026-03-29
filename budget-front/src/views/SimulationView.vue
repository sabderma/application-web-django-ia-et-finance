<template>
  <AppLayout>
    <h2>Simulation achat</h2>

    <p v-if="finance.error" class="err">{{ errText(finance.error) }}</p>

    <form class="form" @submit.prevent="simulate">
      <input v-model.trim="item_name" placeholder="Produit" required />
      <input
        v-model.number="price"
        type="number"
        min="1"
        placeholder="Prix (€)"
        required
      />

      <select v-model="priority">
        <option value="NEED">NEED</option>
        <option value="WANT">WANT</option>
        <option value="LUXURY">LUXURY</option>
      </select>

      <input
        v-model.number="monthly_saving_target"
        type="number"
        min="0"
        placeholder="Épargne mensuelle (optionnel)"
      />

      <button class="btn" :disabled="finance.loading">
        {{ finance.loading ? "..." : "Simuler" }}
      </button>
    </form>

    <!-- ✅ Résultat -->
    <div class="card" v-if="finance.simulateResult">
      <h3>Résultat</h3>

      <p><b>Decision:</b> {{ finance.simulateResult.decision }}</p>
      <p><b>Estimated months:</b> {{ finance.simulateResult.estimated_months }}</p>
      <p>
        <b>Recommended saving:</b>
        {{ finance.simulateResult.recommended_monthly_saving }} €
      </p>

      <!-- ✅ Bouton IA -->
      <button class="btn" @click="getAdvice" :disabled="loadingAdvice">
        {{ loadingAdvice ? "Chargement..." : "💡 Suggestions IA" }}
      </button>

      <!-- ✅ Affichage conseils -->
      <div v-if="adviceText" class="advice">
        <h4>Conseils IA</h4>
        <pre>{{ adviceText }}</pre>
      </div>

      <details>
        <summary>Détails</summary>
        <pre>{{ finance.simulateResult.details }}</pre>
      </details>
    </div>

    <!-- ✅ Historique -->
    <div class="card">
      <div class="row">
        <h3>Historique</h3>
      </div>

      <p v-if="finance.loading" style="opacity: 0.7">Chargement...</p>

      <div v-if="finance.simulations?.length" class="list">
        <div class="item" v-for="s in finance.simulations" :key="s.id">
          <div>
            <b>{{ s.item_name }}</b> — {{ s.price }} € — {{ s.decision }}
            <div style="opacity: 0.7">{{ s.created_at }}</div>
          </div>

          <button class="btn" @click="del(s.id)" :disabled="finance.loading">
            Supprimer
          </button>
        </div>
      </div>

      <p v-else style="opacity: 0.7">Aucune simulation.</p>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from "vue";
import AppLayout from "../components/AppLayout.vue";
import { useFinanceStore } from "../stores/finance";

const finance = useFinanceStore();

const item_name = ref("");
const price = ref(0);
const priority = ref("WANT");
const monthly_saving_target = ref("");

const adviceText = ref("");
const loadingAdvice = ref(false);

function errText(e) {
  if (!e) return "";
  if (typeof e === "string") return e;
  return Object.entries(e)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
    .join(" | ");
}

async function simulate() {
  adviceText.value = ""; // reset conseils à chaque nouvelle simulation

  const payload = {
    item_name: item_name.value,
    price: price.value,
    priority: priority.value,
  };

  if (monthly_saving_target.value !== "" && monthly_saving_target.value !== null) {
    payload.monthly_saving_target = Number(monthly_saving_target.value);
  }

  await finance.simulatePurchase(payload);

  // recharger l’historique après simulation
  await loadHistory();
}

async function getAdvice() {
  if (!finance.simulateResult?.id) return;

  loadingAdvice.value = true;
  adviceText.value = "";

  try {
    const token = localStorage.getItem("access");
    if (!token) {
      adviceText.value = "Token manquant : reconnecte-toi.";
      loadingAdvice.value = false;
      return;
    }

    const res = await fetch("http://127.0.0.1:8000/api/advice/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + token,
      },
      body: JSON.stringify({
        simulation_id: finance.simulateResult.id,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      adviceText.value = data?.detail || data?.error || "Erreur API IA.";
    } else {
      adviceText.value = data?.advice_text || "Aucun conseil reçu.";
    }
  } catch (e) {
    const data = e.response?.data;
    console.log(data);
    err.value = data?.error ? `${data.detail} : ${data.error}` : (data?.detail || "Erreur inconnue");
  } finally {
    loadingAdvice.value = false;
  }
}

async function loadHistory() {
  await finance.fetchSimulations();
}

onMounted(() => {
  loadHistory();
});

async function del(id) {
  await finance.deleteSimulation(id);
  await loadHistory();
}
</script>

<style scoped>
h2,
h3 {
  color: #ffffff;
  margin-bottom: 12px;
}

.btn {
  margin: 0;
  padding: 11px 14px;
  border-radius: 12px;
  border: 1px solid #dddddd;
  background: #ffffff;
  color: #1f1f1f;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
  background: #f7f7f7;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.err {
  color: #ff6b6b;
  margin-top: 10px;
}

.form {
  max-width: 620px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 14px;
  margin-bottom: 20px;
  padding: 18px;
  border-radius: 18px;
  background: #ffffff;
  color: #1f1f1f;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
}

input,
select {
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid #dddddd;
  background: #ffffff;
  color: #1f1f1f;
  outline: none;
  font-size: 0.98rem;
}

input::placeholder {
  color: #888888;
}

input:focus,
select:focus {
  border-color: #6c63ff;
}

.card {
  border-radius: 16px;
  padding: 16px;
  margin-top: 14px;
  background: #ffffff;
  color: #1f1f1f;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
}

.card b,
.card div,
.card span,
.card p,
.card h3,
.card h4,
.card label {
  color: #1f1f1f;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  border-radius: 14px;
  padding: 14px;
  background: #fafafa;
  color: #1f1f1f;
  border: 1px solid #eeeeee;
}

.item b,
.item div,
.item span,
.item p {
  color: #1f1f1f;
}

pre {
  background: #f7f7f7;
  color: #1f1f1f;
  padding: 12px;
  border-radius: 12px;
  overflow: auto;
  border: 1px solid #ececec;
  white-space: pre-wrap;
  word-break: break-word;
}

/* zone conseils IA */
.advice {
  margin-top: 14px;
  background: #f0f9ff;
  color: #1f1f1f;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid #cce7ff;
}

.advice b,
.advice p,
.advice span,
.advice li {
  color: #1f1f1f;
}

@media (max-width: 700px) {
  .row {
    flex-direction: column;
    align-items: stretch;
  }

  .item {
    flex-direction: column;
    align-items: flex-start;
  }

  .btn {
    width: 100%;
  }
}
</style>