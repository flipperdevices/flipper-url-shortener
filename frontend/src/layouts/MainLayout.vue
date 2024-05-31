<template>
  <q-layout view="lHh Lpr lFf">
    <q-header flat>
      <q-toolbar>
        <q-toolbar-title>
          <router-link to="/" class="text-white">URL Shortener</router-link>
        </q-toolbar-title>
        <q-space />
        <div v-if="user" class="q-mr-md">
          Logged in as {{ userDisplayName }}
        </div>
        <q-btn flat dense icon="logout" label="Log out" :href="`${location.origin}/oauth2/sign_out?rd=${location.origin}/admin`" />
      </q-toolbar>
    </q-header>
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import showNotif from 'composables/useShowNotif'

const location = window.location
const user = ref(null)

const userDisplayName = computed(() => {
  if (!user.value) {
    return ''
  } else if (!user.value.preferredUsername) {
    return user.value.email
  } else {
    return `${user.value.preferredUsername} (${user.value.email})`
  }
})

onMounted(async () => {
  const response = await axios.get(`${location.origin}/oauth2/userinfo`)
    .catch(error => {
      console.error(error)
      if (error.response?.data?.detail) {
        if (error.response.data.detail[0]?.msg) {
          error.message = error.response.data.detail[0]?.msg
        } else {
          error.message = error.response?.data?.detail
        }
      }
      showNotif({
        message: `Failed to get user data: ${error.message}`,
        color: 'negative'
      })
    })
  user.value = response?.data
})
</script>
