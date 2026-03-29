<template>
  <div class="box">
    <h2>Inscription</h2>

    <form @submit.prevent="submit">
      <input v-model.trim="username" placeholder="Username" required />
      <input v-model.trim="email" placeholder="Email (optionnel)" type="email" />
      <input v-model="password" placeholder="Mot de passe" type="password" required minlength="6" />
      <button :disabled="auth.loading">{{ auth.loading ? "..." : "Créer compte" }}</button>
    </form>

    <p v-if="auth.error" class="err">{{ formatErr(auth.error) }}</p>
    <p class="link">Déjà un compte ? <router-link to="/login">Connexion</router-link></p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();

const username = ref("");
const email = ref("");
const password = ref("");

function formatErr(e) {
  if (!e) return "";
  if (typeof e === "string") return e;
  return Object.entries(e).map(([k,v]) => `${k}: ${Array.isArray(v)?v.join(", "):v}`).join(" | ");
}

async function submit() {
  await auth.register({ username: username.value, email: email.value, password: password.value });
  router.push("/login");
}
</script>

<style scoped>
.box{max-width:420px;margin:40px auto;padding:16px;border:1px solid #ddd;border-radius:12px}
form{display:flex;flex-direction:column;gap:10px}
input,button{padding:10px;border-radius:10px;border:1px solid #ccc}
.err{color:#b00020;margin-top:10px}
.link{margin-top:12px}
</style>
