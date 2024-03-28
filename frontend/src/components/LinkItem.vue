<template>
  <div style="display: inline-block;">
    <q-btn
      flat
      dense
      :color="isCopySuccess ? 'positive' : 'primary'"
      :icon="isCopySuccess ? 'mdi-check' : 'mdi-content-copy'"
      @click="copy(href)"
      size="0.55rem"
      style="margin: -2px 1px 0 0;"
    />
    <a :href="href" _target="blank" class="link-item bg-blue-grey-1">
      {{ href }}
    </a>
  </div>
</template>

<script setup>
import { defineProps, ref } from 'vue'
import { copyToClipboard } from 'quasar'

defineProps({
  href: {
    type: String,
    required: true
  }
})

const isCopySuccess = ref(false)
const copy = (text) => {
  isCopySuccess.value = false
  copyToClipboard(text)
    .then(() => {
      isCopySuccess.value = true
      setTimeout(() => {
        isCopySuccess.value = false
      }, 1500)
    })
}
</script>
