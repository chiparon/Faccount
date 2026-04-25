const API_BASE_URL = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const text = await response.text();
    try {
      const payload = JSON.parse(text);
      throw new Error(payload.detail || text || "request failed");
    } catch (error) {
      if (error instanceof SyntaxError) {
        throw new Error(text || "request failed");
      }
      throw error;
    }
  }

  return response.json();
}

export const api = {
  listAccounts() {
    return request("/accounts");
  },
  createAccount(payload) {
    return request("/accounts", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  listCategories() {
    return request("/categories");
  },
  createCategory(payload) {
    return request("/categories", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  listTransactions() {
    return request("/transactions");
  },
  createTransaction(payload) {
    return request("/transactions", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
