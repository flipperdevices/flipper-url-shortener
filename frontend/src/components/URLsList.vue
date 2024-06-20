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
        v-model:pagination="queryParams"
        no-data-label="No items to show"
        :loading="isURLsListLoading"
        @request="onURLsRequest"
        binary-state-sort
      >
        <template v-slot:top>
          <div class="row items-center full-width">
            <q-btn
              unelevated
              icon="mdi-plus"
              label="New redirect"
              color="primary"
              @click="onNewRedirect"
            />

            <q-space />

            <div class="row q-gutter-x-md q-gutter-y-sm">
              <q-checkbox v-model="isCellEllipsis" dense label="Ellipsis" class="q-mr-sm" @update:model-value="localStore('isCellEllipsis', isCellEllipsis)" />

              <div class="row items-center no-wrap">
                <div>Items on page:</div>
                <q-select
                  v-model="queryParams.rowsPerPage"
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
                @update:model-value="onURLsRequest({ pagination: queryParams })"
              />
            </div>
          </div>
        </template>

        <template v-slot:header-cell="props">
          <q-th :props="props" style="padding-top: 15px; vertical-align: top">
            {{ props.col.label }}
          </q-th>
        </template>

        <template v-slot:header-cell-tags="props">
          <q-th
            :props="props"
            :style="`${filterTags.length ? 'padding-top: 8px;' : ''} padding-bottom: 8px; max-width: 250px;`"
          >
            <q-btn
              class="full-width text-caption text-weight-medium"
              color="primary"
              text-color="black"
              align="between"
              :label="props.col.label"
              icon-right="filter_list"
              no-icon-animation
              no-caps
              flat
              @click="openFilterTagsDialog"
            />
            <div class="q-mt-sm">
              <TagList
                :tags="filterTags"
                :selectedTags="filterTags"
                clickable
                @click="addFilterTag"
              />
            </div>
          </q-th>
        </template>

        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td key="slug" :props="props" style="max-width: 400px;" :class="isCellEllipsis ? 'ellipsis' : 'white-space-normal break-all'">
              <LinkItem :href="SHORTENED_URL_BASE_PATH + props.row.slug" />
            </q-td>
            <q-td key="original_url" :props="props" style="max-width: 400px;" :class="isCellEllipsis ? 'ellipsis' : 'white-space-normal break-all'">
              <LinkItem :href="props.row.original_url" />
            </q-td>
            <q-td key="visits" :props="props">
              {{ props.row.visits }}
            </q-td>
            <q-td key="tags" :props="props" style="max-width: 250px;">
              <TagList
                :tags="props.row.tags"
                :selectedTags="props.row.tags"
                clickable
                @click="addFilterTag"
              />
            </q-td>
            <q-td key="last_visit_at" :props="props">
              {{ formattedDateTime(props.row.last_visit_at) }}
            </q-td>
            <q-td key="created_at" :props="props">
              {{ formattedDateTime(props.row.created_at) }}
            </q-td>
            <q-td key="updated_at" :props="props">
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
    <q-btn
      v-else
      unelevated
      icon="mdi-plus"
      label="New redirect"
      color="primary"
      @click="onNewRedirect"
    />

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

          <div class="q-mt-md flex column q-gutter-sm">
            <div class="flex justify-between items-center">
              <p class="q-mb-none text-body1">Tags</p>
              <q-btn
                outline
                padding="xs"
                color="primary"
                icon="add"
                @click="openAddTagsDialog"
              />
            </div>
            <TagList
              :tags="tags"
              :selectedTags="tags"
              removable
              @remove="localDeleteTagUrl"
            />
          </div>

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

    <q-dialog v-model="editURLDialog" @hide="URLToEdit = {
      id: -1,
      original_url: '',
      newOriginalUrl: '',
      slug: '',
      newSlug: '',
      status: '',
      detail: null
    }">
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

          <div class="q-mt-md flex column q-gutter-sm">
            <div class="flex justify-between items-center">
              <p class="q-mb-none text-body1">Tags</p>
              <q-btn
                outline
                padding="xs"
                color="primary"
                icon="add"
                @click="openAddTagsDialog"
              />
            </div>
            <TagList
              :tags="URLToEdit.tags"
              :selectedTags="URLToEdit.tags"
              removable
              @remove="localDeleteTagUrl"
            />
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
              @click="editURL"
              :loading="isEditURLLoading"
              :disable="isDisableSaveBtn"
            />
          </template>
          <q-btn v-else flat label="Close" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="dialogNewTag" @hide="clearSearchTagParams">
      <q-card class="dialog">
        <q-card-section class="q-pb-none">
          <div class="text-h6 q-my-sm">Add tags</div>
        </q-card-section>
        <q-card-section>
          <q-input
            v-model.trim="searchTagParams.query"
            type="text"
            hint="Search or create tag"
            outlined
            debounce="300"
            @update:model-value="onSearchTag"
          >
          <template v-slot:append>
            <q-btn
              v-show="showCreateTagBtn"
              color="primary"
              label="Create"
              flat
              no-caps
              @click="createNewTag"
            />
          </template>
          </q-input>
        </q-card-section>
        <q-card-section>
          <TagList
            :tags="allTags"
            :selectedTags="tags"
            clickable
            removable
            @click="(val) => addTag({
              tag: val
            })"
            @remove="deleteTag"
          />
          <div
            v-show="searchTagParams.pages > 1"
            class="flex justify-center q-mt-sm"
          >
            <q-pagination
              v-model="searchTagParams.page"
              :max="searchTagParams.pages"
              :max-pages="searchTagParams.pages > 6 ? 6 : searchTagParams.pages"
              boundary-numbers
              direction-links
              @update:model-value="changeTagPage"
            />
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <q-dialog v-model="dialogFilterTag" @hide="clearSearchTagParams">
      <q-card class="dialog">
        <q-card-section class="q-pb-none">
          <div class="text-h6 q-my-sm">Add tags for filtering</div>
        </q-card-section>
        <q-card-section>
          <q-input
            v-model.trim="searchTagParams.query"
            type="text"
            hint="Search filter tag"
            outlined
            debounce="300"
            @update:model-value="onSearchTag"
          />
        </q-card-section>
        <q-card-section>
          <TagList
            :tags="allTags"
            :selectedTags="filterTags"
            clickable
            removable
            @click="addFilterTag"
            @remove="deleteTag"
          />
          <div
            v-show="searchTagParams.pages > 1"
            class="flex justify-center q-mt-sm"
          >
            <q-pagination
              v-model="searchTagParams.page"
              :max="searchTagParams.pages"
              :max-pages="searchTagParams.pages > 6 ? 6 : searchTagParams.pages"
              boundary-numbers
              direction-links
              @update:model-value="changeTagPage"
            />
          </div>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancel" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import showNotif from 'composables/useShowNotif'
import LinkItem from 'components/LinkItem.vue'
import TagList from 'components/tags/TagList.vue'

const API_ENDPOINT = `${location.origin}${process.env.API_PATH || '/api/v0'}`
const SHORTENED_URL_BASE_PATH = process.env.SHORTENED_URL_BASE_PATH || `${location.origin}/`

const localStore = (key, value) => {
  localStorage.setItem(key, value)
}

// table setup
const rows = ref([])
const columns = [
  { name: 'slug', label: 'Short URL', field: 'slug', align: 'left', sortable: true },
  { name: 'original_url', label: 'Original URL', field: 'original_url', align: 'left', sortable: true },
  { name: 'visits', label: 'Visits', field: 'visits', align: 'left', sortable: true },
  { name: 'tags', label: 'Tags', field: 'tags', align: 'left' },
  { name: 'last_visit_at', label: 'Last visit', field: 'last_visit_at', align: 'left', sortable: true },
  { name: 'created_at', label: 'Created at', field: 'created_at', align: 'left', sortable: true },
  { name: 'updated_at', label: 'Updated at', field: 'updated_at', align: 'left', sortable: true },
  { name: 'actions', label: 'Actions', field: 'slug', align: 'left', sortable: true }
]
const isCellEllipsis = ref(false)
const formattedDateTime = computed(() => (timestamp) => {
  const date = new Date(timestamp)
  return `${String(date.getDate()).padStart(2, '0')}.${String(date.getMonth() + 1).padStart(2, '0')}.${date.getFullYear()} ${date.toLocaleTimeString('nu', { hour: 'numeric', minute: 'numeric' })}`
})

const isDisableSaveBtn = computed(() => {
  return URLToEdit.value.slug === URLToEdit.value.newSlug &&
  URLToEdit.value.original_url === URLToEdit.value.newOriginalUrl
})

// get items
const totalItems = ref(0)
const totalPages = ref(0)
const queryParams = ref({
  sortBy: 'created_at',
  sortOrder: 'desc',
  descending: true,
  page: 1,
  rowsPerPage: 50,
  rowsNumber: computed(() => totalItems.value),
  tags: []
})
const changeRowsPerPage = async () => {
  localStore('queryParams.size', queryParams.value.rowsPerPage)

  await getURLs()
}
const onURLsRequest = async (props) => {
  const { page, sortBy, descending } = props.pagination

  console.log('descending', descending)

  if (sortBy && descending) {
    queryParams.value.sortOrder = 'desc'
    queryParams.value.sortBy = sortBy
  } else if (sortBy && !descending) {
    queryParams.value.sortOrder = 'asc'
    queryParams.value.sortBy = sortBy
  }

  queryParams.value.page = page
  queryParams.value.descending = descending

  await getURLs()
}
const isURLsListLoading = ref(false)
const getURLs = async () => {
  isURLsListLoading.value = true

  const result = await axios.get(new URL('url/', API_ENDPOINT).href, {
    params: {
      page: queryParams.value.page,
      size: queryParams.value.rowsPerPage,
      sort_by: queryParams.value.sortBy,
      sort_order: queryParams.value.sortOrder,
      tag_ids: queryParams.value.tags.map((tag) => tag.id)
    },
    paramsSerializer: {
      indexes: null
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

const onNewRedirect = () => {
  initNewURL()
  addURLDialog.value = true
  searchTagParams.value.query = ''
  tags.value = []
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
const dialogNewTag = ref(false)
const openAddTagsDialog = () => {
  dialogNewTag.value = true
}
const showCreateTagBtn = ref(false)
const allTags = ref([])
const tagNames = computed(() => {
  return allTags.value.map(i => i.name)
})
const maxTagPages = ref(1)
const searchTagParams = ref({
  query: '',
  page: 1,
  pages: computed(() => maxTagPages.value),
  size: 50
})
const changeTagPage = async (value) => {
  await getTags({
    page: value
  })
}
const clearSearchTagParams = async () => {
  searchTagParams.value = {
    query: '',
    page: 1,
    pages: computed(() => maxTagPages.value),
    size: 50
  }

  await getTags()
}
const onSearchTag = async () => {
  await getTags()
}
watch(() => searchTagParams.value.query, (value) => {
  if (tagNames.value.includes(value) || !value) {
    showCreateTagBtn.value = false
  } else {
    showCreateTagBtn.value = true
  }
})
const getTags = async ({
  query = searchTagParams.value.query,
  page = searchTagParams.value.page,
  size = searchTagParams.value.size
} = {}) => {
  if (!query.trim().length) {
    query = null
  }
  await axios.get(new URL('tag/', API_ENDPOINT).href, {
    params: {
      query,
      page,
      size
    }
  })
    .then(({ data }) => {
      allTags.value = data.items
      maxTagPages.value = data.pages
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
        message: `Failed to get Tags: ${error.message}`,
        color: 'negative'
      })
    })
}
const tags = ref([])
const createNewTag = async () => {
  await axios.post(new URL('tag/', API_ENDPOINT), {
    name: searchTagParams.value.query
  })
    .then(({ data }) => {
      addTag({
        tag: data,
        isShowNotif: false
      })
      if (URLToEdit.value.id !== -1) {
        showNotif({
          message: `Successfully added «${searchTagParams.value.query}» tag to URL`,
          color: 'positive',
          timeout: 1000
        })
      }
      searchTagParams.value.query = ''
      getTags()
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
        message: `Failed to create new Tags: ${error.message}`,
        color: 'negative'
      })
    })
}
const originalUrlTags = ref([]) // newUrlTags
const addTag = async ({ tag, isShowNotif = true }) => {
  let _tags = []

  if (URLToEdit.value.id !== -1) {
    _tags = URLToEdit.value.tags
  } else {
    _tags = tags.value
    isShowNotif = false
  }

  const tagIndex = _tags.findIndex((i) => i.id === tag.id)
  if (tagIndex === -1) {
    _tags.push(tag)

    if (editURLDialog.value) {
      const originalTagsArrayMap = new Map(originalUrlTags.value.map((x) => [x.id, x]))
      const addedTags = _tags.filter((x) => !originalTagsArrayMap.has(x.id))

      await addTagsUrl({
        UrlId: URLToEdit.value.id,
        tags: addedTags,
        isShowNotif
      })
    }
  } else {
    _tags.splice(tagIndex, 1)

    if (editURLDialog.value) {
      await deleteTagsUrl({
        UrlId: URLToEdit.value.id,
        tags: [tag]
      })
    }
  }
}
const deleteTag = (tag) => {
  axios.delete(new URL(`tag/${tag.id}`, API_ENDPOINT))
    .then(res => {
      rows.value.forEach(row => {
        const tagIndex = row.tags.findIndex((i) => i.id === tag.id)
        if (tagIndex !== -1) {
          row.tags.splice(tagIndex, 1)
        }
      })

      showNotif({
        message: `Successfully removed «${tag.name}» tag to URL`,
        color: 'positive',
        timeout: 1000
      })

      getTags()
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
        message: `Failed to delete Tag: ${error.message}`,
        color: 'negative'
      })
    })
}
const localDeleteTagUrl = async (tag) => {
  let _tags = []

  if (URLToEdit.value.id !== -1) {
    _tags = URLToEdit.value.tags
  } else {
    _tags = tags.value
  }

  const tagIndex = _tags.findIndex((i) => i.id === tag.id)
  if (tagIndex !== -1) {
    _tags.splice(tagIndex, 1)

    if (editURLDialog.value) {
      await deleteTagsUrl({
        UrlId: URLToEdit.value.id,
        tags: [tag]
      })
    }
  }
}
const addTagsUrl = async ({ UrlId, tags, isShowNotif = true }) => {
  await axios.post(new URL(`url/${UrlId}/tag`, API_ENDPOINT), {
    tag_ids: tags.map((tag) => tag.id)
  })
    .then(() => {
      if (isShowNotif) {
        tags.forEach(tag => {
          showNotif({
            message: `Successfully added «${tag.name}» tag to URL`,
            color: 'positive',
            timeout: 1000
          })
        })
      }
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
        message: `Failed to add Tag to URL: ${error.message}`,
        color: 'negative'
      })
    })
}
const deleteTagsUrl = async ({ UrlId, tags }) => {
  await axios.delete(new URL(`url/${UrlId}/tag`, API_ENDPOINT), {
    data: {
      tag_ids: tags.map((tag) => tag.id)
    }
  })
    .then(async () => {
      tags.forEach(tag => {
        const tagIndex = originalUrlTags.value.findIndex((i) => i.id === tag.id)
        if (tagIndex !== -1) {
          originalUrlTags.value.splice(tagIndex, 1)
        }

        showNotif({
          message: `Successfully removed «${tag.name}» tag to URL`,
          color: 'positive',
          timeout: 1000
        })
      })

      await getURLs()
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
        message: `Failed to remove Tag to URL: ${error.message}`,
        color: 'negative'
      })
    })
}

const dialogFilterTag = ref(false)
const openFilterTagsDialog = () => {
  dialogFilterTag.value = true
}
const filterTags = ref([])
const addFilterTag = async (tag) => {
  const _tags = filterTags.value

  const tagIndex = _tags.findIndex((i) => i.id === tag.id)
  if (tagIndex === -1) {
    _tags.push(tag)
  } else {
    _tags.splice(tagIndex, 1)
  }

  if (_tags.length) {
    queryParams.value.tags = _tags
  } else {
    queryParams.value.tags = []
  }

  await getURLs()
}

const isCreateURLLoading = ref(false)
const addURLDialog = ref(false)
const createURL = async () => {
  isCreateURLLoading.value = true
  await axios.post(new URL('url/', API_ENDPOINT), {
    original_url: newURL.value.originalUrl,
    slug: newURL.value.slug
  })
    .then(async ({ data }) => {
      newURL.value.status = 'success'

      await addTagsUrl({
        UrlId: data.id,
        tags: tags.value,
        isShowNotif: false
      })
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

  tags.value = URLToEdit.value.tags
  originalUrlTags.value = [...URLToEdit.value.tags]
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

  if (Object.keys(data).length) {
    await axios.patch(new URL(`url/${URLToEdit.value.id}`, API_ENDPOINT), data)
      .then(async () => {
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
  }
  isEditURLLoading.value = false
}

onMounted(async () => {
  // restore settings
  if (localStorage.getItem('isCellEllipsis') === 'true') {
    isCellEllipsis.value = true
  }
  const storedSize = localStorage.getItem('queryParams.size')
  if (storedSize && !isNaN(Number(storedSize)) && Number(storedSize) > 0) {
    queryParams.value.rowsPerPage = Number(storedSize)
  }

  // get URLs
  await onURLsRequest({ pagination: queryParams.value })
  await getTags()
  console.log(rows.value)
})
</script>

<style lang="sass" scoped>
.items-list-container
  max-width: calc(100vw - 16px)
  width: 100%
</style>
