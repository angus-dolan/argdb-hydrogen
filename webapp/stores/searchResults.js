import { defineStore } from 'pinia'

export const useSearchResultsStore = defineStore('searchResults', {
  state: () => ({
    data: null,
    query: ref(null),
    selected: ref(null),
    elapsedTime: ref(null),
    searchMode: null,
  }),
  actions: {
    setModeFulltext() {
      this.searchMode = 'fulltext';
    },
    setModeHybrid() {
      this.searchMode = 'hybrid';
    },
    setResults(data) {
      this.data = data;
      if (this.data.results.length > 0) {
        this.selected = this.data.results[0];
      }
    },
    setElapsedTime(time) {
      this.elapsedTime = time;
    },
    setSelected(argument) {
      this.selected = argument
    }
  },
});
