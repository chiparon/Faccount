<template>
  <section class="panel" :class="{ 'panel-fill': fill }">
    <div class="panel-head">
      <div>
        <p v-if="kicker" class="panel-kicker">{{ kicker }}</p>
        <h2>{{ title }}</h2>
        <p v-if="description" class="panel-description">{{ description }}</p>
      </div>
      <slot name="actions" />
    </div>
    <div class="panel-body">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: "",
  },
  kicker: {
    type: String,
    default: "",
  },
  fill: {
    type: Boolean,
    default: false,
  },
});
</script>
