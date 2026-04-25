<template>
  <Panel title="记一笔" description="录入收入、支出和转账流水。">
    <form class="stack" @submit.prevent="submitTransaction">
      <input v-model.trim="form.title" placeholder="标题" />
      <select v-model="form.transaction_type">
        <option value="income">收入</option>
        <option value="expense">支出</option>
        <option value="transfer">转账</option>
      </select>
      <input v-model="form.occurred_at" type="datetime-local" />
      <input v-model.number="form.amount" type="number" min="0.01" step="0.01" placeholder="金额" />
      <select v-model="form.category_id">
        <option :value="null">选择分类</option>
        <option v-for="item in categoryOptions" :key="item.id" :value="item.id">
          #{{ item.id }} {{ item.name }}
        </option>
      </select>
      <select v-model="form.from_account_id" :disabled="form.transaction_type === 'income'">
        <option :value="null">选择来源账户</option>
        <option v-for="item in accounts" :key="item.id" :value="item.id">
          #{{ item.id }} {{ item.name }} / {{ item.type }}
        </option>
      </select>
      <select v-model="form.to_account_id" :disabled="form.transaction_type === 'expense'">
        <option :value="null">选择目标账户</option>
        <option v-for="item in accounts" :key="item.id" :value="item.id">
          #{{ item.id }} {{ item.name }} / {{ item.type }}
        </option>
      </select>
      <textarea v-model.trim="form.note" rows="3" placeholder="备注"></textarea>
      <button type="submit" :disabled="loading">{{ loading ? "提交中..." : "提交流水" }}</button>
    </form>

    <p v-if="message" class="notice success">{{ message }}</p>
    <p v-if="error" class="notice error">{{ error }}</p>
  </Panel>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue";
import Panel from "../components/Panel.vue";
import { api } from "../api/client";

const form = reactive({
  title: "",
  transaction_type: "expense",
  occurred_at: "",
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

watch(
  () => form.transaction_type,
  () => {
    form.category_id = null;
    if (form.transaction_type === "income") {
      form.from_account_id = null;
    }
    if (form.transaction_type === "expense") {
      form.to_account_id = null;
    }
  },
);

async function submitTransaction() {
  if (!form.title || !form.occurred_at || !form.amount || !form.category_id) {
    error.value = "请填写标题、时间、金额和分类 ID";
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
    form.occurred_at = "";
    form.amount = null;
    form.category_id = null;
    form.from_account_id = null;
    form.to_account_id = null;
    form.note = "";
    message.value = "流水已提交，请刷新流水列表查看";
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
