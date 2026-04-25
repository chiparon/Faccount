<template>
  <Panel title="账户管理" description="新增和查看资金账户。">
    <form class="stack" @submit.prevent="submitAccount">
      <input v-model.trim="form.name" placeholder="账户名称，如 微信零钱" />
      <input v-model.trim="form.type" placeholder="账户类型，如 e-wallet / bank" />
      <button type="submit" :disabled="loading">{{ loading ? "提交中..." : "新增账户" }}</button>
    </form>

    <p v-if="message" class="notice success">{{ message }}</p>
    <p v-if="error" class="notice error">{{ error }}</p>

    <ul class="list">
      <li v-for="item in accounts" :key="item.id">
        <strong>{{ item.name }}</strong>
        <span>{{ item.type }}</span>
      </li>
    </ul>
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

onMounted(loadAccounts);
</script>
