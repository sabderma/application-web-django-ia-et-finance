<template>
  <AppLayout>
    <h2>Abonnements (Recurring)</h2>

    <!-- ❌ supprimé : bouton Charger -->
    <p v-if="finance.loading" style="opacity:.7">Chargement...</p>

    <p v-if="finance.error" class="err">{{ errText(finance.error) }}</p>

    <form class="form" @submit.prevent="add">
      <!-- ✅ Sélection catégorie abonnement -->
      <select v-model="form.category" required>
        <option disabled value="">Choisir une catégorie</option>
        <option v-for="c in finance.categories" :key="c.id" :value="c.id">
          {{ c.name }}
        </option>
      </select>

      <input v-model.trim="form.name" placeholder="Nom (ex: Netflix)" required />
      <input v-model.number="form.amount" type="number" min="0" placeholder="Montant" required />
      <input v-model="form.start_date" type="date" required />
      <input v-model="form.end_date" type="date" placeholder="Fin (optionnel)" />

      <label class="chk">
        <input type="checkbox" v-model="form.active" />
        Actif
      </label>

      <button class="btn" :disabled="finance.loading">Ajouter</button>
    </form>

    <div class="list" v-if="finance.recurring?.length">
      <div class="item" v-for="r in finance.recurring" :key="r.id">
        <div>
          <b>{{ r.name }}</b> — {{ r.amount }} €
          <div style="opacity:.7">
            Catégorie: {{ r.category_name }} |
            du {{ r.start_date }} au {{ r.end_date || "∞" }} |
            active: {{ r.active }}
          </div>
        </div>
        <div class="actions">
          <button class="btn" @click="toggle(r)" :disabled="finance.loading">
            {{ r.active ? "Désactiver" : "Activer" }}
          </button>
          <button class="btn" @click="del(r.id)" :disabled="finance.loading">
            Supprimer
          </button>
        </div>
      </div>
    </div>

    <p v-else style="opacity:.7">Aucun abonnement.</p>
  </AppLayout>
</template>

<script setup>
import { reactive, onMounted } from "vue";
import AppLayout from "../components/AppLayout.vue";
import { useFinanceStore } from "../stores/finance";

const finance = useFinanceStore();

const form = reactive({
  category: "",
  name: "",
  amount: 0,
  start_date: new Date().toISOString().slice(0, 10),
  end_date: "",
  active: true,
});

function errText(e) {
  if (!e) return "";
  if (typeof e === "string") return e;
  return Object.entries(e)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
    .join(" | ");
}

async function init() {
  // ✅ Charger uniquement les catégories abonnement
  await finance.fetchCategories({ type: "SUBSCRIPTION" });
  await finance.fetchRecurring();
}

// ✅ Chargement automatique à l’ouverture de la page
onMounted(() => {
  init();
});

async function add() {
  const payload = { ...form };
  if (!payload.end_date) delete payload.end_date;

  await finance.createRecurring(payload);

  form.category = "";
  form.name = "";
  form.amount = 0;
  form.end_date = "";
}

async function toggle(r) {
  await finance.updateRecurring(r.id, { ...r, active: !r.active });
}

async function del(id) {
  await finance.deleteRecurring(id);
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

.chk {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #1f1f1f;
  font-weight: 500;
}

.chk input {
  width: auto;
  margin: 0;
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
  border-radius: 16px;
  padding: 16px;
  gap: 14px;
  background: #ffffff;
  color: #1f1f1f;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
}

.item b,
.item div,
.item span,
.item p {
  color: #1f1f1f;
}

.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

@media (max-width: 700px) {
  .item {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  .btn {
    width: 100%;
  }
}
</style>