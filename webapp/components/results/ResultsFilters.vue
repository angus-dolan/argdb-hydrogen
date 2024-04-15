<script setup>
import { Slider } from '@/components/ui/slider'

const minArgs = ref(0)
</script>

<template>
  <div class="grid gap-4">
    <div class="p-4 border rounded bg-accent text-sm">
      <h5 class="font-semibold pb-4">Year</h5>
      <RadioGroup default-value="comfortable">
        <div class="flex items-center space-x-2">
          <RadioGroupItem id="r1" value="2019" />
          <Label for="r1">2019</Label>
        </div>
      </RadioGroup>
    </div>
    <div class="p-4 space-y-4 border rounded bg-accent text-sm hidden">
      <h5 class="font-semibold">Min Arguments</h5>
      <Slider
        v-bind="minArgs"
        :default-value="[0]"
        :max="25"
        :min="0"
        :step="1"
      />
      <p class="text-gray-500">{{ minArgs }}</p>
    </div>
  </div>
</template>