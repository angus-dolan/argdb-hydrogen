<script setup lang="ts">
import {
  Pagination,
  PaginationEllipsis,
  PaginationFirst,
  PaginationLast,
  PaginationList,
  PaginationListItem,
  PaginationNext,
  PaginationPrev,
} from '@/components/ui/pagination'
import {
  Button,
} from '@/components/ui/button'
import {useSearchResultsStore} from "@/stores/searchResults"

const searchResultsStore = useSearchResultsStore();
const data = computed(() => searchResultsStore.data);

const ITEMS_PER_PAGE = 5;
const totalItems = computed(() => data.value.total);
const totalPages = computed(() => Math.ceil(totalItems.value / ITEMS_PER_PAGE));
const currentPage = ref(1);
const from = computed(() => (currentPage.value - 1) * ITEMS_PER_PAGE);

const paginationItems = computed(() => {
  let items = [];
  let startPage = Math.max(currentPage.value - 2, 1);
  let endPage = Math.min(startPage + 4, totalPages.value);

  if (startPage > 1) {
    items.push(1);
    if (startPage > 2) {
      items.push('ellipsisLeft');
    }
  }

  for (let i = startPage; i <= endPage; i++) {
    items.push(i);
  }

  if (endPage < totalPages.value) {
    if (endPage < totalPages.value - 1) {
      items.push('ellipsisRight');
    }
    items.push(totalPages.value);
  }

  return items;
});
</script>

<template>
  <div>
    <Pagination :total="totalPages" :sibling-count="1" show-edges v-model:page="currentPage">
      <PaginationList class="flex items-center gap-1">
        <PaginationFirst @click="currentPage = 1" />
        <PaginationPrev @click="currentPage = Math.max(1, currentPage - 1)" />

        <template v-for="(item, index) in paginationItems" :key="index">
          <PaginationListItem v-if="item !== 'ellipsisLeft' && item !== 'ellipsisRight'" :class="{ 'is-active': item === currentPage }" @click="currentPage = item">
            <Button class="w-10 h-10 p-0" :variant="item === currentPage ? 'default' : 'outline'">
              {{ item }}
            </Button>
          </PaginationListItem>
          <PaginationEllipsis v-else :key="index" />
        </template>

        <PaginationNext @click="currentPage = Math.min(totalPages.value, currentPage + 1)" />
        <PaginationLast @click="currentPage = totalPages.value" />
      </PaginationList>
    </Pagination>
  </div>
</template>
