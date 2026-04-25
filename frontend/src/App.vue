<template>
  <div class="shell">
    <header class="hero">
      <div>
        <p class="eyebrow">Accounts App V1</p>
        <h1>个人账目记录应用</h1>
        <p class="lead">
          围绕账户、分类、流水三类核心数据，先完成一个稳定可用的个人账本闭环。
        </p>
      </div>
      <div class="hero-card">
        <span>技术栈</span>
        <strong>Vue 3 + Vite</strong>
        <small>配合 FastAPI 与 MySQL 8</small>
      </div>
    </header>

    <main class="grid">
      <AccountsPage />
      <CategoriesPage />
      <TransactionEntryPage />
      <TransactionsPage />
    </main>
  </div>
</template>

<script setup>
import AccountsPage from "./pages/AccountsPage.vue";
import CategoriesPage from "./pages/CategoriesPage.vue";
import TransactionEntryPage from "./pages/TransactionEntryPage.vue";
import TransactionsPage from "./pages/TransactionsPage.vue";
</script>

