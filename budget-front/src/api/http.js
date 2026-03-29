import axios from "axios";

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

http.interceptors.request.use((config) => {
  const access = localStorage.getItem("access");
  if (access) config.headers.Authorization = `Bearer ${access}`;
  return config;
});

// ---------------------------
// REFRESH AUTO SI TOKEN EXPIRE
// ---------------------------
let isRefreshing = false;
let queue = [];

function runQueue(newAccess) {
  queue.forEach((cb) => cb(newAccess));
  queue = [];
}

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error?.response?.status;
    const code = error?.response?.data?.code; // "token_not_valid" souvent
    const originalRequest = error.config;

    // Evite boucle infinie
    if (!originalRequest) return Promise.reject(error);

    // On ne refresh pas sur l'endpoint refresh lui-même
    const isRefreshCall = originalRequest.url?.includes("/api/token/refresh");

    if (status === 401 && code === "token_not_valid" && !originalRequest._retry && !isRefreshCall) {
      originalRequest._retry = true;

      const refresh = localStorage.getItem("refresh");
      if (!refresh) {
        // plus de refresh => logout
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        window.location.href = "/login";
        return Promise.reject(error);
      }

      // Si un refresh est déjà en cours, on met en queue
      if (isRefreshing) {
        return new Promise((resolve) => {
          queue.push((newAccess) => {
            originalRequest.headers.Authorization = `Bearer ${newAccess}`;
            resolve(http(originalRequest));
          });
        });
      }

      isRefreshing = true;
      try {
        // IMPORTANT: utilise la MEME baseURL que ton http
        const r = await http.post("/api/token/refresh/", { refresh });

        const newAccess = r.data.access;
        localStorage.setItem("access", newAccess);

        runQueue(newAccess);

        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return http(originalRequest);
      } catch (e) {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        window.location.href = "/login";
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);