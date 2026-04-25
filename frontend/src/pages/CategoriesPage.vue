<template>
  <Panel title="分类管理" description="支持父子级分类。">
    <form class="stack" @submit.prevent="submitCategory">
      <input v-model.trim="form.name" placeholder="分类名称，如 食物开销" />
      <select v-model="form.kind">
        <option value="income">收入</option>
        <option value="expense">支出</option>
        <option value="transfer">转账</option>
      </select>
      <select v-model="form.parent_id">
        <option :value="null">无父分类</option>
        <option v-for="item in parentOptions" :key="item.id" :value="item.id">
          #{{ item.id }} {{ item.name }} / {{ kindLabel(item.kind) }}
        </option>
      </select>
      <button type="submit" :disabled="loading">{{ loading ? "提交中..." : "新增分类" }}</button>
    </form>

    <p v-if="message" class="notice success">{{ message }}</p>
    <p v-if="error" class="notice error">{{ error }}</p>

    <ul class="list">
      <li v-for="item in categories" :key="item.id">
        <strong>{{ item.name }}</strong>
        <span>{{ item.kind }}</span>
        <span v-if="item.parent_id">父级 #{{ item.parent_id }}</span>
      </li>
    </ul>
  </Panel>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import Panel from "../components/Panel.vue";
import { api } from "../api/client";

const categories = ref([]);
const error = ref("");
const loading = ref(false);
const message = ref("");
const form = reactive({
  name: "",
  kind: "expense",
  parent_id: null,
  is_active: true,
  sort_order: 0,
});

const parentOptions = computed(() =>
  categories.value.filter((item) => item.kind === form.kind),
);

function kindLabel(kind) {
  return {
    income: "收入",
    expense: "支出",
    transfer: "转账",
  }[kind] || kind;
}

async function loadCategories() {
  try {
    error.value = "";
    categories.value = await api.listCategories();
  } catch (err) {
    error.value = `加载分类失败：${err.message}`;
  }
}

async function submitCategory() {
  if (!form.name) {
    error.value = "请填写分类名称";
    return;
  }

  const payload = {
    ...form,
    parent_id: form.parent_id || null,
  };

  try {
    loading.value = true;
    error.value = "";
    message.value = "";
    await api.createCategory(payload);
    form.name = "";
    form.kind = "expense";
    form.parent_id = null;
    message.value = "分类已新增";
    await loadCategories();
    window.dispatchEvent(new CustomEvent("categories-updated"));
  } catch (err) {
    error.value = `新增分类失败：${err.message}`;
  } finally {
    loading.value = false;
  }
}

onMounted(loadCategories);
</script>
