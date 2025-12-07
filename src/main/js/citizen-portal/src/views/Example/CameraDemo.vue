<template>
  <div class="camera-demo-page">
    <el-card class="demo-header">
      <template #header>
        <div class="card-header">
          <h2>📸 相機功能示範</h2>
          <el-tag>Capacitor Camera Plugin</el-tag>
        </div>
      </template>

      <el-space direction="vertical" :size="16" style="width: 100%">
        <el-alert
          title="功能說明"
          type="info"
          :closable="false"
        >
          此示範展示如何在 Citizen Portal APP 中使用相機功能。
          支援拍照、選擇相簿圖片、多圖上傳、圖片壓縮等功能。
        </el-alert>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="平台">
            <el-tag :type="platformType">{{ platformName }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="相機權限">
            <el-tag :type="hasPermission ? 'success' : 'danger'">
              {{ hasPermission ? '已授權' : '未授權' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-space>
    </el-card>

    <!-- 方法 1: 使用 CameraUpload 元件 -->
    <el-card class="demo-section">
      <template #header>
        <h3>方法 1: 使用 CameraUpload 元件 (推薦)</h3>
      </template>

      <CameraUpload
        ref="cameraUploadRef"
        :allow-multiple="allowMultiple"
        :max-images="maxImages"
        :compress="enableCompress"
        :compress-quality="compressQuality"
        @update:images="handleImagesUpdate"
      />

      <el-divider />

      <el-space wrap>
        <el-switch
          v-model="allowMultiple"
          active-text="允許多選"
          inactive-text="單張模式"
        />

        <el-switch
          v-model="enableCompress"
          active-text="啟用壓縮"
          inactive-text="原始大小"
        />

        <div v-if="enableCompress" class="compress-slider">
          <span>壓縮品質:</span>
          <el-slider
            v-model="compressQualityPercent"
            :min="50"
            :max="100"
            :step="10"
            style="width: 150px"
          />
          <span>{{ compressQualityPercent }}%</span>
        </div>

        <el-input-number
          v-model="maxImages"
          :min="1"
          :max="20"
          label="最大數量"
        />
      </el-space>

      <el-divider />

      <el-space>
        <el-button
          type="primary"
          :icon="Upload"
          :disabled="images.length === 0"
          :loading="uploading"
          @click="handleUpload"
        >
          上傳圖片 ({{ images.length }})
        </el-button>

        <el-button
          :icon="Delete"
          :disabled="images.length === 0"
          @click="handleClearImages"
        >
          清空圖片
        </el-button>

        <el-button
          :icon="View"
          :disabled="images.length === 0"
          @click="handleShowImageInfo"
        >
          查看資訊
        </el-button>
      </el-space>
    </el-card>

    <!-- 方法 2: 使用工具函式 -->
    <el-card class="demo-section">
      <template #header>
        <h3>方法 2: 直接使用工具函式</h3>
      </template>

      <el-space wrap>
        <el-button
          type="primary"
          :icon="Camera"
          @click="handleTakePicture('camera')"
        >
          直接拍照
        </el-button>

        <el-button
          type="success"
          :icon="Picture"
          @click="handleTakePicture('gallery')"
        >
          從相簿選擇
        </el-button>

        <el-button
          type="info"
          :icon="FolderOpened"
          @click="handlePickMultiple"
        >
          選擇多張
        </el-button>

        <el-button
          type="warning"
          :icon="Key"
          @click="handleCheckPermission"
        >
          檢查權限
        </el-button>
      </el-space>

      <div v-if="singlePhoto" class="single-photo-preview">
        <el-image
          :src="singlePhoto.dataUrl"
          fit="contain"
          style="max-width: 100%; max-height: 400px"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
              <span>載入失敗</span>
            </div>
          </template>
        </el-image>

        <div class="photo-info">
          <el-tag>格式: {{ singlePhoto.format }}</el-tag>
          <el-tag type="info">大小: {{ formatFileSize(singlePhoto.size) }}</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 圖片資訊對話框 -->
    <el-dialog
      v-model="imageInfoVisible"
      title="圖片詳細資訊"
      width="90%"
      :close-on-click-modal="false"
    >
      <el-table :data="images" stripe>
        <el-table-column type="index" label="#" width="60" />
        <el-table-column label="預覽" width="120">
          <template #default="{ row }">
            <el-image
              :src="row.dataUrl"
              style="width: 80px; height: 80px"
              fit="cover"
            />
          </template>
        </el-table-column>
        <el-table-column prop="format" label="格式" width="100" />
        <el-table-column label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="Base64 長度">
          <template #default="{ row }">
            {{ row.base64.length.toLocaleString() }} 字元
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="imageInfoVisible = false">關閉</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Capacitor } from '@capacitor/core';
import { ElMessage, ElNotification } from 'element-plus';
import {
  Camera,
  Picture,
  Upload,
  Delete,
  View,
  FolderOpened,
  Key
} from '@element-plus/icons-vue';
import CameraUpload from '@/components/CameraUpload.vue';
import {
  takePicture,
  pickImages,
  checkCameraPermission,
  requestCameraPermission,
  compressImage
} from '@/utils/camera';

// Refs
const cameraUploadRef = ref(null);
const images = ref([]);
const singlePhoto = ref(null);
const uploading = ref(false);
const imageInfoVisible = ref(false);
const hasPermission = ref(false);

// Settings
const allowMultiple = ref(true);
const maxImages = ref(10);
const enableCompress = ref(true);
const compressQualityPercent = ref(80);

// Computed
const compressQuality = computed(() => compressQualityPercent.value / 100);

const platformName = computed(() => {
  const platform = Capacitor.getPlatform();
  const names = {
    web: '網頁瀏覽器',
    android: 'Android',
    ios: 'iOS'
  };
  return names[platform] || platform;
});

const platformType = computed(() => {
  const platform = Capacitor.getPlatform();
  const types = {
    web: 'info',
    android: 'success',
    ios: 'primary'
  };
  return types[platform] || 'info';
});

// Methods
function handleImagesUpdate(newImages) {
  images.value = newImages;
  console.log('圖片更新:', newImages);
}

async function handleUpload() {
  if (images.value.length === 0) {
    ElMessage.warning('請先選擇圖片');
    return;
  }

  uploading.value = true;

  try {
    // 模擬上傳到後端
    await new Promise(resolve => setTimeout(resolve, 2000));

    // TODO: 實際上傳邏輯
    // const formData = new FormData();
    // images.value.forEach((img, index) => {
    //   const blob = base64ToBlob(img.base64, `image/${img.format}`);
    //   formData.append('images', blob, `image_${index}.${img.format}`);
    // });
    //
    // await axios.post('/api/upload', formData);

    ElNotification({
      title: '上傳成功',
      message: `已成功上傳 ${images.value.length} 張圖片`,
      type: 'success',
      duration: 3000
    });

    // 清空圖片
    handleClearImages();
  } catch (error) {
    console.error('上傳失敗:', error);
    ElMessage.error('上傳失敗: ' + error.message);
  } finally {
    uploading.value = false;
  }
}

function handleClearImages() {
  if (cameraUploadRef.value) {
    cameraUploadRef.value.clearImages();
  }
  images.value = [];
}

function handleShowImageInfo() {
  imageInfoVisible.value = true;
}

async function handleTakePicture(source) {
  try {
    const photo = await takePicture({
      source,
      quality: 80
    });

    if (enableCompress.value) {
      photo.dataUrl = await compressImage(
        photo.dataUrl,
        1920,
        1920,
        compressQuality.value
      );
      photo.base64 = photo.dataUrl.split(',')[1];
    }

    singlePhoto.value = {
      ...photo,
      size: calculateBase64Size(photo.dataUrl)
    };

    ElMessage.success(source === 'camera' ? '拍照成功' : '選擇圖片成功');
  } catch (error) {
    console.error('操作失敗:', error);
    ElMessage.error(error.message || '操作失敗');
  }
}

async function handlePickMultiple() {
  try {
    const photos = await pickImages({ multiple: true });

    ElNotification({
      title: '選擇成功',
      message: `已選擇 ${photos.length} 張圖片`,
      type: 'success'
    });

    console.log('多張圖片:', photos);
  } catch (error) {
    console.error('選擇失敗:', error);
    ElMessage.error(error.message || '選擇失敗');
  }
}

async function handleCheckPermission() {
  try {
    const granted = await checkCameraPermission();

    if (granted) {
      hasPermission.value = true;
      ElMessage.success('已擁有相機權限');
    } else {
      const requested = await requestCameraPermission();

      if (requested) {
        hasPermission.value = true;
        ElMessage.success('權限授予成功');
      } else {
        hasPermission.value = false;
        ElMessage.error('權限被拒絕');
      }
    }
  } catch (error) {
    console.error('權限檢查失敗:', error);
    ElMessage.error('權限檢查失敗');
  }
}

function calculateBase64Size(base64String) {
  const base64 = base64String.split(',')[1] || base64String;
  return Math.ceil(base64.length * 0.75);
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Lifecycle
checkCameraPermission().then(granted => {
  hasPermission.value = granted;
});
</script>

<style scoped>
.camera-demo-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.demo-header {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}

.demo-section {
  margin-bottom: 20px;
}

.compress-slider {
  display: flex;
  align-items: center;
  gap: 12px;
}

.single-photo-preview {
  margin-top: 20px;
  padding: 20px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  text-align: center;
}

.photo-info {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  gap: 8px;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #c0c4cc;
}

/* 手機版樣式 */
@media (max-width: 768px) {
  .camera-demo-page {
    padding: 12px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .compress-slider {
    flex-direction: column;
    align-items: flex-start;
  }

  .compress-slider .el-slider {
    width: 100% !important;
  }
}
</style>
