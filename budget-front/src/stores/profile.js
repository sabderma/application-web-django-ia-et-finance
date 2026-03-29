import { defineStore } from "pinia";
import { http } from "../api/http";
import { endpoints } from "../api/endpoints";

export const useProfileStore = defineStore("profile", {
  state: () => ({ loading: false, error: null, profile: null }),
  actions: {
    async fetchProfile() {
      this.loading = true; this.error = null;
      try {
        const { data } = await http.get(endpoints.financialProfileMe);
        this.profile = data;
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur profil (GET)";
        throw e;
      } finally { this.loading = false; }
    },

    async updateProfile(payload) {
      this.loading = true; this.error = null;
      try {
        // ✅ PATCH (tu as RetrieveUpdateAPIView)
        const { data } = await http.patch(endpoints.financialProfileMe, payload);
        this.profile = data;
        return data;
      } catch (e) {
        this.error = e?.response?.data || "Erreur profil (PATCH)";
        throw e;
      } finally { this.loading = false; }
    },
  },
});

