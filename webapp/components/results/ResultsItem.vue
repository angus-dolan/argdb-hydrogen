<script setup lang="ts">
import {useSearchResultsStore} from "@/stores/searchResults";

const searchResultsStore = useSearchResultsStore();
const selected = computed(() => searchResultsStore.selected);
</script>

<template>
  <div>
    <h3 class="font-semibold capitalize py-4">{{selected._source.title}}</h3>
  </div>
</template>