<template>
  <div class="app-shell">
    <div class="app-container">
      <header class="app-header">
        <div>
          <div class="brand-row">
            <div class="brand-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 7v10M15.5 9.5A3.5 3.5 0 0 0 12 8c-1.93 0-3.5.9-3.5 2s1.57 2 3.5 2 3.5.9 3.5 2-1.57 2-3.5 2a3.5 3.5 0 0 1-3.5-1.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8" />
              </svg>
            </div>
            <p class="eyebrow">Transactions</p>
          </div>
          <h1>个人账目记录应用</h1>
          <p class="lead">
            将流水查看、记账编辑、月度复盘、导入整理和恢复操作拆成独立视图，降低单屏信息压力。
          </p>
        </div>

        <div class="tech-card">
          <span>技术栈 Tech Stack</span>
          <strong>Vue 3 + Vite</strong>
          <small>配合 FastAPI 与 MySQL 8</small>
        </div>
      </header>

      <nav class="page-tabs" aria-label="功能分页">
        <button
          v-for="page in pages"
          :key="page.key"
          type="button"
          :class="{ active: activePage === page.key }"
          @click="activePage = page.key"
        >
          <span>{{ page.label }}</span>
        </button>
      </nav>

      <main class="page-shell">
        <section v-show="activePage === 'transactions'" class="page-panel">
          <TransactionsPage />
        </section>

        <section v-show="activePage === 'entry'" class="page-panel">
          <TransactionEntryPage />
        </section>

        <section v-show="activePage === 'monthly'" class="page-panel">
          <MonthlyTransactionsPage />
        </section>

        <section v-show="activePage === 'flow'" class="page-panel">
          <BudgetFlowPage />
        </section>

        <section v-show="activePage === 'import'" class="page-panel">
          <ImportCachePage />
        </section>

        <section v-show="activePage === 'trash'" class="page-panel">
          <TrashPage />
        </section>

        <section v-show="activePage === 'manage'" class="page-panel management-grid">
          <AccountsPage />
          <CategoriesPage />
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import AccountsPage from "./pages/AccountsPage.vue";
import BudgetFlowPage from "./pages/BudgetFlowPage.vue";
import CategoriesPage from "./pages/CategoriesPage.vue";
import ImportCachePage from "./pages/ImportCachePage.vue";
import MonthlyTransactionsPage from "./pages/MonthlyTransactionsPage.vue";
import TransactionEntryPage from "./pages/TransactionEntryPage.vue";
import TransactionsPage from "./pages/TransactionsPage.vue";
import TrashPage from "./pages/TrashPage.vue";

const pages = [
  { key: "transactions", label: "流水" },
  { key: "entry", label: "记一笔/编辑" },
  { key: "monthly", label: "月度总览" },
  { key: "flow", label: "预算流转" },
  { key: "import", label: "账单导入" },
  { key: "trash", label: "Trash" },
  { key: "manage", label: "基础管理" },
];

const activePage = ref("transactions");

function openEditorPage() {
  activePage.value = "entry";
}

onMounted(() => {
  window.addEventListener("transaction-edit-requested", openEditorPage);
});

onUnmounted(() => {
  window.removeEventListener("transaction-edit-requested", openEditorPage);
});
</script>
