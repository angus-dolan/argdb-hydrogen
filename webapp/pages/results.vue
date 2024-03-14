<script setup lang="ts">
import SearchBox from "@/components/SearchBox.vue";
import ResultsList from "@/components/results/ResultsList.vue"
import ResultsFilters from "@/components/results/ResultsFilters.vue"
import ResultsItem from "@/components/results/ResultsItem.vue"
import {useSearchResultsStore} from "@/stores/searchResults"

const searchResultsStore = useSearchResultsStore();
const data = computed(() => searchResultsStore.data);
</script>

<template>
  <div class="grid grid-cols-12 min-h-screen">
    <div class="col-span-2">
      <ResultsFilters class="px-8 pt-32 mt-2"/>
    </div>
    <div class="col-span-5 px-8 flex flex-col gap-2 border-r">
      <div class="py-3">
        <SearchBox shadow="shadow-xl"/>
      </div>
      <p class="text-muted-foreground text-xs py-4">Retrieved {{data.total}} results in {{searchResultsStore.elapsedTime}}ms</p>
      <ResultsList/>
      <p class="text-muted-foreground text-xs py-8">Showing results {{ data.from + 1}}-{{ data.from + data.results.length }} out of {{ data.total }}</p>
    </div>
    <div class="col-span-4 px-8">
      <ResultsItem class="pt-2"/>
    </div>
  </div>
</template>
