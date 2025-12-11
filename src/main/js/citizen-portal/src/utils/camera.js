/**
 * Capacitor Camera Utility
 * 提供相機拍照和相片選擇功能
 */

import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Filesystem, Directory } from '@capacitor/filesystem';

/**
 * 拍照或從相簿選擇圖片
 * @param {Object} options - 選項
 * @param {String} options.source - 'camera' | 'gallery' | 'prompt'
 * @param {Number} options.quality - 圖片品質 0-100
 * @param {Number} options.width - 最大寬度
 * @param {Number} options.height - 最大高度
 * @returns {Promise<Object>} 包含 base64, webPath, format 的物件
 */
export async function takePicture(options = {}) {
  const {
    source = CameraSource.Prompt, // 預設讓使用者選擇
    quality = 80,
    width = 1920,
    height = 1920,
  } = options;

  try {
    const image = await Camera.getPhoto({
      quality,
      allowEditing: false,
      resultType: CameraResultType.Base64,
      source: getCameraSource(source),
      width,
      height,
    });

    return {
      base64: image.base64String,
      format: image.format,
      dataUrl: `data:image/${image.format};base64,${image.base64String}`,
    };
  } catch (error) {
    console.error('Camera error:', error);
    throw new Error('無法取得照片: ' + error.message);
  }
}

/**
 * 從相簿選擇多張圖片 (僅限 Web)
 * @param {Object} options - 選項
 * @param {Number} options.quality - 圖片品質 0-100
 * @param {Boolean} options.multiple - 是否允許多選
 * @returns {Promise<Array>} 圖片陣列
 */
export async function pickImages(options = {}) {
  const { quality = 80, multiple = false } = options;

  try {
    const images = await Camera.pickImages({
      quality,
      limit: multiple ? 10 : 1,
    });

    return await Promise.all(
      images.photos.map(async (photo) => {
        // 讀取圖片並轉換為 base64
        const file = await fetch(photo.webPath);
        const blob = await file.blob();
        const base64 = await blobToBase64(blob);

        return {
          base64: base64.split(',')[1],
          format: photo.format,
          dataUrl: base64,
          webPath: photo.webPath,
        };
      })
    );
  } catch (error) {
    console.error('Pick images error:', error);
    throw new Error('無法選擇圖片: ' + error.message);
  }
}

/**
 * 儲存圖片到裝置
 * @param {String} base64Data - Base64 圖片資料
 * @param {String} fileName - 檔案名稱
 * @returns {Promise<String>} 儲存的檔案路徑
 */
export async function saveImage(base64Data, fileName = `image_${Date.now()}.jpg`) {
  try {
    const savedFile = await Filesystem.writeFile({
      path: fileName,
      data: base64Data,
      directory: Directory.Data,
    });

    return savedFile.uri;
  } catch (error) {
    console.error('Save image error:', error);
    throw new Error('無法儲存圖片: ' + error.message);
  }
}

/**
 * 讀取已儲存的圖片
 * @param {String} filePath - 檔案路徑
 * @returns {Promise<String>} Base64 圖片資料
 */
export async function readImage(filePath) {
  try {
    const contents = await Filesystem.readFile({
      path: filePath,
      directory: Directory.Data,
    });

    return contents.data;
  } catch (error) {
    console.error('Read image error:', error);
    throw new Error('無法讀取圖片: ' + error.message);
  }
}

/**
 * 刪除圖片
 * @param {String} filePath - 檔案路徑
 * @returns {Promise<void>}
 */
export async function deleteImage(filePath) {
  try {
    await Filesystem.deleteFile({
      path: filePath,
      directory: Directory.Data,
    });
  } catch (error) {
    console.error('Delete image error:', error);
    throw new Error('無法刪除圖片: ' + error.message);
  }
}

/**
 * 檢查相機權限
 * @returns {Promise<Boolean>}
 */
export async function checkCameraPermission() {
  try {
    const permission = await Camera.checkPermissions();
    return permission.camera === 'granted' && permission.photos === 'granted';
  } catch (error) {
    console.error('Check permission error:', error);
    return false;
  }
}

/**
 * 請求相機權限
 * @returns {Promise<Boolean>}
 */
export async function requestCameraPermission() {
  try {
    const permission = await Camera.requestPermissions();
    return permission.camera === 'granted' && permission.photos === 'granted';
  } catch (error) {
    console.error('Request permission error:', error);
    return false;
  }
}

// ==================== Helper Functions ====================

function getCameraSource(source) {
  const sourceMap = {
    camera: CameraSource.Camera,
    gallery: CameraSource.Photos,
    prompt: CameraSource.Prompt,
  };
  return sourceMap[source] || CameraSource.Prompt;
}

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

/**
 * 壓縮圖片 (額外功能)
 * @param {String} base64 - Base64 圖片資料
 * @param {Number} maxWidth - 最大寬度
 * @param {Number} maxHeight - 最大高度
 * @param {Number} quality - 品質 0-1
 * @returns {Promise<String>} 壓縮後的 base64
 */
export async function compressImage(base64, maxWidth = 1920, maxHeight = 1920, quality = 0.8) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      let width = img.width;
      let height = img.height;

      // 計算縮放比例
      if (width > height) {
        if (width > maxWidth) {
          height *= maxWidth / width;
          width = maxWidth;
        }
      } else {
        if (height > maxHeight) {
          width *= maxHeight / height;
          height = maxHeight;
        }
      }

      canvas.width = width;
      canvas.height = height;

      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, width, height);

      resolve(canvas.toDataURL('image/jpeg', quality));
    };
    img.onerror = reject;
    img.src = base64.startsWith('data:') ? base64 : `data:image/jpeg;base64,${base64}`;
  });
}
