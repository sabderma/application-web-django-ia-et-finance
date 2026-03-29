export const endpoints = {
  register: "/api/auth/register/",
  login: "/api/auth/login/",
  refresh: "/api/auth/refresh/",

  // ✅ Financial profile
  financialProfileMe: "/api/financial-profile/me/",

  // ✅ Categories
  categories: "/api/categories/",
  categoryDetail: (id) => `/api/categories/${id}/`,
  categoriesAll: "/api/categories/all/",


  // ✅ Expenses
  expenses: "/api/expenses/",
  expenseDetail: (id) => `/api/expenses/${id}/`,

  // ✅ Recurring
  recurring: "/api/recurring-expenses/",
  recurringDetail: (id) => `/api/recurring-expenses/${id}/`,

  // ✅ Dashboard
  dashboard: "/api/dashboard/",

  // ✅ Simulation achat
  simulate: "/api/simulate/",
  simulations: "/api/simulations/",
  simulationDetail: (id) => `/api/simulations/${id}/`,

  // ✅ ML
  mlPredict: "/api/ml/predict/",

  advice: "/api/advice/",
};
