<script setup>
import {cn} from "@/lib/utils.ts";
import {formatDistanceToNow} from "date-fns";
import {useSearchResultsStore} from "@/stores/searchResults.ts";

const searchResultsStore = useSearchResultsStore();
const data = computed(() => searchResultsStore.data);
</script>

<template>
  <TransitionGroup name="list" appear>
    <button
      v-for="result of data.results"
      :key="result._id"
      :class="cn(
  'flex flex-col items-start gap-2 rounded-lg border p-3 text-left text-sm transition-all hover:bg-accent',
        searchResultsStore.selected._id === result._id && 'bg-muted',
      )"
      class="flex flex-col items-start gap-2 rounded-lg border p-3 text-left text-sm transition-all hover:bg-accent"
      @click="searchResultsStore.setSelected(result)"
    >
      <div class="flex w-full flex-col gap-1">
        <div class="flex items-center">
          <div class="flex-1 items-center gap-2">
            <div class="font-semibold">
              {{ result._source.title.substring(0, 200) }}
            </div>
          </div>
          <div
            :class="cn(
              'flex-none ml-auto text-xs',
              selectedArgument === result._id
                ? 'text-foreground'
                : 'text-muted-foreground',
            )"
          >
            {{ formatDistanceToNow(new Date(result._source.created), { addSuffix: true }) }}
          </div>
        </div>

        <div class="text-xs font-medium">
          {{ result._score }}
        </div>
      </div>
      <div class="line-clamp-2 text-xs text-muted-foreground">
        {{ result._source.nodes[0].text.substring(0, 300) }}
      </div>
      <div class="flex items-center gap-2">
        <Badge>Argsme</Badge><Badge variant="secondary">{{result._source.nodes.length}} Arguments</Badge>
      </div>
    </button>
  </TransitionGroup>
</template>