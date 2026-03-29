<template>
  <AppLayout>
    <h2>Dépenses</h2>

    <!-- ✅ plus de bouton "Charger" -->

    <p v-if="finance.loading" style="opacity:.7">Chargement...</p>
    <p v-if="finance.error" class="err">{{ errText(finance.error) }}</p>

    <form class="form" @submit.prevent="add">
      <select v-model="form.category" required>
        <option disabled value="">Choisir catégorie</option>
        <option v-for="c in finance.categories" :key="c.id" :value="c.id">
          {{ c.name }}
        </option>
      </select>

      <input v-model.number="form.amount" type="number" min="0" placeholder="Montant" required />
      <input v-model="form.date" type="date" required />
      <input v-model.trim="form.description" placeholder="Description (optionnel)" />

      <button class="btn" :disabled="finance.loading">Ajouter</button>
    </form>

    <div class="list" v-if="finance.expenses?.length">
      <div class="item" v-for="e in finance.expenses" :key="e.id">
        <div>
          <b>{{ e.amount }} €</b> — {{ e.date }}
          <div style="opacity:.7">{{ e.description || "-" }}</div>
        </div>
        <button class="btn" @click="del(e.id)" :disabled="finance.loading">Supprimer</button>
      </div>
    </div>

    <p v-else style="opacity:.7">Aucune dépense.</p>
  </AppLayout>
</template>

<script setup>
import { reactive, onMounted } from "vue";
import AppLayout from "../components/AppLayout.vue";
import { useFinanceStore } from "../stores/finance";

const finance = useFinanceStore();

const form = reactive({
  category: "",
  amount: 0,
  date: new Date().toISOString().slice(0, 10),
  description: "",
});

function errText(e) {
  if (!e) return "";
  if (typeof e === "string") return e;
  return Object.entries(e)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
    .join(" | ");
}

async function init() {
  await finance.fetchCategories({ type: "NORMAL" });
  await finance.fetchExpenses();
}

// ✅ Chargement automatique au montage de la page
onMounted(() => {
  init();
});

async function add() {
  await finance.createExpense({ ...form });
  form.amount = 0;
  form.description = "";
}

async function del(id) {
  await finance.deleteExpense(id);
}
</script>

<style scoped>
h2 {
  color: #ffffff;
  margin-bottom: 12px;
}

.btn {
  margin: 0;
  padding: 11px 14px;
  border-radius: 12px;
  border: none;
  background: #6c63ff;
  color: #ffffff;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s ease;
}

.btn:hover {
  background: #7d75ff;
  transform: translateY(-1px);
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

.list {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  border-radius: 16px;
  padding: 16px;
  background: #ffffff;
  color: #1f1f1f;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
}

.item b {
  color: #111111;
  font-size: 1.05rem;
}

.item div {
  color: #1f1f1f;
}

.item div div {
  color: #666666 !important;
  margin-top: 4px;
}

p[style*="opacity"] {
  color: #aaaaaa !important;
}

@media (max-width: 700px) {
  .item {
    flex-direction: column;
    align-items: flex-start;
  }

  .item .btn {
    width: 100%;
  }
}
</style>  