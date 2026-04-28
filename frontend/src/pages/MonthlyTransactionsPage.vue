<template>
  <Panel title="月度流水总览" kicker="Monthly Review" description="适合每月几百条流水的聚合查看" fill>
    <template #actions>
      <button class="ghost-button" type="button" @click="loadMonthlyData">刷新</button>
    </template>

    <p v-if="error" class="notice error">{{ error }}</p>

    <div class="month-list">
      <section v-for="month in monthGroups" :key="month.key" class="month-section">
        <div class="month-head">
          <div>
            <strong>{{ month.label }}</strong>
            <span>{{ month.items.length }} 条流水</span>
          </div>
          <div class="month-totals">
            <span class="income">收入 {{ formatAmount(month.income) }}</span>
            <span class="expense">支出 {{ formatAmount(month.expense) }}</span>
            <span>净额 {{ formatAmount(month.net) }}</span>
          </div>
        </div>

        <div class="month-table">
          <div class="month-table-row month-table-head">
            <span>时间</span>
            <span>名称</span>
            <span>分类</span>
            <span>账户</span>
            <span>金额</span>
          </div>
          <div v-for="item in month.items" :key="item.id" class="month-table-row">
            <span>{{ formatShortDate(item.occurred_at) }}</span>
            <strong>{{ item.title }}</strong>
            <span>{{ categoryName(item.category_id) }}</span>
            <span>{{ accountSummary(item) }}</span>
            <strong :class="['month-amount', item.transaction_type]">
              {{ amountPrefix(item.transaction_type) }}{{ formatAmount(item.amount) }}
            </strong>
          </div>
        </div>
      </section>

      <p v-if="!monthGroups.length && !error" class="empty-state">暂无流水，月度总览会在有记录后自动生成。</p>
    </div>
  </Panel>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import Panel from "../components/Panel.vue";
import { api } from "../api/client";

const transactions = ref([]);
const accounts = ref([]);
const categories = ref([]);
const error = ref("");

const monthGroups = computed(() => {
  const grouped = transactions.value.reduce((result, item) => {
    const date = new Date(item.occurred_at);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
    if (!result[key]) {
      result[key] = {
        key,
        label: `${date.getFullYear()} 年 ${date.getMonth() + 1} 月`,
        items: [],
        income: 0,
        expense: 0,
        net: 0,
      };
    }

    const amount = Number(item.amount || 0);
    result[key].items.push(item);
    if (item.transaction_type === "income") {
      result[key].income += amount;
      result[key].net += amount;
    } else if (item.transaction_type === "expense") {
      result[key].expense += amount;
      result[key].net -= amount;
    }
    return result;
  }, {});

  return Object.values(grouped).sort((left, right) => right.key.localeCompare(left.key));
});

async function loadMonthlyData() {
  try {
    error.value = "";
    const [transactionRows, accountRows, categoryRows] = await Promise.all([
      api.listTransactions({ sort_by: "occurred_at", sort_order: "desc" }),
      api.listAccounts(),
      api.listCategories(),
    ]);
    transactions.value = transactionRows;
    accounts.value = accountRows;
    categories.value = categoryRows;
  } catch (err) {
    error.value = `加载月度流水失败：${err.message}`;
  }
}

function formatAmount(value) {
  return `¥${Number(value || 0).toFixed(2)}`;
}

function formatShortDate(value) {
  return new Intl.DateTimeFormat("zh-CN", {
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function amountPrefix(type) {
  if (type === "income") {
    return "+";
  }
  if (type === "expense") {
    return "-";
  }
  return "";
}

function accountName(id) {
  const account = accounts.value.find((item) => item.id === id);
  return account ? account.name : `#${id}`;
}

function categoryName(id) {
  const category = categories.value.find((item) => item.id === id);
  return category ? category.name : `分类 #${id}`;
}

function accountSummary(item) {
  if (item.transaction_type === "transfer") {
    return `${accountName(item.from_account_id)} → ${accountName(item.to_account_id)}`;
  }
  if (item.from_account_id) {
    return accountName(item.from_account_id);
  }
  if (item.to_account_id) {
    return accountName(item.to_account_id);
  }
  return "-";
}

onMounted(() => {
  loadMonthlyData();
  window.addEventListener("transactions-updated", loadMonthlyData);
  window.addEventListener("accounts-updated", loadMonthlyData);
  window.addEventListener("categories-updated", loadMonthlyData);
});

onUnmounted(() => {
  window.removeEventListener("transactions-updated", loadMonthlyData);
  window.removeEventListener("accounts-updated", loadMonthlyData);
  window.removeEventListener("categories-updated", loadMonthlyData);
});
</script>
