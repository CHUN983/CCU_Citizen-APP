/**
 * Media URL Helper
 *
 * 處理媒體 URL 在不同平台（Web/Android/iOS）的路徑問題
 *
 * 問題：
 * - 後端返回相對路徑：/media/thumbnails/xxx.jpg
 * - 網頁：Vite 代理處理，可以正常載入
 * - Android/iOS：相對路徑解析為 http://localhost/media/..., 無法找到資源
 *
 * 解決方案：
 * - 在原生平台，將相對路徑轉換為完整的 API URL
 * - 在網頁平台，保持相對路徑（使用 Vite 代理）
 */

import { Capacitor } from '@capacitor/core'
import axios from '@/api/axios'

/**
 * 獲取媒體文件的完整 URL
 * @param {string} url - 後端返回的 URL（可能是相對路徑或完整 URL）
 * @returns {string} - 完整的可訪問 URL
 */
export function getMediaUrl(url) {
  // 如果 URL 為空，返回佔位圖
  if (!url) {
    return '/placeholder-image.png'
  }

  // 如果已經是完整的 URL（http:// 或 https://），直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }

  // 如果是 base64 圖片，直接返回
  if (url.startsWith('data:')) {
    return url
  }

  // 如果是相對路徑，根據平台處理
  if (Capacitor.isNativePlatform()) {
    // 原生平台（Android/iOS）：轉換為完整 API URL
    const baseURL = axios.defaults.baseURL
    // 確保 baseURL 不以 / 結尾，url 以 / 開頭
    const cleanBaseURL = baseURL.endsWith('/') ? baseURL.slice(0, -1) : baseURL
    const cleanUrl = url.startsWith('/') ? url : `/${url}`
    return `${cleanBaseURL}${cleanUrl}`
  } else {
    // 網頁平台：使用 Vite 代理，需要加上 /api 前綴
    // 如果 url 已經包含 /api，不再添加
    if (url.startsWith('/api/')) {
      return url
    }
    // 否則添加 /api 前綴
    const cleanUrl = url.startsWith('/') ? url : `/${url}`
    return `/api${cleanUrl}`
  }
}

/**
 * 處理意見列表/詳情中的媒體 URL
 * @param {Array} mediaList - 媒體列表
 * @returns {Array} - 處理後的媒體列表
 */
export function processMediaUrls(mediaList) {
  if (!Array.isArray(mediaList)) {
    return []
  }

  return mediaList.map(media => ({
    ...media,
    url: getMediaUrl(media.url),
    thumbnail_url: getMediaUrl(media.thumbnail_url)
  }))
}

/**
 * 處理意見物件中的媒體 URL
 * @param {Object} opinion - 意見物件
 * @returns {Object} - 處理後的意見物件
 */
export function processOpinionMediaUrls(opinion) {
  if (!opinion) {
    return null
  }

  return {
    ...opinion,
    media: processMediaUrls(opinion.media)
  }
}

/**
 * 批量處理意見列表中的媒體 URL
 * @param {Array} opinions - 意見列表
 * @returns {Array} - 處理後的意見列表
 */
export function processOpinionsMediaUrls(opinions) {
  if (!Array.isArray(opinions)) {
    return []
  }

  return opinions.map(processOpinionMediaUrls)
}

export default {
  getMediaUrl,
  processMediaUrls,
  processOpinionMediaUrls,
  processOpinionsMediaUrls
}
