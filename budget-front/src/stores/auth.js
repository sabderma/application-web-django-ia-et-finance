import { defineStore } from "pinia";
import { http } from "../api/http";
import { endpoints } from "../api/endpoints";

export const useAuthStore = defineStore("auth", {
  state: () => ({ loading: false, error: null }),
  actions: {
    async register(payload) {
      this.loading = true; this.error = null;
      try {
        const { data } = await http.post(endpoints.register, payload);
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur inscription";
        throw e;
      } finally { this.loading = false; }
    },

    async login({ username, password }) {
      this.loading = true; this.error = null;
      try {
        const { data } = await http.post(endpoints.login, { username, password });
        localStorage.setItem("access", data.access);
        localStorage.setItem("refresh", data.refresh);
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur login";
        throw e;
      } finally { this.loading = false; }
    },

    logout() {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
    },
  },
});
