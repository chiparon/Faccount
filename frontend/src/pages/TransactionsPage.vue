<template>
  <Panel title="流水列表" description="按时间倒序展示当前流水。">
    <button class="secondary" type="button" @click="loadTransactions">刷新列表</button>

    <p v-if="error" class="notice error">{{ error }}</p>

    <ul class="list">
      <li v-for="item in transactions" :key="item.id">
        <div class="row">
          <strong>{{ item.title }}</strong>
          <span>{{ item.transaction_type }}</span>
        </div>
        <div class="row muted">
          <span>金额：{{ item.amount }}</span>
          <span>分类：#{{ item.category_id }}</span>
          <span v-if="item.from_account_id">出：#{{ item.from_account_id }}</span>
          <span v-if="item.to_account_id">入：#{{ item.to_account_id }}</span>
        </div>
      </li>
    </ul>
  </Panel>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import Panel from "../components/Panel.vue";
import { api } from "../api/client";

const transactions = ref([]);
const error = ref("");

async function loadTransactions() {
  try {
    error.value = "";
    transactions.value = await api.listTransactions();
  } catch (err) {
    error.value = `加载流水失败：${err.message}`;
  }
}

onMounted(() => {
  loadTransactions();
  window.addEventListener("transactions-updated", loadTransactions);
});

onUnmounted(() => {
  window.removeEventListener("transactions-updated", loadTransactions);
});
</script>
