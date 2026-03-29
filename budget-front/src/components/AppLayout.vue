<template>
  <div class="layout">
    <aside class="side">
      <h3 class="logo">Budget AI</h3>

      <nav class="nav">
        <router-link to="/">Dashboard</router-link>
        <router-link to="/profile">Profil</router-link>
        <router-link to="/categories">Catégories</router-link>
        <router-link to="/expenses">Dépenses</router-link>
        <router-link to="/recurring">Abonnements</router-link>
        <router-link to="/simulation">Simulation achat</router-link>
      </nav>

      <button class="logout" @click="logout">Déconnexion</button>
    </aside>

    <main class="main">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();

function logout() {
  auth.logout();
  router.push("/login");
}
</script>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  background: #111111;
}

/* SIDEBAR */
.side {
  border-right: 1px solid #1f1f1f;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  background: #161616;
}

/* LOGO */
.logo {
  margin: 0;
  color: #ffffff;
  font-size: 1.4rem;
  font-weight: 700;
}

/* NAV */
.nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav a {
  padding: 12px 14px;
  border-radius: 12px;
  text-decoration: none;
  border: 1px solid transparent;
  color: #cccccc;
  background: #1d1d1d;
  transition: 0.2s ease;
  font-weight: 500;
}

.nav a:hover {
  background: #262626;
  color: #ffffff;
}

/* ACTIVE LINK */
.nav a.router-link-active {
  background: #6c63ff;
  color: #ffffff;
  border-color: transparent;
}

/* LOGOUT BUTTON */
.logout {
  margin-top: auto;
  padding: 12px;
  border-radius: 12px;
  border: none;
  background: #ff4d4f;
  color: white;
  cursor: pointer;
  font-weight: 600;
  transition: 0.2s ease;
}

.logout:hover {
  background: #ff6b6b;
}

/* MAIN CONTENT */
.main {
  padding: 28px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

/* RESPONSIVE */
@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .side {
    flex-direction: row;
    overflow-x: auto;
    border-right: none;
    border-bottom: 1px solid #1f1f1f;
  }

  .nav {
    flex-direction: row;
    flex-wrap: nowrap;
  }

  .nav a {
    white-space: nowrap;
  }

  .logout {
    margin-top: 0;
    margin-left: auto;
  }
}
</style>
