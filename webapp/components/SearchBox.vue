<script setup lang="ts">
import {Input} from "~/components/ui/input";
import { MagnifyingGlassIcon } from '@radix-icons/vue'
import { useToast } from '@/components/ui/toast/use-toast'

const nuxtConfig = useRuntimeConfig();
const { toast } = useToast();
const query = ref('');

async function search() {
  if (query.value.length === 0) {
    return
  }

  try {
    const response = await $fetch("/handle_search", {
      method: "POST",
      baseURL: nuxtConfig.public.baseURL,
    });
    // console.log(response)
  } catch (error) {
    console.log('shskjisok')
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
  <div class="relative items-center" :class="[width ? width : 'w-full']">
    <Input @keyup.enter="search" v-model="query" id="search" type="text" placeholder="Search..." class="pl-6 bg-white focus-visible:ring-0 rounded-xl" :class="[large ? 'h-14' : '', shadow ? shadow : '']" />
    <div @click="search" class="cursor-pointer absolute end-3 top-3 inset-y-0 flex items-center justify-center rounded-md bg-blue-600 h-8 w-8">
      <MagnifyingGlassIcon class="size-4 text-white" />
    </div>
  </div>
</template>
