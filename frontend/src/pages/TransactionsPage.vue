<template>
  <div :class="{ 'transactions-expanded': expanded }">
    <Panel title="流水列表" kicker="Recent Activity" description="支持搜索、复杂筛选、排序、编辑与删除" fill>
      <template #actions>
        <button class="ghost-button" type="button" @click="expanded = !expanded">
          {{ expanded ? "恢复默认" : "全页查看" }}
        </button>
        <button class="ghost-button" type="button" @click="resetFilters">重置筛选</button>
      </template>

      <div class="quick-search">
        <input v-model.trim="filters.q" placeholder="搜索名称、备注、来源逻辑" @keyup.enter="loadAll" />
        <button class="filter-submit" type="button" @click="loadAll">搜索</button>
      </div>

      <form class="filter-bar" @submit.prevent="loadAll">
        <label>
          <span>开始时间</span>
          <input v-model="filters.start_at" type="datetime-local" />
        </label>
        <label>
          <span>结束时间</span>
          <input v-model="filters.end_at" type="datetime-local" />
        </label>
        <label>
          <span>金额下限</span>
          <input v-model.number="filters.amount_min" type="number" min="0" step="0.01" placeholder="不限" />
        </label>
        <label>
          <span>金额上限</span>
          <input v-model.number="filters.amount_max" type="number" min="0" step="0.01" placeholder="不限" />
        </label>
        <label>
          <span>类型</span>
          <select v-model="filters.transaction_type">
            <option value="">全部类型</option>
            <option value="income">收入</option>
            <option value="expense">支出</option>
            <option value="transfer">转账</option>
          </select>
        </label>
        <label>
          <span>分类属性</span>
          <select v-model="filters.category_id">
            <option value="">全部分类</option>
            <option v-for="item in categories" :key="item.id" :value="item.id">
              {{ categoryPath(item) }}
            </option>
          </select>
        </label>
        <label>
          <span>账户</span>
          <select v-model="filters.account_id">
            <option value="">全部账户</option>
            <option v-for="item in accounts" :key="item.id" :value="item.id">
              {{ item.name }} / {{ item.type }}
            </option>
          </select>
        </label>
        <label>
          <span>排序字段</span>
          <select v-model="filters.sort_by">
            <option value="occurred_at">按时间</option>
            <option value="amount">按金额</option>
            <option value="created_at">按创建时间</option>
            <option value="id">按编号</option>
          </select>
        </label>
        <label>
          <span>排序方向</span>
          <select v-model="filters.sort_order">
            <option value="desc">降序</option>
            <option value="asc">升序</option>
          </select>
        </label>
        <button class="filter-submit" type="submit">应用筛选</button>
      </form>

      <div class="summary-strip">
        <div>
          <span>匹配流水</span>
          <strong>{{ transactions.length }}</strong>
        </div>
        <div>
          <span>收入</span>
          <strong class="income">{{ formatAmount(incomeTotal) }}</strong>
        </div>
        <div>
          <span>支出</span>
          <strong class="expense">{{ formatAmount(expenseTotal) }}</strong>
        </div>
      </div>

      <p v-if="message" class="notice success">{{ message }}</p>
      <p v-if="error" class="notice error">{{ error }}</p>

      <div class="transaction-list dense">
        <article v-for="item in transactions" :key="item.id" class="transaction-card table-like">
          <div class="transaction-main">
            <div class="transaction-grid-row">
              <div class="transaction-name">
                <strong>{{ item.title }}</strong>
                <span v-if="item.source_logic">{{ item.source_logic }}</span>
              </div>
              <strong class="transaction-amount" :class="item.transaction_type">
                {{ amountPrefix(item.transaction_type) }}{{ formatAmount(item.amount) }}
              </strong>
              <span>{{ formatDate(item.occurred_at) }}</span>
              <span class="category-chip" :class="item.transaction_type">{{ categoryPathById(item.category_id) }}</span>
              <span>{{ accountSummary(item) }}</span>
              <div class="transaction-actions">
                <button class="ghost-button mini" type="button" @click="editTransaction(item)">编辑</button>
                <button class="danger-link" type="button" @click="deleteTransaction(item)">删除</button>
              </div>
            </div>
            <div v-if="item.items?.length" class="subitem-preview">
              <span v-for="child in item.items" :key="child.id">
                {{ child.title }} {{ formatAmount(child.amount) }}
              </span>
            </div>
            <p v-if="item.note" class="transaction-note">{{ item.note }}</p>
          </div>
        </article>
        <p v-if="!transactions.length && !error" class="empty-state">暂无匹配流水，可调整筛选条件或新增记录。</p>
      </div>
    </Panel>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from "vue";
import Panel from "../components/Panel.vue";
import { api } from "../api/client";

const transactions = ref([]);
const accounts = ref([]);
const categories = ref([]);
const error = ref("");
const message = ref("");
const expanded = ref(false);
const filters = reactive({
  q: "",
  start_at: "",
  end_at: "",
  amount_min: "",
  amount_max: "",
  transaction_type: "",
  category_id: "",
  account_id: "",
  sort_by: "occurred_at",
  sort_order: "desc",
});

const incomeTotal = computed(() => totalByType("income"));
const expenseTotal = computed(() => totalByType("expense"));

async function loadAll() {
  try {
    error.value = "";
    const [accountRows, categoryRows] = await Promise.all([
      api.listAccounts(),
      api.listCategories(),
    ]);
    accounts.value = accountRows;
    categories.value = categoryRows;
    transactions.value = await api.listTransactions(normalizedFilters());
  } catch (err) {
    error.value = `加载流水失败：${err.message}`;
  }
}

function normalizedFilters() {
  return {
    ...filters,
    start_at: filters.start_at ? new Date(filters.start_at).toISOString() : "",
    end_at: filters.end_at ? new Date(filters.end_at).toISOString() : "",
  };
}

function resetFilters() {
  Object.assign(filters, {
    q: "",
    start_at: "",
    end_at: "",
    amount_min: "",
    amount_max: "",
    transaction_type: "",
    category_id: "",
    account_id: "",
    sort_by: "occurred_at",
    sort_order: "desc",
  });
  message.value = "";
  loadAll();
}

function editTransaction(item) {
  window.dispatchEvent(new CustomEvent("transaction-edit-requested", { detail: item }));
}

async function deleteTransaction(item) {
  if (!window.confirm(`确认删除流水「${item.title}」吗？删除后会进入 Trash，可恢复。`)) {
    return;
  }

  try {
    error.value = "";
    message.value = "";
    await api.deleteTransaction(item.id);
    message.value = "流水已移入 Trash";
    await loadAll();
    window.dispatchEvent(new CustomEvent("transactions-updated"));
  } catch (err) {
    error.value = `删除流水失败：${err.message}`;
  }
}

function totalByType(type) {
  return transactions.value
    .filter((item) => item.transaction_type === type)
    .reduce((sum, item) => sum + Number(item.amount || 0), 0);
}

function formatAmount(value) {
  return `¥${Number(value || 0).toFixed(2)}`;
}

function formatDate(value) {
  if (!value) {
    return "未记录时间";
  }
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function typeLabel(type) {
  return {
    income: "收入",
    expense: "支出",
    transfer: "转账",
  }[type] || type;
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

function categoryPath(item) {
  const parent = item.parent_id ? categories.value.find((category) => category.id === item.parent_id) : null;
  return parent ? `${parent.name}-${item.name}` : `${item.name} / ${typeLabel(item.kind)}`;
}

function categoryPathById(id) {
  const category = categories.value.find((item) => item.id === id);
  return category ? categoryPath(category) : `分类 #${id}`;
}

onMounted(() => {
  loadAll();
  window.addEventListener("transactions-updated", loadAll);
  window.addEventListener("accounts-updated", loadAll);
  window.addEventListener("categories-updated", loadAll);
});

onUnmounted(() => {
  window.removeEventListener("transactions-updated", loadAll);
  window.removeEventListener("accounts-updated", loadAll);
  window.removeEventListener("categories-updated", loadAll);
});
</script>
