<template>
  <Panel title="预算流转" kicker="Flow Map" description="按来源逻辑聚合收入、账户流转、分类和流水明细">
    <template #actions>
      <button class="ghost-button" type="button" @click="loadData">刷新</button>
    </template>

    <p v-if="error" class="notice error">{{ error }}</p>

    <div class="flow-board">
      <section v-for="group in flowGroups" :key="group.name" class="flow-orbit">
        <div class="flow-core">
          <strong>{{ group.name }}</strong>
          <span>{{ formatAmount(group.total) }}</span>
        </div>

        <div class="flow-rings">
          <article v-for="category in group.categories" :key="category.name" class="flow-category">
            <div class="flow-category-ball">
              <strong>{{ category.name }}</strong>
              <span>{{ formatAmount(category.total) }}</span>
            </div>
            <div class="flow-stars">
              <span
                v-for="item in category.items"
                :key="item.id"
                class="flow-star"
                :title="`${item.title} ${formatAmount(item.amount)} / ${accountSummary(item)}`"
              >
                {{ item.transaction_type === "income" ? "入" : item.transaction_type === "transfer" ? "转" : "出" }}
              </span>
            </div>
          </article>
        </div>
      </section>

      <p v-if="!flowGroups.length && !error" class="empty-state">
        暂无可聚合的流水。可在创建或编辑流水时填写“来源逻辑”，例如“4月生活费”或“比赛奖金”。
      </p>
    </div>
  </Panel>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import Panel from "../components/Panel.vue";
import { api } from "../api/client";

const transactions = ref([]);
const accounts = ref([]);
const categories = ref([]);
const error = ref("");

const flowGroups = computed(() => {
  const groups = transactions.value.reduce((result, item) => {
    const groupName = item.source_logic || "未归集来源";
    const categoryName = categoryPathById(item.category_id);
    result[groupName] = result[groupName] || {
      name: groupName,
      total: 0,
      categoryMap: {},
    };
    const signedAmount = item.transaction_type === "expense" ? -Number(item.amount || 0) : Number(item.amount || 0);
    result[groupName].total += signedAmount;
    result[groupName].categoryMap[categoryName] = result[groupName].categoryMap[categoryName] || {
      name: categoryName,
      total: 0,
      items: [],
    };
    result[groupName].categoryMap[categoryName].total += signedAmount;
    result[groupName].categoryMap[categoryName].items.push(item);
    return result;
  }, {});

  return Object.values(groups).map((group) => ({
    ...group,
    categories: Object.values(group.categoryMap),
  }));
});

async function loadData() {
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
    error.value = `加载预算流转失败：${err.message}`;
  }
}

function formatAmount(value) {
  const prefix = Number(value || 0) < 0 ? "-" : "";
  return `${prefix}¥${Math.abs(Number(value || 0)).toFixed(2)}`;
}

function accountName(id) {
  const account = accounts.value.find((item) => item.id === id);
  return account ? account.name : `#${id}`;
}

function accountSummary(item) {
  if (item.transaction_type === "transfer") {
    return `${accountName(item.from_account_id)} → ${accountName(item.to_account_id)}`;
  }
  return accountName(item.from_account_id || item.to_account_id);
}

function categoryPathById(id) {
  const category = categories.value.find((item) => item.id === id);
  if (!category) {
    return `分类 #${id}`;
  }
  const parent = category.parent_id ? categories.value.find((item) => item.id === category.parent_id) : null;
  return parent ? `${parent.name}-${category.name}` : category.name;
}

onMounted(loadData);
</script>
