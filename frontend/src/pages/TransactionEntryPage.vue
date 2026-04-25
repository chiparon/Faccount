<template>
  <Panel title="记一笔" kicker="New Transaction" description="录入收入、支出和转账流水">
    <form class="transaction-form" @submit.prevent="submitTransaction">
      <div class="type-switch">
        <button
          v-for="item in transactionTypes"
          :key="item.value"
          type="button"
          :class="{ active: form.transaction_type === item.value }"
          @click="form.transaction_type = item.value"
        >
          {{ item.label }}
        </button>
      </div>

      <label class="field span-2">
        <span>标题</span>
        <input v-model.trim="form.title" placeholder="如 麦当劳早餐" />
      </label>

      <label class="field amount-field">
        <span>金额</span>
        <input v-model.number="form.amount" type="number" min="0.01" step="0.01" placeholder="0.00" />
      </label>

      <label class="field">
        <span>发生时间</span>
        <input v-model="form.occurred_at" type="datetime-local" />
      </label>

      <label class="field">
        <span>分类</span>
        <select v-model="form.category_id">
          <option :value="null">选择分类</option>
          <option v-for="item in categoryOptions" :key="item.id" :value="item.id">
            {{ item.name }} / {{ kindLabel(item.kind) }}
          </option>
        </select>
      </label>

      <label class="field" :class="{ disabled: form.transaction_type === 'income' }">
        <span>来源账户</span>
        <select v-model="form.from_account_id" :disabled="form.transaction_type === 'income'">
          <option :value="null">选择来源账户</option>
          <option v-for="item in accounts" :key="item.id" :value="item.id">
            {{ item.name }} / {{ item.type }}
          </option>
        </select>
      </label>

      <label class="field" :class="{ disabled: form.transaction_type === 'expense' }">
        <span>目标账户</span>
        <select v-model="form.to_account_id" :disabled="form.transaction_type === 'expense'">
          <option :value="null">选择目标账户</option>
          <option v-for="item in accounts" :key="item.id" :value="item.id">
            {{ item.name }} / {{ item.type }}
          </option>
        </select>
      </label>

      <label class="field span-2">
        <span>备注</span>
        <textarea v-model.trim="form.note" rows="3" placeholder="可选，记录更多细节"></textarea>
      </label>

      <button class="submit-button span-2" type="submit" :disabled="loading">
        {{ loading ? "提交中..." : "提交流水" }}
      </button>
    </form>

    <p v-if="message" class="notice success">{{ message }}</p>
    <p v-if="error" class="notice error">{{ error }}</p>
  </Panel>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue";
import Panel from "../components/Panel.vue";
import { api } from "../api/client";

const transactionTypes = [
  { value: "expense", label: "支出" },
  { value: "income", label: "收入" },
  { value: "transfer", label: "转账" },
];

const form = reactive({
  title: "",
  transaction_type: "expense",
  occurred_at: toLocalInputValue(new Date()),
  amount: null,
  category_id: null,
  from_account_id: null,
  to_account_id: null,
  note: "",
});
const accounts = ref([]);
const categories = ref([]);
const error = ref("");
const loading = ref(false);
const message = ref("");

const categoryOptions = computed(() =>
  categories.value.filter((item) => item.kind === form.transaction_type),
);

watch(
  () => form.transaction_type,
  (value) => {
    form.category_id = null;
    if (value === "income") {
      form.from_account_id = null;
    }
    if (value === "expense") {
      form.to_account_id = null;
    }
  },
);

function toLocalInputValue(date) {
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function kindLabel(kind) {
  return {
    income: "收入",
    expense: "支出",
    transfer: "转账",
  }[kind] || kind;
}

async function loadOptions() {
  try {
    error.value = "";
    const [accountRows, categoryRows] = await Promise.all([
      api.listAccounts(),
      api.listCategories(),
    ]);
    accounts.value = accountRows;
    categories.value = categoryRows;
  } catch (err) {
    error.value = `加载账户或分类失败：${err.message}`;
  }
}

function validateTransaction() {
  if (!form.title || !form.occurred_at || !form.amount || !form.category_id) {
    return "请填写标题、时间、金额和分类";
  }
  if (form.transaction_type === "expense" && !form.from_account_id) {
    return "支出流水需要选择来源账户";
  }
  if (form.transaction_type === "income" && !form.to_account_id) {
    return "收入流水需要选择目标账户";
  }
  if (form.transaction_type === "transfer") {
    if (!form.from_account_id || !form.to_account_id) {
      return "转账流水需要同时选择来源和目标账户";
    }
    if (form.from_account_id === form.to_account_id) {
      return "转账的来源账户和目标账户不能相同";
    }
  }
  return "";
}

async function submitTransaction() {
  const validationMessage = validateTransaction();
  if (validationMessage) {
    error.value = validationMessage;
    return;
  }

  try {
    loading.value = true;
    error.value = "";
    message.value = "";
    await api.createTransaction({
      ...form,
      occurred_at: new Date(form.occurred_at).toISOString(),
      from_account_id: form.from_account_id || null,
      to_account_id: form.to_account_id || null,
      note: form.note || null,
    });

    form.title = "";
    form.transaction_type = "expense";
    form.occurred_at = toLocalInputValue(new Date());
    form.amount = null;
    form.category_id = null;
    form.from_account_id = null;
    form.to_account_id = null;
    form.note = "";
    message.value = "流水已提交";
    window.dispatchEvent(new CustomEvent("transactions-updated"));
  } catch (err) {
    error.value = `提交流水失败：${err.message}`;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadOptions();
  window.addEventListener("accounts-updated", loadOptions);
  window.addEventListener("categories-updated", loadOptions);
});

onUnmounted(() => {
  window.removeEventListener("accounts-updated", loadOptions);
  window.removeEventListener("categories-updated", loadOptions);
});
</script>
