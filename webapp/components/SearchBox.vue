<script setup lang="ts">
import {Input} from "~/components/ui/input";
import { MagnifyingGlassIcon } from '@radix-icons/vue'
import { useToast } from '@/components/ui/toast/use-toast'
import { useSearchResultsStore } from '@/stores/searchResults.ts';

const searchResultsStore = useSearchResultsStore();
const nuxtConfig = useRuntimeConfig();
const router = useRouter();
const { toast } = useToast();
const query = computed({
  get: () => searchResultsStore.query,
  set: (value) => {
    searchResultsStore.query = value;
  },
});

async function search() {
  const startTime = performance.now();

  if (query.value.length === 0) {
    return
  }

  const { data, pending, error, refresh } = await useFetch('/', {
    method: 'POST',
    baseURL: nuxtConfig.public.baseURL,
    body: {query: query.value}
  })

  if (data.value) {
    searchResultsStore.setResults(data.value);
    searchResultsStore.setElapsedTime(Math.round(performance.now() - startTime));
    router.push({ path: `/results` });
  }

  if (error.value) {
    toast({
      title: 'Uh oh! something went wrong.',
      description: 'There was a problem with your request',
      variant: 'destructive'
    });
  }
}

defineProps<{
  large?: bool,
  width?: String,
  shadow?: String
}>()
</script>

<template>
  <div class="relative" :class="[width ? width : 'w-full']">
    <div class="absolute inset-y-0 start-0 flex items-center" :class="[large ? 'ps-3' : 'ps-2']">
      <MagnifyingGlassIcon class="size-4" />
    </div>
    <input
      v-model="query"
      @keyup.enter="search"
      type="search"
      :class="[large ? 'rounded-xl p-4 ps-10' : 'rounded-lg p-3 ps-8', shadow ? shadow : '']"
      class="bg-white border border-gray-200 block w-full text-sm text-gray-900 outline-none focus-visible:ring-0" placeholder="Search..."
    />
    <button
      class="text-white absolute  bg-blue-700 hover:bg-blue-800 focus:outline-none focus-visible:ring-0 font-medium rounded-lg px-4 py-2"
      :class="[large ? 'text-sm bottom-2.5 end-2.5' : 'text-xs bottom-1.5 end-2']"
      @click="search"
    >
      Search
    </button>
  </div>
</template>
