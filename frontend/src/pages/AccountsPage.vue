<template>
  <Panel title="账户管理" kicker="Accounts" description="新增、查看和移入 Trash 资金账户">
    <div class="account-list">
      <article v-for="item in accounts" :key="item.id" class="account-card">
        <div class="account-avatar">{{ item.name.slice(0, 1) }}</div>
        <div>
          <strong>{{ item.name }}</strong>
          <span>{{ item.type }}</span>
        </div>
        <button class="danger-link" type="button" @click="deleteAccount(item)">删除</button>
      </article>
      <p v-if="!accounts.length && !error" class="empty-state">暂无账户，请先新增一个资金账户。</p>
    </div>

    <form class="stack compact-form divider-top" @submit.prevent="submitAccount">
      <label>
        <span>账户名称</span>
        <input v-model.trim="form.name" placeholder="如 微信零钱" />
      </label>
      <label>
        <span>账户类型</span>
        <input v-model.trim="form.type" placeholder="如 e-wallet / bank" />
      </label>
      <button type="submit" :disabled="loading">{{ loading ? "提交中..." : "新增账户" }}</button>
    </form>

    <p v-if="message" class="notice success">{{ message }}</p>
    <p v-if="error" class="notice error">{{ error }}</p>
  </Panel>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import Panel from "../components/Panel.vue";
import { api } from "../api/client";

const accounts = ref([]);
const error = ref("");
const loading = ref(false);
const message = ref("");
const form = reactive({
  name: "",
  type: "",
});

async function loadAccounts() {
  try {
    error.value = "";
    accounts.value = await api.listAccounts();
  } catch (err) {
    error.value = `加载账户失败：${err.message}`;
  }
}

async function submitAccount() {
  if (!form.name || !form.type) {
    error.value = "请填写账户名称和账户类型";
    return;
  }

  try {
    loading.value = true;
    error.value = "";
    message.value = "";
    await api.createAccount({ ...form });
    form.name = "";
    form.type = "";
    message.value = "账户已新增";
    await loadAccounts();
    window.dispatchEvent(new CustomEvent("accounts-updated"));
  } catch (err) {
    error.value = `新增账户失败：${err.message}`;
  } finally {
    loading.value = false;
  }
}

async function deleteAccount(item) {
  if (!window.confirm(`确认删除账户「${item.name}」吗？删除后会进入 Trash，可恢复。`)) {
    return;
  }

  try {
    error.value = "";
    message.value = "";
    await api.deleteAccount(item.id);
    message.value = "账户已移入 Trash";
    await loadAccounts();
    window.dispatchEvent(new CustomEvent("accounts-updated"));
  } catch (err) {
    error.value = `删除账户失败：${err.message}`;
  }
}

onMounted(loadAccounts);
</script>
