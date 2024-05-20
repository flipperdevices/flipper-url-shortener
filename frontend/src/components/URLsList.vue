<template>
  <div class="items-list-container column flex-center">
    <template v-if="rows.length">
      <q-table
        flat
        bordered
        :rows="rows"
        :columns="columns"
        row-key="id"
        hide-bottom
        :pagination="{ rowsPerPage: 0 }"
        no-data-label="No items to show"
      >
        <template v-slot:top>
          <div class="row items-center full-width">
            <q-btn
              unelevated
              icon="mdi-plus"
              label="New redirect"
              color="primary"
              @click="initNewURL(); addURLDialog = true"
            />

            <q-space />

            <div class="row q-gutter-x-md q-gutter-y-sm">
              <q-checkbox v-model="isCellEllipsis" dense label="Ellipsis" class="q-mr-sm" @update:model-value="localStore('isCellEllipsis', isCellEllipsis)" />

              <div class="row items-center no-wrap">
                <div>Items on page:</div>
                <q-select
                  v-model="queryParams.size"
                  :options="[10, 20, 50, 100]"
                  dense
                  borderless
                  class="q-ml-sm"
                  @update:model-value="localStore('queryParams.size', queryParams.size)"
                ></q-select>
              </div>

              <q-pagination
                v-model="queryParams.page"
                :max="totalPages"
                input
                @update:model-value="getURLs()"
              />
            </div>
          </div>
        </template>

        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td key="slug" :props="props" style="max-width: 400px;" :class="isCellEllipsis ? 'ellipsis' : 'white-space-normal break-all'">
              <LinkItem :href="SHORTENED_URL_BASE_PATH + props.row.slug" />
            </q-td>
            <q-td key="originalUrl" :props="props" style="max-width: 400px;" :class="isCellEllipsis ? 'ellipsis' : 'white-space-normal break-all'">
              <LinkItem :href="props.row.original_url" />
            </q-td>
            <q-td key="visits" :props="props">
              {{ props.row.visits }}
            </q-td>
            <q-td key="lastVisit" :props="props">
              {{ formattedDateTime(props.row.last_visit_at) }}
            </q-td>
            <q-td key="createdAt" :props="props">
              {{ formattedDateTime(props.row.created_at) }}
            </q-td>
            <q-td key="updatedAt" :props="props">
              {{ formattedDateTime(props.row.updated_at) }}
            </q-td>
            <q-td key="actions" :props="props">
              <div class="row no-wrap q-gutter-sm">
                <q-btn flat dense icon="mdi-pencil-outline" color="primary" @click="initURLToEdit(props.row); editURLDialog = true"/>
                <q-btn flat dense icon="mdi-delete-outline" color="negative" @click="URLToDelete = props.row; deleteURLDialog = true" />
              </div>
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </template>

    <q-dialog v-model="addURLDialog">
      <q-card class="dialog">
        <q-btn icon="close" flat round dense v-close-popup class="dialog-close-btn"/>

        <q-card-section v-if="newURL.status !== 'success'" class="q-pb-none">
          <div class="text-h6 q-my-sm">Create a new redirect</div>
        </q-card-section>

        <q-card-section v-if="newURL.status !== 'success'">
          <q-input
            v-model="newURL.slug"
            outlined
            hint="Short URL"
            :prefix="SHORTENED_URL_BASE_PATH"
            :rules="[val => !!val || 'Field is required']"
          >
            <template v-slot:label></template>
          </q-input>
          <div class="column flex-center q-mb-md">
            <q-icon name="mdi-arrow-down" size="1.5rem" color="primary"/>
          </div>
          <q-input
            v-model="newURL.originalUrl"
            outlined
            hint="Original URL"
            :rules="[val => !!val || 'Field is required']"
          />

          <div v-if="newURL.status === 'error'" class="q-mt-md">
            <div class="text-negative">
              <q-icon name="mdi-close-circle-outline" color="negative" style="position: relative; top: -1px" />
              {{ newURL.detail || 'Failed to create URL' }}
            </div>
          </div>
        </q-card-section>

        <q-card-section v-if="newURL.status === 'success'" align="center">
          <q-icon name="mdi-check-circle-outline" color="positive" size="64px" />
          <div class="q-mt-md break-all">
            <LinkItem :href="SHORTENED_URL_BASE_PATH + newURL.slug" />
            now points to
            <LinkItem :href="newURL.originalUrl" />
          </div>
        </q-card-section>

        <q-card-actions class="q-pt-none" align="right">
          <template v-if="newURL.status !== 'success'">
            <q-btn flat label="Cancel" v-close-popup/>
            <q-btn flat label="Create" color="primary" @click="createURL" :loading="isCreateURLLoading"/>
          </template>
          <q-btn v-else flat label="Close" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="deleteURLDialog">
      <q-card class="dialog">
        <q-btn icon="close" flat round dense v-close-popup class="dialog-close-btn"/>

        <q-card-section class="q-pb-none">
          <div class="text-h6 q-my-sm">Delete redirect</div>
          <div>
            Are you sure you want to delete <LinkItem :href="SHORTENED_URL_BASE_PATH + URLToDelete.slug" />?<br />
            It can still be in use, proceed with caution.
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup/>
          <q-btn flat label="Delete" color="negative" @click="deleteURL" :loading="isDeleteURLLoading" />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="editURLDialog">
      <q-card class="dialog">
        <q-btn icon="close" flat round dense v-close-popup class="dialog-close-btn"/>

        <q-card-section v-if="URLToEdit.status !== 'success'" class="q-pb-none">
          <div class="text-h6 q-my-sm">Edit redirect</div>
        </q-card-section>

        <q-card-section v-if="URLToEdit.status !== 'success'">
          <q-input
            v-model="URLToEdit.newSlug"
            outlined
            hint="Short URL"
            :prefix="SHORTENED_URL_BASE_PATH"
            :rules="[val => !!val || 'Field is required']"
          >
            <template v-slot:label></template>
          </q-input>
          <div class="column flex-center q-mb-md">
            <q-icon name="mdi-arrow-down" size="1.5rem" color="primary"/>
          </div>
          <q-input
            v-model="URLToEdit.newOriginalUrl"
            outlined
            hint="Original URL"
            :rules="[val => !!val || 'Field is required']"
          />

          <div v-if="URLToEdit.status === 'error'" class="q-mt-md">
            <div class="text-negative">
              <q-icon name="mdi-close-circle-outline" color="negative" style="position: relative; top: -1px" />
              {{ URLToEdit.detail || 'Failed to edit URL' }}
            </div>
          </div>
        </q-card-section>

        <q-card-section v-if="URLToEdit.status === 'success'" align="center">
          <q-icon name="mdi-check-circle-outline" color="positive" size="64px" />
          <div class="q-mt-md break-all">
            <LinkItem :href="SHORTENED_URL_BASE_PATH + URLToEdit.newSlug" />
            now points to
            <LinkItem :href="URLToEdit.newOriginalUrl" />
          </div>
        </q-card-section>

        <q-card-actions class="q-pt-none" align="right">
          <template v-if="URLToEdit.status !== 'success'">
            <q-btn flat label="Cancel" v-close-popup/>
            <q-btn
              flat
              label="Save"
              color="primary"
              @click="editURL" :loading="isEditURLLoading"
              :disable="URLToEdit.slug === URLToEdit.newSlug && URLToEdit.original_url === URLToEdit.newOriginalUrl"
            />
          </template>
          <q-btn v-else flat label="Close" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import showNotif from 'composables/useShowNotif'
import LinkItem from 'components/LinkItem.vue'

const API_ENDPOINT = process.env.API_ENDPOINT || `${location.origin}${location.pathname}/api/v0/`
const SHORTENED_URL_BASE_PATH = process.env.SHORTENED_URL_BASE_PATH

const localStore = (key, value) => {
  localStorage.setItem(key, value)
}

// table setup
const rows = ref([])
const columns = [
  { name: 'slug', label: 'Short URL', field: 'slug', align: 'left' },
  { name: 'originalUrl', label: 'Original URL', field: 'original_url', align: 'left' },
  { name: 'visits', label: 'Visits', field: 'visits', align: 'left' },
  { name: 'lastVisit', label: 'Last visit', field: 'last_visit_at', align: 'left' },
  { name: 'createdAt', label: 'Created at', field: 'created_at', align: 'left' },
  { name: 'updatedAt', label: 'Updated at', field: 'updated_at', align: 'left' },
  { name: 'actions', label: 'Actions', field: 'slug', align: 'left' }
]
const isCellEllipsis = ref(false)
const formattedDateTime = computed(() => (timestamp) => {
  const date = new Date(timestamp)
  return `${date.toLocaleDateString('nu').replaceAll('/', '.')} ${date.toLocaleTimeString('nu', { hour: 'numeric', minute: 'numeric' })}`
})

// get items
const totalItems = ref(0)
const totalPages = ref(0)
const queryParams = ref({
  page: 1,
  size: 50
})
const isURLsListLoading = ref(false)
const getURLs = async () => {
  isURLsListLoading.value = true
  const result = await axios.get(new URL('url/', API_ENDPOINT).href, {
    params: {
      page: queryParams.value.page,
      size: queryParams.value.size
    }
  })
    .then(res => {
      totalItems.value = res.data.total
      totalPages.value = res.data.pages
      return res.data.items
    })
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
        message: `Failed to get URLs: ${error.message}`,
        color: 'negative'
      })
    })
  isURLsListLoading.value = false
  rows.value = result || []
}

// add new URL
const newURL = ref({
  originalUrl: '',
  slug: '',
  status: '',
  detail: null
})
const initNewURL = () => {
  newURL.value = {
    originalUrl: '',
    slug: '',
    status: '',
    detail: null
  }
}
const isCreateURLLoading = ref(false)
const addURLDialog = ref(false)
const createURL = async () => {
  isCreateURLLoading.value = true
  await axios.post(new URL('url/', API_ENDPOINT), {
    original_url: newURL.value.originalUrl,
    slug: newURL.value.slug
  })
    .then(res => {
      console.log(res.data)
      newURL.value.status = 'success'
    })
    .catch(error => {
      console.error(error)
      newURL.value.status = 'error'
      if (error.response?.data?.detail) {
        if (error.response.data.detail[0]?.msg) {
          newURL.value.detail = error.response.data.detail[0]?.msg
          error.message = error.response.data.detail[0]?.msg
        } else {
          newURL.value.detail = error.response?.data?.detail
          error.message = error.response?.data?.detail
        }
      }
      showNotif({
        message: `Failed to create URL: ${error.message}`,
        color: 'negative'
      })
    })
  await getURLs()
  isCreateURLLoading.value = false
}

// delete URL
const URLToDelete = ref({
  id: -1,
  slug: ''
})
const isDeleteURLLoading = ref(false)
const deleteURLDialog = ref(false)
const deleteURL = async () => {
  isDeleteURLLoading.value = true
  await axios.delete(new URL(`url/${URLToDelete.value.id}`, API_ENDPOINT))
    .then(res => {
      console.log(res.data)
    })
    .catch(error => {
      console.error(error)
      showNotif({
        message: `Failed to delete URL: ${error.message}`,
        color: 'negative'
      })
    })
  await getURLs()
  deleteURLDialog.value = false
  isDeleteURLLoading.value = false
}

// edit URL
const URLToEdit = ref({
  id: -1,
  original_url: '',
  newOriginalUrl: '',
  slug: '',
  newSlug: '',
  status: '',
  detail: null
})
const initURLToEdit = (row) => {
  URLToEdit.value = row
  URLToEdit.value.newSlug = URLToEdit.value.slug
  URLToEdit.value.newOriginalUrl = URLToEdit.value.original_url
}
const isEditURLLoading = ref(false)
const editURLDialog = ref(false)
const editURL = async () => {
  isEditURLLoading.value = true
  const data = {}
  if (URLToEdit.value.slug !== URLToEdit.value.newSlug) {
    data.slug = URLToEdit.value.newSlug
  }
  if (URLToEdit.value.original_url !== URLToEdit.value.newOriginalUrl) {
    data.original_url = URLToEdit.value.newOriginalUrl
  }
  await axios.patch(new URL(`url/${URLToEdit.value.id}`, API_ENDPOINT), data)
    .then(() => {
      URLToEdit.value.status = 'success'
    })
    .catch(error => {
      console.error(error)
      URLToEdit.value.status = 'error'
      if (error.response?.data?.detail) {
        if (error.response.data.detail[0]?.msg) {
          URLToEdit.value.detail = error.response.data.detail[0]?.msg
          error.message = error.response.data.detail[0]?.msg
        } else {
          URLToEdit.value.detail = error.response?.data?.detail
          error.message = error.response?.data?.detail
        }
      }
      showNotif({
        message: `Failed to edit URL: ${error.message}`,
        color: 'negative'
      })
    })
  await getURLs()
  isEditURLLoading.value = false
}

onMounted(async () => {
  // restore settings
  if (localStorage.getItem('isCellEllipsis') === 'true') {
    isCellEllipsis.value = true
  }
  const storedSize = localStorage.getItem('queryParams.size')
  if (storedSize && !isNaN(Number(storedSize)) && Number(storedSize) > 0) {
    queryParams.value.size = Number(storedSize)
  }

  // get URLs
  await getURLs()
  console.log(rows.value)
})
</script>

<style lang="sass" scoped>
.items-list-container
  max-width: calc(100vw - 16px)
  width: 100%
</style>
