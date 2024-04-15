<template>
  <div>
    <div class="flex flex-col items-center justify-center w-full h-[calc(100vh-3rem)]">
      <SearchBox :large="true" :shadow="'shadow-2xl'" :width="'w-full max-w-xl'"/>
    </div>
    <div class="flex justify-between h-12 px-8">
      <SearchMode/>
      <nav class="space-x-8 hidden">
        <NuxtLink to="/settings" class="inline-flex items-center space-x-2 transition-colors hover:text-foreground/80 text-foreground/60">
          <GearIcon/>
          <span>Settings</span>
        </NuxtLink>
        <NuxtLink to="/settings" class="inline-flex items-center space-x-2 transition-colors hover:text-foreground/80 text-foreground/60">
          <QuestionMarkCircledIcon/>
          <span>Guide</span>
        </NuxtLink>
      </nav>
    </div>
  </div>
</template>


<script setup>
import { GearIcon, StackIcon, QuestionMarkCircledIcon } from '@radix-icons/vue'
import SearchBox from "@/components/SearchBox.vue";
</script>