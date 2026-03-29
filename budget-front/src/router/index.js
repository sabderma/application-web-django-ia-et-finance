import { createRouter, createWebHistory } from "vue-router";

import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";

import DashboardView from "../views/DashboardView.vue";
import ProfileView from "../views/ProfileView.vue";
import CategoriesView from "../views/CategoriesView.vue";
import ExpensesView from "../views/ExpensesView.vue";
import RecurringView from "../views/RecurringView.vue";
import SimulationView from "../views/SimulationView.vue";

function isAuthed() {
  return !!localStorage.getItem("access");
}

const routes = [
  { path: "/login", component: LoginView },
  { path: "/register", component: RegisterView },

  { path: "/", component: DashboardView, meta: { auth: true } },
  { path: "/profile", component: ProfileView, meta: { auth: true } },
  { path: "/categories", component: CategoriesView, meta: { auth: true } },
  { path: "/expenses", component: ExpensesView, meta: { auth: true } },
  { path: "/recurring", component: RecurringView, meta: { auth: true } },
  { path: "/simulation", component: SimulationView, meta: { auth: true } },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach((to) => {
  if (to.meta.auth && !isAuthed()) return "/login";
});

export default router;
