<template>
  <Panel
    :title="editingId ? '编辑流水' : '记一笔'"
    kicker="Transaction Editor"
    description="录入或修改收入、支出和转账流水，支持拆分子元素"
  >
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
        <span>名称</span>
        <input v-model.trim="form.title" placeholder="如 超市采购" />
      </label>

      <label class="field amount-field">
        <span>金额</span>
        <input v-model.number="form.amount" type="number" min="0.01" step="0.01" placeholder="0.00" />
      </label>

      <label class="field">
        <span>时间</span>
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
        <span>来源逻辑</span>
        <input v-model.trim="form.source_logic" placeholder="如 4月生活费 / 比赛奖金 / 微信导入待确认" />
      </label>

      <label class="field span-2">
        <span>备注</span>
        <textarea v-model.trim="form.note" rows="3" placeholder="可选，记录更多细节"></textarea>
      </label>

      <div class="span-2 subitem-editor">
        <div class="subitem-head">
          <div>
            <strong>流水子元素</strong>
            <span>用于拆分一笔超市、网购或导入账单中的细目</span>
          </div>
          <button class="ghost-button" type="button" @click="addItem">新增子项</button>
        </div>

        <div v-for="(item, index) in form.items" :key="index" class="subitem-row">
          <input v-model.trim="item.title" placeholder="子项名称，如 水果" />
          <input v-model.number="item.amount" type="number" min="0.01" step="0.01" placeholder="金额" />
          <select v-model="item.category_id">
            <option :value="null">可选分类</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
          <input v-model.trim="item.note" placeholder="备注" />
          <button class="danger-link" type="button" @click="removeItem(index)">删除</button>
        </div>
      </div>

      <div class="span-2 form-actions">
        <button class="submit-button" type="submit" :disabled="loading">
          {{ loading ? "保存中..." : editingId ? "保存修改" : "提交流水" }}
        </button>
        <button v-if="editingId" class="ghost-button" type="button" @click="resetForm">取消编辑</button>
      </div>
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

const emptyForm = () => ({
  title: "",
  transaction_type: "expense",
  occurred_at: toLocalInputValue(new Date()),
  amount: null,
  category_id: null,
  from_account_id: null,
  to_account_id: null,
  note: "",
  source_logic: "",
  items: [],
});

const form = reactive(emptyForm());
const accounts = ref([]);
const categories = ref([]);
const editingId = ref(null);
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

function assignForm(values) {
  const next = {
    ...emptyForm(),
    ...values,
    occurred_at: values.occurred_at ? toLocalInputValue(new Date(values.occurred_at)) : toLocalInputValue(new Date()),
    note: values.note || "",
    source_logic: values.source_logic || "",
    items: (values.items || []).map((item) => ({
      title: item.title,
      amount: Number(item.amount),
      category_id: item.category_id || null,
      note: item.note || "",
    })),
  };
  Object.assign(form, next);
}

function resetForm() {
  editingId.value = null;
  Object.assign(form, emptyForm());
}

function addItem() {
  form.items.push({
    title: "",
    amount: null,
    category_id: form.category_id,
    note: "",
  });
}

function removeItem(index) {
  form.items.splice(index, 1);
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
    return "请填写名称、时间、金额和分类";
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
  const invalidItem = form.items.find((item) => !item.title || !item.amount);
  if (invalidItem) {
    return "请补全子元素的名称和金额，或删除空子项";
  }
  return "";
}

function buildPayload() {
  return {
    ...form,
    occurred_at: new Date(form.occurred_at).toISOString(),
    from_account_id: form.from_account_id || null,
    to_account_id: form.to_account_id || null,
    note: form.note || null,
    source_logic: form.source_logic || null,
    items: form.items.map((item) => ({
      title: item.title,
      amount: item.amount,
      category_id: item.category_id || null,
      note: item.note || null,
    })),
  };
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
    if (editingId.value) {
      await api.updateTransaction(editingId.value, buildPayload());
      message.value = "流水已更新";
    } else {
      await api.createTransaction(buildPayload());
      message.value = "流水已提交";
    }
    resetForm();
    window.dispatchEvent(new CustomEvent("transactions-updated"));
  } catch (err) {
    error.value = `保存流水失败：${err.message}`;
  } finally {
    loading.value = false;
  }
}

function startEditing(event) {
  editingId.value = event.detail.id;
  assignForm(event.detail);
  message.value = "已载入流水，可在下方修改后保存";
  error.value = "";
  window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
}

onMounted(() => {
  loadOptions();
  window.addEventListener("accounts-updated", loadOptions);
  window.addEventListener("categories-updated", loadOptions);
  window.addEventListener("transaction-edit-requested", startEditing);
});

onUnmounted(() => {
  window.removeEventListener("accounts-updated", loadOptions);
  window.removeEventListener("categories-updated", loadOptions);
  window.removeEventListener("transaction-edit-requested", startEditing);
});
</script>
