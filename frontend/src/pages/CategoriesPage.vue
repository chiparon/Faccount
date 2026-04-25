<template>
  <Panel title="分类管理" kicker="Categories" description="支持父子级分类" fill>
    <div class="category-scroll">
      <article v-for="item in rootCategories" :key="item.id" class="category-node">
        <div class="category-row">
          <span class="category-dot" :class="item.kind"></span>
          <strong>{{ item.name }}</strong>
          <em>{{ kindLabel(item.kind) }}</em>
          <button class="danger-link" type="button" @click="deleteCategory(item)">删除</button>
        </div>
        <div v-if="childrenMap[item.id]?.length" class="category-children">
          <div v-for="child in childrenMap[item.id]" :key="child.id" class="category-row child">
            <span class="category-dot" :class="child.kind"></span>
            <span>{{ child.name }}</span>
            <em>{{ kindLabel(child.kind) }}</em>
            <button class="danger-link" type="button" @click="deleteCategory(child)">删除</button>
          </div>
        </div>
      </article>
      <p v-if="!categories.length && !error" class="empty-state">暂无分类，请新增收入或支出分类。</p>
    </div>

    <form class="stack compact-form divider-top" @submit.prevent="submitCategory">
      <label>
        <span>分类名称</span>
        <input v-model.trim="form.name" placeholder="如 餐饮美食" />
      </label>
      <label>
        <span>分类类型</span>
        <select v-model="form.kind">
          <option value="income">收入</option>
          <option value="expense">支出</option>
          <option value="transfer">转账</option>
        </select>
      </label>
      <label>
        <span>父分类</span>
        <select v-model="form.parent_id">
          <option :value="null">无父分类</option>
          <option v-for="item in parentOptions" :key="item.id" :value="item.id">
            {{ item.name }} / {{ kindLabel(item.kind) }}
          </option>
        </select>
      </label>
      <button type="submit" :disabled="loading">{{ loading ? "提交中..." : "新增分类" }}</button>
    </form>

    <p v-if="message" class="notice success">{{ message }}</p>
    <p v-if="error" class="notice error">{{ error }}</p>
  </Panel>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
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
  categories.value.filter((item) => item.kind === form.kind && !item.parent_id),
);

const rootCategories = computed(() => categories.value.filter((item) => !item.parent_id));

const childrenMap = computed(() =>
  categories.value.reduce((result, item) => {
    if (item.parent_id) {
      result[item.parent_id] = result[item.parent_id] || [];
      result[item.parent_id].push(item);
    }
    return result;
  }, {}),
);

watch(
  () => form.kind,
  () => {
    form.parent_id = null;
  },
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

  try {
    loading.value = true;
    error.value = "";
    message.value = "";
    await api.createCategory({
      ...form,
      parent_id: form.parent_id || null,
    });
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

async function deleteCategory(item) {
  if (!window.confirm(`确认删除分类「${item.name}」吗？存在子分类或已被流水使用时不能删除。`)) {
    return;
  }

  try {
    error.value = "";
    message.value = "";
    await api.deleteCategory(item.id);
    message.value = "分类已删除";
    await loadCategories();
    window.dispatchEvent(new CustomEvent("categories-updated"));
  } catch (err) {
    error.value = `删除分类失败：${err.message}`;
  }
}
</script>
