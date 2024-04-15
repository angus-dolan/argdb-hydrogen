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
import { Progress } from '@/components/ui/progress'

const nuxtConfig = useRuntimeConfig();
const searchResultsStore = useSearchResultsStore();
const selectedSearchMode = ref(searchResultsStore.searchMode);
const loading = ref(false);
const progress = ref(0);

async function updateAPI() {
  loading.value = true;
  progress.value = 0;
  const interval = setInterval(() => {
    if (progress.value < 100) {
      progress.value += 1;
    } else {
      clearInterval(interval);
    }
  }, 100);

  const { data, pending, error, refresh } = await useFetch('/search_mode', {
    headers: {'Content-Type': 'application/json'},
    method: 'POST',
    baseURL: `${nuxtConfig.public.baseURL}`,
    body: JSON.stringify({ mode: selectedSearchMode.value })
  });

  clearInterval(interval);
  progress.value = 10;
  loading.value = false;

  if (selectedSearchMode.value === 'fulltext') {
    searchResultsStore.setModeFulltext();
  } else if (selectedSearchMode.value === 'hybrid') {
    searchResultsStore.setModeHybrid();
  }
}

watch(selectedSearchMode, async (newMode, oldMode) => {
  if (newMode === oldMode) return;
  await updateAPI();
});
</script>

<template>
  <div>
    <DropdownMenu>
      <DropdownMenuTrigger as-child>
        <Button variant="ghost" class="capitalize px-0 hover:bg-transparent">
          <span>{{ selectedSearchMode === 'hybrid' ? 'Smart search' : 'Simple search' }}</span>
          <ChevronDownIcon class="ml-2"/>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent class="w-56">
        <DropdownMenuLabel>Search Mode</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuRadioGroup v-model="selectedSearchMode">
          <DropdownMenuRadioItem value="fulltext">
            Simple
          </DropdownMenuRadioItem>
          <DropdownMenuRadioItem value="hybrid">
            Smart
          </DropdownMenuRadioItem>
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
    <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <Progress v-model="progress" class="w-3/5" />
    </div>
  </div>
</template>