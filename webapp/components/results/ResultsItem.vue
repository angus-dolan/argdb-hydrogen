<script setup lang="ts">
import {useSearchResultsStore} from "@/stores/searchResults";
const searchResultsStore = useSearchResultsStore();
const selected = computed(() => searchResultsStore.selected);
</script>

<template>
  <div>
    <h3 class="font-semibold capitalize py-4 pb-20">{{selected._source.title}}</h3>
    <ScrollArea class="h-[calc(100vh-25vh)] w-full">
    <div class="w-full" v-for="node in selected._source.nodes">
        <Badge variant="secondary">
          {{ node.id }}
        </Badge>
      <p class="leading-7 text-sm pt-4">{{node.text}}</p>
      <Separator class="my-4" />
    </div>
    </ScrollArea>
  </div>
</template>