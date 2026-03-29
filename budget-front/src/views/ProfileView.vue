<template>
  <AppLayout>
    <h2>Profil financier</h2>

    <p v-if="store.loading" class="note">Chargement...</p>
    <p v-if="store.error" class="err">{{ errText(store.error) }}</p>

    <form class="form" @submit.prevent="onSubmit">
      <!-- ÂGE -->
      <div class="field">
        <label class="label">Âge</label>
        <input
          v-model.number="form.age"
          :disabled="!isEditing"
          type="number"
          min="16"
          max="100"
          placeholder="Ex: 22"
          required
        />
      </div>

      <!-- STATUT -->
      <div class="field">
        <label class="label">Statut</label>
        <select v-model="form.statut" :disabled="!isEditing" required>
          <option value="ETUDIANT">Étudiant</option>
          <option value="SALARIE">Salarié</option>
          <option value="RETRAITE">Retraité</option>
        </select>
      </div>

      <!-- SALAIRE -->
      <div class="field">
        <label class="label">Salaire mensuel (€)</label>
        <input
          v-model.number="form.salaire_mensuel"
          :disabled="!isEditing"
          type="number"
          min="0"
          placeholder="Ex: 1600"
        />
      </div>

      <!-- SOLDE -->
      <div class="field">
        <label class="label">Solde (€)</label>
        <input
          v-model.number="form.solde"
          :disabled="!isEditing"
          type="number"
          placeholder="Ex: 500"
        />
      </div>

      <!-- DEPENSES FIXES -->
      <div class="field">
        <label class="label">Dépenses fixes (€)</label>
        <input
          v-model.number="form.depenses_fixes"
          :disabled="!isEditing"
          type="number"
          min="0"
          placeholder="Ex: 800"
        />
      </div>

      <!-- OBJECTIF EPARGNE -->
      <div class="field">
        <label class="label">Objectif d’épargne (€)</label>
        <input
          v-model.number="form.objectif_epargne"
          :disabled="!isEditing"
          type="number"
          min="0"
          placeholder="Ex: 200"
        />
      </div>

      <!-- ACTIONS (EN BAS) -->
      <div class="actions">
        <button
          v-if="!isEditing"
          type="button"
          class="btn primary"
          @click="startEdit"
          :disabled="store.loading"
        >
          Modifier
        </button>

        <template v-else>
          <button class="btn primary" type="submit" :disabled="store.loading">
            {{ store.loading ? "..." : "Enregistrer" }}
          </button>
          <button class="btn" type="button" @click="cancelEdit" :disabled="store.loading">
            Annuler
          </button>
        </template>
      </div>
    </form>

    <p class="note">
      Endpoint utilisé : <b>GET/PATCH /api/financial-profile/me/</b>
      (créé automatiquement si absent)
    </p>
  </AppLayout>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import AppLayout from "../components/AppLayout.vue";
import { useProfileStore } from "../stores/profile";

const store = useProfileStore();

const isEditing = ref(false);

const form = reactive({
  age: 18,
  statut: "ETUDIANT",
  salaire_mensuel: 0,
  solde: 0,
  depenses_fixes: 0,
  objectif_epargne: null,
});

// pour annuler et revenir aux valeurs chargées
const snapshot = ref(null);

function errText(e) {
  if (!e) return "";
  if (typeof e === "string") return e;
  return Object.entries(e)
    .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
    .join(" | ");
}

async function load() {
  const p = await store.fetchProfile();
  if (p) Object.assign(form, p);
  snapshot.value = JSON.parse(JSON.stringify(form));
}

onMounted(load);

function startEdit() {
  isEditing.value = true;
  snapshot.value = JSON.parse(JSON.stringify(form));
}

function cancelEdit() {
  if (snapshot.value) Object.assign(form, snapshot.value);
  isEditing.value = false;
}

async function onSubmit() {
  if (!isEditing.value) return;

  await store.updateProfile({
    age: form.age,
    statut: form.statut,
    salaire_mensuel: form.salaire_mensuel,
    solde: form.solde,
    depenses_fixes: form.depenses_fixes,
    objectif_epargne: form.objectif_epargne,
  });

  // si pas d'erreur, on repasse en mode lecture
  if (!store.error) {
    isEditing.value = false;
    snapshot.value = JSON.parse(JSON.stringify(form));
  }
}
</script>

<style scoped>
h2 {
  color: #ffffff;
  margin-bottom: 12px;
}

.form {
  max-width: 640px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 14px;
  padding: 22px;
  border-radius: 20px;
  background: #ffffff;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.14);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label {
  font-weight: 700;
  font-size: 0.95rem;
  color: #222222;
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
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input::placeholder {
  color: #8a8a8a;
}

input:focus,
select:focus {
  border-color: #6c63ff;
  box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.12);
}

input:disabled,
select:disabled {
  background: #f5f5f5;
  color: #666666;
  cursor: not-allowed;
  border-color: #e6e6e6;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 11px 16px;
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
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn.primary {
  background: #6c63ff;
  color: #ffffff;
  border: none;
}

.btn.primary:hover {
  background: #7d75ff;
}

.err {
  color: #ff6b6b;
  margin-top: 10px;
}

.note {
  margin-top: 14px;
  color: #b5b5b5;
  opacity: 1;
}

.note b {
  color: #ffffff;
}

@media (max-width: 640px) {
  .form {
    padding: 16px;
  }

  .actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>