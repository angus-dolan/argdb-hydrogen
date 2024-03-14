<script setup lang="ts">
import { Label } from "~/components/ui/label";
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Badge } from '~/components/ui/badge'
</script>

<template>
  <RadioGroup default-value="comfortable">
    <div class="flex items-center space-x-2">
      <RadioGroupItem id="r1" value="default" />
      <Label for="r1"><Badge variant="outline" class="text-blue-500">Full Text</Badge></Label>
    </div>
    <div class="flex items-center space-x-2">
      <RadioGroupItem id="r2" value="comfortable" />
      <Label for="r2"><Badge variant="outline" class="text-green-500">Vector</Badge></Label>
    </div>
    <div class="flex items-center space-x-2">
      <RadioGroupItem id="r3" value="compact" />
      <Label for="r3"><Badge variant="outline" class="text-purple-500">Semantic</Badge></Label>
    </div>
    <div class="flex items-center space-x-2">
      <RadioGroupItem id="r4" value="compact" />
      <Label for="r4">
        <Badge variant="outline" class="text-blue-500">Full Text</Badge> +
        <Badge variant="outline" class="text-green-500">Vector</Badge>
      </Label>
    </div>
    <div class="flex items-center space-x-2">
      <RadioGroupItem id="r5" value="compact" />
      <Label for="r5">
        <Badge variant="outline" class="text-blue-500">Full Text</Badge> +
        <Badge variant="outline" class="text-purple-500">Semantic</Badge>
      </Label>
    </div>
  </RadioGroup>
</template>