<template>
  <div class="camera-upload">
    <!-- 上傳按鈕區域 -->
    <div class="upload-actions">
      <el-button
        type="primary"
        :icon="Camera"
        @click="handleTakePicture"
        :loading="loading"
      >
        拍照
      </el-button>

      <el-button
        type="success"
        :icon="Picture"
        @click="handlePickFromGallery"
        :loading="loading"
      >
        從相簿選擇
      </el-button>

      <el-button
        v-if="allowMultiple"
        type="info"
        :icon="FolderOpened"
        @click="handlePickMultiple"
        :loading="loading"
      >
        選擇多張
      </el-button>
    </div>

    <!-- 圖片預覽區域 -->
    <div class="image-preview-container" v-if="images.length > 0">
      <div
        v-for="(image, index) in images"
        :key="index"
        class="image-preview-item"
      >
        <el-image
          :src="image.dataUrl"
          :preview-src-list="previewList"
          :initial-index="index"
          fit="cover"
          class="preview-image"
        >
          <template #error>
            <div class="image-error">
              <el-icon><PictureFilled /></el-icon>
              <span>載入失敗</span>
            </div>
          </template>
        </el-image>

        <div class="image-actions">
          <el-button
            type="danger"
            size="small"
            :icon="Delete"
            circle
            @click="handleRemoveImage(index)"
          />
        </div>

        <div class="image-info">
          <el-tag size="small">{{ image.format }}</el-tag>
          <el-tag size="small" type="info">{{ formatFileSize(image.size) }}</el-tag>
        </div>
      </div>
    </div>

    <!-- 空狀態 -->
    <el-empty
      v-else
      description="尚未選擇圖片"
      :image-size="120"
    />

    <!-- 上傳進度 -->
    <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
      <el-progress
        :percentage="uploadProgress"
        :status="uploadProgress === 100 ? 'success' : ''"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Camera,
  Picture,
  Delete,
  FolderOpened,
  PictureFilled
} from '@element-plus/icons-vue';
import {
  takePicture,
  pickImages,
  checkCameraPermission,
  requestCameraPermission,
  compressImage
} from '@/utils/camera';

// Props
const props = defineProps({
  allowMultiple: {
    type: Boolean,
    default: false
  },
  maxImages: {
    type: Number,
    default: 10
  },
  maxFileSize: {
    type: Number,
    default: 5 * 1024 * 1024 // 5MB
  },
  compress: {
    type: Boolean,
    default: true
  },
  compressQuality: {
    type: Number,
    default: 0.8
  }
});

// Emits
const emit = defineEmits(['update:images', 'upload']);

// State
const images = ref([]);
const loading = ref(false);
const uploadProgress = ref(0);

// Computed
const previewList = computed(() => images.value.map(img => img.dataUrl));

// Methods
async function handleTakePicture() {
  try {
    // 檢查權限
    const hasPermission = await checkCameraPermission();
    if (!hasPermission) {
      const granted = await requestCameraPermission();
      if (!granted) {
        ElMessage.error('需要相機權限才能拍照');
        return;
      }
    }

    loading.value = true;

    const photo = await takePicture({ source: 'camera' });

    // 壓縮圖片
    let finalBase64 = photo.dataUrl;
    if (props.compress) {
      finalBase64 = await compressImage(photo.dataUrl, 1920, 1920, props.compressQuality);
    }

    await addImage({
      dataUrl: finalBase64,
      base64: finalBase64.split(',')[1],
      format: photo.format,
      size: calculateBase64Size(finalBase64)
    });

    ElMessage.success('拍照成功');
  } catch (error) {
    console.error('Take picture error:', error);
    ElMessage.error(error.message || '拍照失敗');
  } finally {
    loading.value = false;
  }
}

async function handlePickFromGallery() {
  try {
    loading.value = true;

    const photo = await takePicture({ source: 'gallery' });

    // 壓縮圖片
    let finalBase64 = photo.dataUrl;
    if (props.compress) {
      finalBase64 = await compressImage(photo.dataUrl, 1920, 1920, props.compressQuality);
    }

    await addImage({
      dataUrl: finalBase64,
      base64: finalBase64.split(',')[1],
      format: photo.format,
      size: calculateBase64Size(finalBase64)
    });

    ElMessage.success('選擇圖片成功');
  } catch (error) {
    console.error('Pick from gallery error:', error);
    ElMessage.error(error.message || '選擇圖片失敗');
  } finally {
    loading.value = false;
  }
}

async function handlePickMultiple() {
  try {
    loading.value = true;

    const photos = await pickImages({ multiple: true });

    for (const photo of photos) {
      if (images.value.length >= props.maxImages) {
        ElMessage.warning(`最多只能選擇 ${props.maxImages} 張圖片`);
        break;
      }

      // 壓縮圖片
      let finalBase64 = photo.dataUrl;
      if (props.compress) {
        finalBase64 = await compressImage(photo.dataUrl, 1920, 1920, props.compressQuality);
      }

      await addImage({
        dataUrl: finalBase64,
        base64: finalBase64.split(',')[1],
        format: photo.format,
        size: calculateBase64Size(finalBase64)
      });
    }

    ElMessage.success(`成功選擇 ${photos.length} 張圖片`);
  } catch (error) {
    console.error('Pick multiple error:', error);
    ElMessage.error(error.message || '選擇圖片失敗');
  } finally {
    loading.value = false;
  }
}

async function addImage(imageData) {
  // 檢查檔案大小
  if (imageData.size > props.maxFileSize) {
    ElMessage.error(`圖片大小超過限制 (${formatFileSize(props.maxFileSize)})`);
    return;
  }

  // 檢查數量限制
  if (!props.allowMultiple && images.value.length >= 1) {
    images.value = []; // 單張模式,替換現有圖片
  }

  if (images.value.length >= props.maxImages) {
    ElMessage.warning(`最多只能上傳 ${props.maxImages} 張圖片`);
    return;
  }

  images.value.push(imageData);
  emit('update:images', images.value);
}

function handleRemoveImage(index) {
  images.value.splice(index, 1);
  emit('update:images', images.value);
  ElMessage.info('已移除圖片');
}

function calculateBase64Size(base64String) {
  const base64 = base64String.split(',')[1] || base64String;
  return Math.ceil(base64.length * 0.75);
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Expose methods
defineExpose({
  images,
  clearImages: () => {
    images.value = [];
    emit('update:images', []);
  }
});
</script>

<style scoped>
.camera-upload {
  width: 100%;
}

.upload-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.image-preview-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.image-preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e4e7ed;
  background: #f5f7fa;
}

.preview-image {
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #c0c4cc;
}

.image-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-preview-item:hover .image-actions {
  opacity: 1;
}

.image-info {
  position: absolute;
  bottom: 8px;
  left: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-preview-item:hover .image-info {
  opacity: 1;
}

.upload-progress {
  margin-top: 20px;
}

/* 手機版樣式 */
@media (max-width: 768px) {
  .upload-actions {
    justify-content: center;
  }

  .upload-actions .el-button {
    flex: 1;
    min-width: 100px;
  }

  .image-preview-container {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 12px;
  }
}
</style>
