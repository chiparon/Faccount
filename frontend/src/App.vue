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
            围绕账户、分类、流水三类核心数据，先完成一个稳定可用的个人账本闭环。重新设计的现代化界面，让数据关系更清晰。
          </p>
        </div>

        <div class="tech-card">
          <span>技术栈 Tech Stack</span>
          <strong>Vue 3 + Vite</strong>
          <small>配合 FastAPI 与 MySQL 8</small>
        </div>
      </header>

      <main class="dashboard-grid">
        <section class="main-column">
          <TransactionsPage />
          <MonthlyTransactionsPage />
          <TransactionEntryPage />
        </section>

        <aside class="side-column">
          <AccountsPage />
          <CategoriesPage />
        </aside>
      </main>
    </div>
  </div>
</template>

<script setup>
import AccountsPage from "./pages/AccountsPage.vue";
import CategoriesPage from "./pages/CategoriesPage.vue";
import MonthlyTransactionsPage from "./pages/MonthlyTransactionsPage.vue";
import TransactionEntryPage from "./pages/TransactionEntryPage.vue";
import TransactionsPage from "./pages/TransactionsPage.vue";
</script>
