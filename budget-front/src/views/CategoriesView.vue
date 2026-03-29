<template>
  <AppLayout>
    <h2>Catégories</h2>

    <!-- BARRE TOP -->
    <div class="bar">
      <input v-model.trim="name" class="input" placeholder="Nom catégorie (ex: Loyer)" />

      <!-- TYPE -->
      <select v-model="type" class="input small">
        <option value="NORMAL">Normale</option>
        <option value="SUBSCRIPTION">Abonnement</option>
      </select>

      <button class="btn primary" @click="add" :disabled="finance.loading || !name">
        Ajouter
      </button>
    </div>

    <!-- FILTER TYPE -->
    <div class="filter-type">
      <button
        class="chip"
        :class="{ on: filterType === 'NORMAL' }"
        @click="setFilterType('NORMAL')"
      >
        Normales
      </button>
      <button
        class="chip"
        :class="{ on: filterType === 'SUBSCRIPTION' }"
        @click="setFilterType('SUBSCRIPTION')"
      >
        Abonnements
      </button>
    </div>

    <p v-if="finance.loading" class="muted">Chargement...</p>
    <p v-if="finance.error" class="err">{{ errText(finance.error) }}</p>

    <div class="list" v-if="filtered.length">
      <div class="item" v-for="c in filtered" :key="c.id">
        <div>
          <b>{{ c.name }}</b>
          <div class="muted">
            Type: {{ c.type }}
          </div>
        </div>

        <div class="actions">
          <button class="btn danger" @click="remove(c)" :disabled="finance.loading">
            Supprimer
          </button>
        </div>
      </div>
    </div>

    <p v-else class="muted" style="margin-top:14px;">
      Aucune catégorie.
    </p>
  </AppLayout>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import AppLayout from "../components/AppLayout.vue";
import { useFinanceStore } from "../stores/finance";

const finance = useFinanceStore();

const name = ref("");
const type = ref("NORMAL");
const filterType = ref("NORMAL");

function errText(e) {
  if (!e) return "";
  if (typeof e === "string") return e;
  return Object.entries(e)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
    .join(" | ");
}

async function load() {
  // ton API filtre déjà par type si tu envoies { type: ... }
  await finance.fetchCategories({ type: filterType.value });
}

onMounted(() => {
  load();
});

function setFilterType(t) {
  filterType.value = t;
  load();
}

const filtered = computed(() => {
  const list = finance.categories || [];
  // sécurité si le backend renvoie plus large
  return list.filter((c) => c.type === filterType.value);
});

async function add() {
  await finance.createCategory({
    name: name.value,
    type: type.value,
  });

  name.value = "";
  await load();
}

async function remove(c) {
  if (!confirm(`Supprimer définitivement "${c.name}" ?`)) return;
  await finance.deleteCategory(c.id);
  await load();
}
</script>

<style scoped>
h2 {
  color: #ffffff;
  margin-bottom: 10px;
}

/* BAR */
.bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin: 16px 0;
}

/* INPUT */
.input {
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid #2a2a2a;
  background: #1a1a1a;
  color: #ffffff;
  min-width: 180px;
  outline: none;
}

.input::placeholder {
  color: #888;
}

.input:focus {
  border-color: #6c63ff;
}

.small {
  min-width: 140px;
}

/* BUTTON */
.btn {
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid #2a2a2a;
  background: #1a1a1a;
  color: #ffffff;
  cursor: pointer;
  font-weight: 500;
  transition: 0.2s;
}

.btn:hover {
  transform: translateY(-1px);
}

/* PRIMARY */
.primary {
  background: #6c63ff;
  border: none;
  color: white;
}

.primary:hover {
  background: #7d75ff;
}

/* DANGER */
.danger {
  background: #ff4d4f;
  border: none;
  color: white;
}

.danger:hover {
  background: #ff6b6b;
}

/* FILTER */
.filter-type {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.chip {
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid #2a2a2a;
  background: #1a1a1a;
  color: #ccc;
  cursor: pointer;
  transition: 0.2s;
}

.chip.on {
  background: #6c63ff;
  color: white;
  border-color: transparent;
}

/* LIST */
.list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ITEM */
.item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 16px;
  padding: 16px;
  gap: 10px;

  background: #ffffff;
  color: #1f1f1f;

  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

/* TEXTE DANS LES CARDS */
.item b {
  font-size: 1.1rem;
  color: #111;
}

.item .muted {
  color: #666;
}

/* ACTIONS */
.actions {
  display: flex;
  gap: 8px;
}

/* STATE */
.err {
  color: #ff6b6b;
  margin-top: 10px;
}

.muted {
  opacity: 0.7;
  color: #aaa;
}

/* RESPONSIVE */
@media (max-width: 600px) {
  .item {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    width: 100%;
    justify-content: flex-end;
  }
}

</style>