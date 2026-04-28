<template>
  <Panel title="账单导入缓存" kicker="Import Cache" description="微信/支付宝账单先进入缓存，微调后再压入流水池">
    <div class="import-drop">
      <input type="file" accept=".csv,.xlsx,text/csv" @change="handleFile" />
      <div>
        <strong>选择微信 XLSX 或支付宝 CSV</strong>
        <span>会自动跳过导出说明行，识别交易字段，并生成可编辑流水草稿。</span>
      </div>
    </div>

    <p v-if="message" class="notice success">{{ message }}</p>
    <p v-if="error" class="notice error">{{ error }}</p>

    <div class="import-batches">
      <article v-for="batch in batches" :key="batch.id" class="import-batch">
        <div class="import-batch-head">
          <div>
            <strong>{{ batch.name }}</strong>
            <span>
              {{ sourceLabel(batch.source) }} / {{ selectedCount(batch) }} 条待提交 /
              {{ batch.drafts.length }} 条草稿 / {{ formatDate(batch.created_at) }}
            </span>
          </div>
          <div class="import-actions">
            <select v-model="batch.default_account_id" @change="applyDefaultAccount(batch)">
              <option :value="null">选择默认账户</option>
              <option v-for="account in accounts" :key="account.id" :value="account.id">
                {{ account.name }} / {{ account.type }}
              </option>
            </select>
            <button class="filter-submit" type="button" @click="commitBatch(batch)" :disabled="!selectedCount(batch)">
              压入流水池
            </button>
            <button v-if="batch.created_transaction_ids?.length" class="danger-link" type="button" @click="undoCommittedBatch(batch)">
              撤销压入
            </button>
            <button class="danger-link" type="button" @click="removeBatch(batch.id)">移除缓存</button>
          </div>
        </div>

        <div class="import-drafts">
          <article v-for="draft in batch.drafts" :key="draft.local_id" class="import-draft-row">
            <label class="checkbox-cell">
              <input v-model="draft.selected" type="checkbox" />
            </label>
            <input v-model.trim="draft.title" placeholder="名称" />
            <input v-model.number="draft.amount" type="number" min="0.01" step="0.01" placeholder="金额" />
            <input v-model="draft.occurred_at" type="datetime-local" />
            <select v-model="draft.transaction_type">
              <option value="expense">支出</option>
              <option value="income">收入</option>
              <option value="transfer">转账</option>
            </select>
            <select v-model="draft.category_id">
              <option :value="null">选择分类</option>
              <option v-for="category in categoriesForDraft(draft)" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
            <select v-model="draft.account_id">
              <option :value="null">选择账户</option>
              <option v-for="account in accounts" :key="account.id" :value="account.id">
                {{ account.name }}
              </option>
            </select>
            <input v-model.trim="draft.note" placeholder="备注/交易对方/订单号" />
          </article>
        </div>

        <details class="raw-preview">
          <summary>查看原始字段预览</summary>
          <div class="import-table-wrap">
            <table class="import-table">
              <thead>
                <tr>
                  <th v-for="header in batch.headers" :key="header">{{ header }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in batch.rows.slice(0, 6)" :key="index">
                  <td v-for="header in batch.headers" :key="header">{{ row[header] }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </details>
      </article>
      <p v-if="!batches.length" class="empty-state">暂无导入缓存。</p>
    </div>
  </Panel>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { strFromU8, unzipSync } from "fflate";
import Panel from "../components/Panel.vue";
import { api } from "../api/client";

const STORAGE_KEY = "faccounts.import-cache.v2";
const batches = ref([]);
const accounts = ref([]);
const categories = ref([]);
const error = ref("");
const message = ref("");

function sourceLabel(source) {
  return {
    wechat: "微信",
    alipay: "支付宝",
    unknown: "未知来源",
  }[source] || source;
}

function detectSource(name, headers) {
  const text = `${name} ${headers.join(" ")}`;
  if (text.includes("微信") || text.toLowerCase().includes("wechat") || headers.includes("交易类型")) {
    return "wechat";
  }
  if (text.includes("支付宝") || text.toLowerCase().includes("alipay") || headers.includes("交易分类")) {
    return "alipay";
  }
  return "unknown";
}

async function readTextFile(file) {
  const buffer = await file.arrayBuffer();
  const bytes = new Uint8Array(buffer);
  const decoderNames = ["utf-8", "gb18030", "gbk"];
  for (const name of decoderNames) {
    try {
      const text = new TextDecoder(name).decode(bytes);
      if (text.includes("交易时间") || text.includes("支付宝") || text.includes("微信")) {
        return text;
      }
    } catch {
      // Try next decoder.
    }
  }
  return await file.text();
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let cell = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];
    if (char === '"' && quoted && next === '"') {
      cell += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      row.push(cell.trim());
      cell = "";
    } else if ((char === "\n" || char === "\r") && !quoted) {
      if (char === "\r" && next === "\n") {
        index += 1;
      }
      row.push(cell.trim());
      if (row.some(Boolean)) {
        rows.push(row);
      }
      row = [];
      cell = "";
    } else {
      cell += char;
    }
  }
  if (cell || row.length) {
    row.push(cell.trim());
    rows.push(row);
  }
  return rows;
}

function rowsToObjects(rows) {
  const headerIndex = rows.findIndex((row) => row.includes("交易时间"));
  if (headerIndex < 0) {
    return { headers: [], rows: [] };
  }
  const headers = rows[headerIndex].map((header, index) => header || `字段${index + 1}`);
  return {
    headers,
    rows: rows.slice(headerIndex + 1).map((row) =>
      headers.reduce((result, header, index) => {
        result[header] = row[index] || "";
        return result;
      }, {}),
    ),
  };
}

function excelDateToLocalInput(value) {
  if (value instanceof Date) {
    return toLocalInputValue(value);
  }
  const numeric = Number(value);
  if (!Number.isNaN(numeric) && numeric > 10000) {
    const utcDays = Math.floor(numeric - 25569);
    const utcValue = utcDays * 86400;
    const dateInfo = new Date(utcValue * 1000);
    const fractionalDay = numeric - Math.floor(numeric) + 0.0000001;
    const totalSeconds = Math.floor(86400 * fractionalDay);
    dateInfo.setSeconds(totalSeconds);
    return toLocalInputValue(dateInfo);
  }
  return toLocalInputValue(new Date(value));
}

function toLocalInputValue(date) {
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

function normalizeAmount(value) {
  const text = String(value || "").replace(/[¥￥,\s]/g, "");
  const match = text.match(/-?\d+(\.\d+)?/);
  return match ? Number(match[0]) : 0;
}

function normalizeType(value) {
  if (String(value).includes("收入")) {
    return "income";
  }
  if (String(value).includes("支出")) {
    return "expense";
  }
  return "transfer";
}

function guessCategoryId(row, source, type) {
  const text = [
    row["交易分类"],
    row["交易类型"],
    row["商品说明"],
    row["商品"],
    row["交易对方"],
  ].join(" ");
  const exact = categories.value.find((category) => text.includes(category.name) && category.kind === type);
  if (exact) {
    return exact.id;
  }
  const dictionary = [
    ["餐饮", ["餐饮", "美食", "饭", "轻餐", "盒马", "饮料", "可乐", "水果"]],
    ["交通", ["交通", "打车", "高德", "公交", "地铁"]],
    ["日用", ["日用", "百货", "超市", "扫把", "便利"]],
    ["娱乐", ["娱乐", "游戏", "会员", "VIP"]],
  ];
  const hit = dictionary.find(([, words]) => words.some((word) => text.includes(word)));
  if (hit) {
    const [name] = hit;
    const category = categories.value.find((item) => item.name.includes(name) && item.kind === type);
    if (category) {
      return category.id;
    }
  }
  return categories.value.find((category) => category.kind === type)?.id || null;
}

function normalizeDraft(row, source, fileName) {
  const type = normalizeType(row["收/支"]);
  const isAlipay = source === "alipay";
  const title = isAlipay
    ? row["商品说明"] || row["交易对方"] || "支付宝导入流水"
    : row["商品"] || row["交易对方"] || "微信导入流水";
  const counterparty = row["交易对方"] || "";
  const paymentMethod = row["收/付款方式"] || row["支付方式"] || "";
  const status = row["交易状态"] || row["当前状态"] || "";
  const orderId = row["交易订单号"] || row["交易单号"] || "";
  const occurredAt = source === "wechat"
    ? excelDateToLocalInput(row["交易时间"])
    : toLocalInputValue(new Date(row["交易时间"]));
  const amount = normalizeAmount(row["金额"] || row["金额(元)"]);
  const category_id = type === "transfer" ? null : guessCategoryId(row, source, type);
  return {
    local_id: crypto.randomUUID(),
    selected: type !== "transfer" && amount > 0,
    raw_type: row["收/支"],
    title,
    amount,
    occurred_at: occurredAt,
    transaction_type: type,
    category_id,
    account_id: null,
    source_logic: `${sourceLabel(source)}导入:${fileName}`,
    note: [counterparty, paymentMethod, status, orderId].filter(Boolean).join(" / "),
    raw: row,
  };
}

async function parseFile(file) {
  if (file.name.toLowerCase().endsWith(".xlsx")) {
    return rowsToObjects(parseXlsxRows(await file.arrayBuffer()));
  }
  const text = await readTextFile(file);
  return rowsToObjects(parseCsv(text));
}

function parseXlsxRows(buffer) {
  const files = unzipSync(new Uint8Array(buffer));
  const shared = readSharedStrings(files);
  const sheetName = files["xl/worksheets/sheet1.xml"]
    ? "xl/worksheets/sheet1.xml"
    : Object.keys(files).find((name) => name.startsWith("xl/worksheets/sheet"));
  if (!sheetName) {
    throw new Error("无法找到 XLSX 工作表");
  }
  const xml = strFromU8(files[sheetName]);
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  return [...doc.querySelectorAll("sheetData row")].map((row) =>
    [...row.querySelectorAll("c")].map((cell) => readCellValue(cell, shared)),
  );
}

function readSharedStrings(files) {
  if (!files["xl/sharedStrings.xml"]) {
    return [];
  }
  const xml = strFromU8(files["xl/sharedStrings.xml"]);
  const doc = new DOMParser().parseFromString(xml, "application/xml");
  return [...doc.querySelectorAll("si")].map((item) =>
    [...item.querySelectorAll("t")].map((node) => node.textContent || "").join(""),
  );
}

function readCellValue(cell, shared) {
  const value = cell.querySelector("v")?.textContent || "";
  if (cell.getAttribute("t") === "s") {
    return shared[Number(value)] || "";
  }
  const inlineText = cell.querySelector("is t")?.textContent;
  return inlineText || value;
}

async function handleFile(event) {
  const file = event.target.files?.[0];
  if (!file) {
    return;
  }
  try {
    error.value = "";
    message.value = "";
    await loadOptions();
    const parsed = await parseFile(file);
    if (!parsed.headers.length) {
      throw new Error("无法识别账单表头");
    }
    const source = detectSource(file.name, parsed.headers);
    const drafts = parsed.rows
      .filter((row) => row["交易时间"] && (row["金额"] || row["金额(元)"]))
      .map((row) => normalizeDraft(row, source, file.name));
    const batch = {
      id: crypto.randomUUID(),
      name: file.name,
      source,
      created_at: new Date().toISOString(),
      default_account_id: null,
      created_transaction_ids: [],
      headers: parsed.headers,
      rows: parsed.rows,
      drafts,
    };
    batches.value = [batch, ...batches.value];
    persist();
    message.value = `已识别 ${drafts.length} 条账单记录，进入导入缓存池`;
  } catch (err) {
    error.value = `导入失败：${err.message}`;
  } finally {
    event.target.value = "";
  }
}

function categoriesForDraft(draft) {
  return categories.value.filter((category) => category.kind === draft.transaction_type);
}

function selectedCount(batch) {
  return batch.drafts.filter((draft) => draft.selected).length;
}

function applyDefaultAccount(batch) {
  batch.drafts.forEach((draft) => {
    if (draft.selected && !draft.account_id) {
      draft.account_id = batch.default_account_id;
    }
  });
  persist();
}

function buildPayload(draft) {
  const accountId = draft.account_id || null;
  return {
    title: draft.title,
    transaction_type: draft.transaction_type,
    occurred_at: new Date(draft.occurred_at).toISOString(),
    amount: draft.amount,
    category_id: draft.category_id,
    from_account_id: draft.transaction_type === "expense" ? accountId : null,
    to_account_id: draft.transaction_type === "income" ? accountId : null,
    note: draft.note || null,
    source_logic: draft.source_logic,
    items: [],
  };
}

function validateDraft(draft) {
  if (!draft.title || !draft.amount || !draft.occurred_at || !draft.category_id) {
    return "名称、金额、时间、分类不能为空";
  }
  if (draft.transaction_type !== "transfer" && !draft.account_id) {
    return "收入/支出需要选择账户";
  }
  if (draft.transaction_type === "transfer") {
    return "中性交易/不计收支暂不自动压入，请手动改为收入或支出后再提交";
  }
  return "";
}

async function commitBatch(batch) {
  try {
    error.value = "";
    message.value = "";
    const selected = batch.drafts.filter((draft) => draft.selected);
    for (const draft of selected) {
      const validation = validateDraft(draft);
      if (validation) {
        throw new Error(`「${draft.title}」${validation}`);
      }
    }
    const createdIds = [];
    for (const draft of selected) {
      const created = await api.createTransaction(buildPayload(draft));
      createdIds.push(created.id);
      draft.selected = false;
      draft.created_transaction_id = created.id;
    }
    batch.created_transaction_ids = [...(batch.created_transaction_ids || []), ...createdIds];
    persist();
    window.dispatchEvent(new CustomEvent("transactions-updated"));
    message.value = `已压入 ${createdIds.length} 条流水`;
  } catch (err) {
    error.value = `压入失败：${err.message}`;
  }
}

async function undoCommittedBatch(batch) {
  try {
    error.value = "";
    message.value = "";
    const ids = [...(batch.created_transaction_ids || [])];
    for (const id of ids) {
      await api.deleteTransaction(id);
    }
    batch.created_transaction_ids = [];
    batch.drafts.forEach((draft) => {
      draft.created_transaction_id = null;
    });
    persist();
    window.dispatchEvent(new CustomEvent("transactions-updated"));
    message.value = `已撤销 ${ids.length} 条已压入流水，记录进入 Trash`;
  } catch (err) {
    error.value = `撤销失败：${err.message}`;
  }
}

function removeBatch(id) {
  batches.value = batches.value.filter((batch) => batch.id !== id);
  persist();
  message.value = "已移除该导入缓存";
}

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(batches.value));
}

function formatDate(value) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

async function loadOptions() {
  const [accountRows, categoryRows] = await Promise.all([
    api.listAccounts(),
    api.listCategories(),
  ]);
  accounts.value = accountRows;
  categories.value = categoryRows;
}

onMounted(async () => {
  try {
    batches.value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    batches.value = [];
  }
  await loadOptions();
});
</script>
