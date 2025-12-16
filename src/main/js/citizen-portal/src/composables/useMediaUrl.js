/**
 * Vue Composable for Media URL Handling
 *
 * 提供 Vue 組件中使用的媒體 URL 處理功能
 */

import { computed } from 'vue'
import { getMediaUrl } from '@/utils/mediaUrl'

/**
 * 在 Vue 組件中使用媒體 URL
 * @returns {Object} - 包含 getMediaUrl 函數的物件
 *
 * @example
 * <script setup>
 * import { useMediaUrl } from '@/composables/useMediaUrl'
 *
 * const { getMediaUrl } = useMediaUrl()
 * const imageUrl = getMediaUrl(opinion.thumbnail_url)
 * </script>
 *
 * <template>
 *   <img :src="getMediaUrl(opinion.thumbnail_url)" />
 * </template>
 */
export function useMediaUrl() {
  return {
    getMediaUrl
  }
}

/**
 * 創建響應式的媒體 URL
 * @param {Ref<string>} urlRef - URL 的響應式引用
 * @returns {ComputedRef<string>} - 處理後的 URL
 *
 * @example
 * <script setup>
 * import { ref } from 'vue'
 * import { useReactiveMediaUrl } from '@/composables/useMediaUrl'
 *
 * const rawUrl = ref('/media/thumbnails/image.jpg')
 * const mediaUrl = useReactiveMediaUrl(rawUrl)
 * </script>
 */
export function useReactiveMediaUrl(urlRef) {
  return computed(() => getMediaUrl(urlRef.value))
}

export default {
  useMediaUrl,
  useReactiveMediaUrl
}
