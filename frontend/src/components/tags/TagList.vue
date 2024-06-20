<template>
  <div class="flex wrap q-gutter-sm">
    <template v-for="(tag, index) in mappedTags" :key="index">
      <!-- v-show="tag.isShow" -->
      <q-chip
        :style="`background-color: ${tag.selected ? getCssVar('primary') : changeAlpha(getCssVar('primary'), 0.6)}`"
        text-color="white"
        :label="tag.name"
        :removable="removable"
        :clickable="clickable"
        @click="click(tag)"
        @remove="deleteTag(tag)"
      />
    </template>
    <!-- TODO: Add tag output in one line with removing unnecessary ones under dropdown -->
    <!-- <q-btn-dropdown
      v-if="hiddenTags.length"
      class="q-mb-xs"
      color="primary"
      dropdown-icon="more_horiz"
      size="sm"
      rounded
      unelevated
    >
      <q-list>
        <template v-for="(tag, index) in hiddenTags" :key="index">
          <q-item>
            <q-item-section>
              <div>
                <q-chip
                  :style="`background-color: ${tag.selected ? getCssVar('primary') : changeAlpha(getCssVar('primary'), 0.6)}`"
                  text-color="white"
                  :label="tag.name"
                  :removable="removable"
                  :clickable="clickable"
                  @click="click(tag)"
                  @remove="deleteTag(tag)"
                />
              </div>
            </q-item-section>
          </q-item>
        </template>
      </q-list>
    </q-btn-dropdown> -->
  </div>
</template>

<script setup>
import { /* ref, */ computed } from 'vue'
import { colors, getCssVar } from 'quasar'
const { changeAlpha } = colors

const props = defineProps({
  tags: {
    type: Array,
    default () {
      return []
    }
  },
  selectedTags: {
    type: Array,
    default () {
      return []
    }
  },
  // TODO: Add tag output in one line with removing unnecessary ones under dropdown
  // oneLine: {
  //   type: Boolean,
  //   default () {
  //     return false
  //   }
  // },
  clickable: {
    type: Boolean,
    default () {
      return false
    }
  },
  removable: {
    type: Boolean,
    default () {
      return false
    }
  }
})

const emit = defineEmits(['remove', 'click'])

const deleteTag = (tag) => {
  emit('remove', tag)
}

const click = (tag) => {
  emit('click', tag)
}

// TODO: Add tag output in one line with removing unnecessary ones under dropdown
// const hiddenTags = ref([])
const mappedTags = computed(() => {
  return props.tags.map((tag, index) => {
    if (props.selectedTags?.findIndex((i) => i.id === tag.id) === -1) {
      tag.selected = false
    } else {
      tag.selected = true
    }

    // TODO: Add tag output in one line with removing unnecessary ones under dropdown
    // if (props.oneLine) {
    //   if (index < 2) {
    //     tag.isShow = true
    //   } else {
    //     tag.isShow = false

    //     hiddenTags.value.push(tag)
    //   }
    // } else {
    //   tag.isShow = true
    // }

    return tag
  })
})
</script>
