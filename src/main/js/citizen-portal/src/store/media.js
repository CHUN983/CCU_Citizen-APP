import { defineStore } from 'pinia'
import { mediaAPI } from '../api'

export const useMediaStore = defineStore('media', {
  state: () => ({
    uploading: false
  }),

  actions: {
    async uploadFile(file) {
      this.uploading = true
      try {
        const data = await mediaAPI.upload(file)
        return data
      } finally {
        this.uploading = false
      }
    },

    async uploadMultiple(files) {
      this.uploading = true
      try {
        const data = await mediaAPI.uploadMultiple(files)
        console.log('Uploaded media data:', data)
        return data
      } finally {
        this.uploading = false
      }
    }
  }
})