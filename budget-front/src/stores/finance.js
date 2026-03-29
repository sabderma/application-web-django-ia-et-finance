import { defineStore } from "pinia";
import { http } from "../api/http";
import { endpoints } from "../api/endpoints";

export const useFinanceStore = defineStore("finance", {
  state: () => ({
    loading: false,
    error: null,

    dashboard: null,
    mlPrediction: null,

    categories: [],
    expenses: [],
    recurring: [],

    simulateResult: null,
    simulations: [],

    // ✅ IA Advice
    adviceText: "",
    adviceLoading: false,
  }),

  actions: {
    // ==============================
    // DASHBOARD
    // ==============================
    async fetchDashboard(month = null) {
      this.loading = true;
      this.error = null;
      try {
        const params = month ? { month } : undefined;
        const { data } = await http.get(endpoints.dashboard, { params });
        this.dashboard = data;
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur dashboard";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async predictML() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await http.post(endpoints.mlPredict, {});
        this.mlPrediction = data.depense_mensuelle_predite;
        return this.mlPrediction;
      } catch (e) {
        this.error = e?.response?.data || "Erreur ML";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    // ==============================
    // CATEGORIES
    // ==============================
    async fetchCategories({ activeOnly = true, type = null } = {}) {
      this.loading = true;
      this.error = null;
      try {
        const params = {};
        if (type) params.type = type;

        const { data } = await http.get(endpoints.categories, { params });
        this.categories = data;
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur categories";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async createCategory(payload) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await http.post(endpoints.categories, payload);
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur création catégorie";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async updateCategory(id, payload) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await http.patch(endpoints.categoryDetail(id), payload);
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur modification catégorie";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async deleteCategory(id) {
      this.loading = true;
      this.error = null;
      try {
        await http.delete(endpoints.categoryDetail(id));

        await Promise.all([
          // ✅ petit bug chez toi : tu faisais fetchCategories(true) alors que ça attend un objet
          this.fetchCategories({ activeOnly: true }),
          this.fetchExpenses(),
          this.fetchRecurring(),
        ]);
      } catch (e) {
        this.error = e?.response?.data || "Erreur suppression catégorie";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    // ==============================
    // EXPENSES
    // ==============================
    async fetchExpenses() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await http.get(endpoints.expenses);
        this.expenses = data;
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur expenses";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async createExpense(payload) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await http.post(endpoints.expenses, payload);
        await this.fetchExpenses();
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur création dépense";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async updateExpense(id, payload) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await http.patch(endpoints.expenseDetail(id), payload);
        await this.fetchExpenses();
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur modification dépense";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async deleteExpense(id) {
      this.loading = true;
      this.error = null;
      try {
        await http.delete(endpoints.expenseDetail(id));
        await this.fetchExpenses();
      } catch (e) {
        this.error = e?.response?.data || "Erreur suppression dépense";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    // ==============================
    // RECURRING EXPENSES
    // ==============================
    async fetchRecurring() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await http.get(endpoints.recurring);
        this.recurring = data;
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur recurring";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async createRecurring(payload) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await http.post(endpoints.recurring, payload);
        await this.fetchRecurring();
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur création abonnement";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async updateRecurring(id, payload) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await http.patch(endpoints.recurringDetail(id), payload);
        await this.fetchRecurring();
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur modification abonnement";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async deleteRecurring(id) {
      this.loading = true;
      this.error = null;
      try {
        await http.delete(endpoints.recurringDetail(id));
        await this.fetchRecurring();
      } catch (e) {
        this.error = e?.response?.data || "Erreur suppression abonnement";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    // ==============================
    // SIMULATION ACHAT
    // ==============================
    async simulatePurchase(payload) {
      this.loading = true;
      this.error = null;
      try {
        // ✅ reset advice à chaque nouvelle simulation
        this.adviceText = "";

        const { data } = await http.post(endpoints.simulate, payload);
        this.simulateResult = data;

        await this.fetchSimulations();
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur simulation";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async fetchSimulations() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await http.get(endpoints.simulations);
        this.simulations = data;
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur historique";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    async deleteSimulation(id) {
      this.loading = true;
      this.error = null;
      try {
        await http.delete(endpoints.simulationDetail(id));
        await this.fetchSimulations();
      } catch (e) {
        this.error = e?.response?.data || "Erreur suppression simulation";
        throw e;
      } finally {
        this.loading = false;
      }
    },

    // ==============================
    // ✅ IA ADVICE
    // ==============================
    async fetchAdvice(simulationId) {
      this.adviceLoading = true;
      this.error = null;

      try {
        const { data } = await http.post(endpoints.advice, {
          simulation_id: simulationId,
        });

        this.adviceText = data?.advice_text || "Aucun conseil reçu.";
        return this.adviceText;
      } catch (e) {
        this.error = e?.response?.data || "Erreur conseils IA";
        throw e;
      } finally {
        this.adviceLoading = false;
      }
    },
  },
});