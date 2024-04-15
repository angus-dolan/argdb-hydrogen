<script lang="ts" setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useSearchResultsStore } from '@/stores/searchResults';
import { ChevronDownIcon } from '@radix-icons/vue'

const searchResultsStore = useSearchResultsStore();
const position = ref('bottom')
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" class="capitalize px-0 hover:bg-transparent">
        <span v-if="searchResultsStore.searchMode == 'hybrid'">Smart search</span>
        <span v-if="searchResultsStore.searchMode == 'fulltext'">Simple search</span>
        <ChevronDownIcon class="ml-2"/>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent class="w-56">
      <DropdownMenuLabel>Search Mode</DropdownMenuLabel>
      <DropdownMenuSeparator />
      <DropdownMenuRadioGroup v-model="position">
        <DropdownMenuRadioItem value="top">
          Simple
        </DropdownMenuRadioItem>
        <DropdownMenuRadioItem value="bottom">
          Smart
        </DropdownMenuRadioItem>
      </DropdownMenuRadioGroup>
    </DropdownMenuContent>
  </DropdownMenu>
</template>