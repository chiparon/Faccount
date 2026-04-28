<template>
  <Panel title="Trash 垃圾池" kicker="Recover" description="删除的账户、分类、流水会先进入这里，可恢复、永久删除或清空">
    <div class="quick-search trash-toolbar">
      <input v-model.trim="filters.q" placeholder="搜索 Trash 中的名称、类型、备注" @keyup.enter="loadTrash" />
      <select v-model="filters.entity_type">
        <option value="">全部</option>
        <option value="transaction">流水</option>
        <option value="category">分类</option>
        <option value="account">账户</option>
      </select>
      <button class="filter-submit" type="button" @click="loadTrash">搜索</button>
      <button class="danger-link clear-button" type="button" @click="clearCurrentTrash">清空当前范围</button>
    </div>

    <p class="trash-hint">
      永久删除会释放账户名/分类名的唯一占用。若账户或分类仍被流水引用，后端会跳过并提示原因。
    </p>

    <p v-if="message" class="notice success">{{ message }}</p>
    <p v-if="error" class="notice error">{{ error }}</p>

    <div class="trash-sections">
      <section class="trash-section">
        <h3>流水</h3>
        <article v-for="item in trash.transactions || []" :key="item.id" class="trash-card">
          <div>
            <strong>{{ item.title }}</strong>
            <span>{{ formatAmount(item.amount) }} / {{ formatDate(item.deleted_at) }}</span>
          </div>
          <div class="trash-card-actions">
            <button class="ghost-button mini" type="button" @click="restore('transaction', item.id)">恢复</button>
            <button class="danger-link" type="button" @click="permanentlyDelete('transaction', item.id, item.title)">
              永久删除
            </button>
          </div>
        </article>
        <p v-if="!(trash.transactions || []).length" class="empty-state">暂无已删除流水。</p>
      </section>

      <section class="trash-section">
        <h3>分类</h3>
        <article v-for="item in trash.categories || []" :key="item.id" class="trash-card">
          <div>
            <strong>{{ item.name }}</strong>
            <span>{{ item.kind }} / {{ formatDate(item.deleted_at) }}</span>
          </div>
          <div class="trash-card-actions">
            <button class="ghost-button mini" type="button" @click="restore('category', item.id)">恢复</button>
            <button class="danger-link" type="button" @click="permanentlyDelete('category', item.id, item.name)">
              永久删除
            </button>
          </div>
        </article>
        <p v-if="!(trash.categories || []).length" class="empty-state">暂无已删除分类。</p>
      </section>

      <section class="trash-section">
        <h3>账户</h3>
        <article v-for="item in trash.accounts || []" :key="item.id" class="trash-card">
          <div>
            <strong>{{ item.name }}</strong>
            <span>{{ item.type }} / {{ formatDate(item.deleted_at) }}</span>
          </div>
          <div class="trash-card-actions">
            <button class="ghost-button mini" type="button" @click="restore('account', item.id)">恢复</button>
            <button class="danger-link" type="button" @click="permanentlyDelete('account', item.id, item.name)">
              永久删除
            </button>
          </div>
        </article>
        <p v-if="!(trash.accounts || []).length" class="empty-state">暂无已删除账户。</p>
      </section>
    </div>
  </Panel>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import Panel from "../components/Panel.vue";
import { api } from "../api/client";

const trash = ref({});
const error = ref("");
const message = ref("");
const filters = reactive({
  q: "",
  entity_type: "",
});

async function loadTrash() {
  try {
    error.value = "";
    trash.value = await api.listTrash(filters);
  } catch (err) {
    error.value = `加载 Trash 失败：${err.message}`;
  }
}

async function restore(entityType, id) {
  try {
    error.value = "";
    message.value = "";
    await api.restoreTrash(entityType, id);
    message.value = "已恢复";
    await reloadAfterTrashMutation();
  } catch (err) {
    error.value = `恢复失败：${err.message}`;
  }
}

async function permanentlyDelete(entityType, id, name) {
  if (!window.confirm(`确认永久删除「${name}」吗？这个操作不可恢复。`)) {
    return;
  }

  try {
    error.value = "";
    message.value = "";
    await api.permanentlyDeleteTrash(entityType, id);
    message.value = "已永久删除";
    await reloadAfterTrashMutation();
  } catch (err) {
    error.value = `永久删除失败：${err.message}`;
  }
}

async function clearCurrentTrash() {
  const scopeText = filters.entity_type ? entityLabel(filters.entity_type) : "全部 Trash";
  if (!window.confirm(`确认清空「${scopeText}」吗？这个操作不可恢复。`)) {
    return;
  }

  try {
    error.value = "";
    message.value = "";
    const result = await api.clearTrash({ entity_type: filters.entity_type });
    const deleted = result.deleted || {};
    const skipped = result.skipped || [];
    message.value = `已清空：流水 ${deleted.transactions || 0} 条，分类 ${deleted.categories || 0} 个，账户 ${deleted.accounts || 0} 个。`;
    if (skipped.length) {
      error.value = `有 ${skipped.length} 条因仍被引用未删除：${skipped.map((item) => item.name).join("、")}`;
    }
    await reloadAfterTrashMutation(false);
  } catch (err) {
    error.value = `清空失败：${err.message}`;
  }
}

async function reloadAfterTrashMutation(resetMessage = true) {
  await loadTrash();
  if (resetMessage) {
    window.dispatchEvent(new CustomEvent("transactions-updated"));
    window.dispatchEvent(new CustomEvent("accounts-updated"));
    window.dispatchEvent(new CustomEvent("categories-updated"));
  } else {
    window.dispatchEvent(new CustomEvent("transactions-updated"));
    window.dispatchEvent(new CustomEvent("accounts-updated"));
    window.dispatchEvent(new CustomEvent("categories-updated"));
  }
}

function entityLabel(entityType) {
  return {
    transaction: "流水",
    category: "分类",
    account: "账户",
  }[entityType] || entityType;
}

function formatAmount(value) {
  return `¥${Number(value || 0).toFixed(2)}`;
}

function formatDate(value) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

onMounted(loadTrash);
</script>
