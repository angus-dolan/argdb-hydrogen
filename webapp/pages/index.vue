<template>
  <div>
    <Menubar class="rounded-none border-b border-gray-100 h-12">
      <div class="flex w-full items-center justify-between px-8 text-sm font-medium">
        <nav class="flex space-x-6">
          <h5 class="font-bold pr-4">Hydrogen</h5>
          <NuxtLink to="/data" class="inline-flex items-center space-x-2 transition-colors hover:text-foreground/80 text-foreground/60">
            <StackIcon/>
            <span>Data</span>
          </NuxtLink>
          <NuxtLink to="/settings" class="inline-flex items-center space-x-2 transition-colors hover:text-foreground/80 text-foreground/60">
            <GearIcon/>
            <span>Settings</span>
          </NuxtLink>
        </nav>
        <NuxtLink to="/settings" class="inline-flex items-center space-x-2 transition-colors hover:text-foreground/80 text-foreground/60">
          <QuestionMarkCircledIcon/>
          <span>Guide</span>
        </NuxtLink>
      </div>
    </Menubar>
    <div class="flex flex-col items-center justify-center w-full h-[calc(100vh-3rem)]">
      <SearchBox :large="true" :shadow="'shadow-2xl'" :width="'w-full max-w-xl'"/>
    </div>
  </div>
</template>


<script setup>
import { GearIcon, StackIcon, QuestionMarkCircledIcon } from '@radix-icons/vue'
import {Menubar} from "@/components/ui/menubar";
import SearchBox from "@/components/SearchBox.vue";
</script>