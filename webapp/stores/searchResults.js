import { defineStore } from 'pinia'

export const useSearchResultsStore = defineStore('searchResults', {
  state: () => ({
    data: null,
    query: ref(null),
    selected: ref(null),
    elapsedTime: ref(null)
  }),
  actions: {
    setResults(data) {
      console.log('setting results')
      this.data = data;
      console.log(this.data.results[0])
      if (this.data.results.length > 0) {
        this.selected = this.data.results[0];
      }
    },
    setElapsedTime(time) {
      this.elapsedTime = time;
    },
    setSelected(argument) {
      console.log('set selected')
      this.selected = argument
    }
  },
});
