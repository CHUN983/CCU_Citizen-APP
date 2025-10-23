# Android 開發完整規劃

## 📋 專案資訊

- **專案名稱**：市民參與城市規劃 APP
- **團隊規模**：7 人（4 人負責 Android）
- **開發時間**：1.5 個月（6 週）
- **技術棧**：Kotlin + Jetpack Compose + MVVM
- **後端 API**：已完成（24+ 端點）

---

## 🎯 Android APP 核心功能

### **必做功能（MVP）**

#### 1. **用戶系統**
- [x] 註冊頁面
- [x] 登入頁面
- [x] 個人資料頁面
- [x] Token 管理

#### 2. **意見瀏覽系統**
- [x] 意見列表（分頁載入）
- [x] 意見詳情頁
- [x] 篩選功能（分類、狀態、地區）
- [x] 搜尋功能

#### 3. **意見發表系統**
- [x] 發表意見表單
- [x] 分類選擇
- [x] 拍照上傳
- [x] 從相簿選圖
- [x] 地圖選位置

#### 4. **互動功能**
- [x] 留言功能
- [x] 投票/按讚
- [x] 收藏功能

#### 5. **通知系統**
- [x] 通知列表
- [x] 標記已讀

### **加分功能（選做）**
- [ ] 推播通知（Firebase Cloud Messaging）
- [ ] 離線模式（草稿儲存）
- [ ] 深色模式
- [ ] 多語言支援

---

## 🏗️ Android 專案架構

### **推薦架構：MVVM + Clean Architecture**

```
app/
├── data/                          # 數據層
│   ├── api/                      # API 介面定義
│   │   ├── ApiService.kt         # Retrofit 介面
│   │   ├── AuthApi.kt            # 認證 API
│   │   ├── OpinionApi.kt         # 意見 API
│   │   └── MediaApi.kt           # 媒體 API
│   ├── model/                    # 數據模型
│   │   ├── User.kt
│   │   ├── Opinion.kt
│   │   ├── Comment.kt
│   │   └── Response.kt
│   ├── repository/               # Repository 實作
│   │   ├── AuthRepository.kt
│   │   ├── OpinionRepository.kt
│   │   └── MediaRepository.kt
│   └── local/                    # 本地儲存
│       ├── PreferenceManager.kt  # SharedPreferences
│       └── TokenManager.kt       # Token 管理
│
├── domain/                        # 業務邏輯層
│   ├── usecase/                  # Use Cases
│   │   ├── auth/
│   │   │   ├── LoginUseCase.kt
│   │   │   └── RegisterUseCase.kt
│   │   ├── opinion/
│   │   │   ├── GetOpinionsUseCase.kt
│   │   │   └── CreateOpinionUseCase.kt
│   │   └── media/
│   │       └── UploadImageUseCase.kt
│   └── model/                    # Domain Models
│
├── ui/                           # UI 層
│   ├── theme/                    # 主題設定
│   │   ├── Color.kt
│   │   ├── Theme.kt
│   │   └── Type.kt
│   ├── components/               # 可重用組件
│   │   ├── OpinionCard.kt
│   │   ├── CommentItem.kt
│   │   └── LoadingIndicator.kt
│   ├── screens/                  # 頁面
│   │   ├── auth/                 # 認證相關頁面
│   │   │   ├── LoginScreen.kt
│   │   │   ├── RegisterScreen.kt
│   │   │   └── LoginViewModel.kt
│   │   ├── home/                 # 首頁
│   │   │   ├── HomeScreen.kt
│   │   │   └── HomeViewModel.kt
│   │   ├── opinion/              # 意見相關
│   │   │   ├── OpinionListScreen.kt
│   │   │   ├── OpinionDetailScreen.kt
│   │   │   ├── CreateOpinionScreen.kt
│   │   │   └── OpinionViewModel.kt
│   │   ├── profile/              # 個人頁面
│   │   │   ├── ProfileScreen.kt
│   │   │   └── ProfileViewModel.kt
│   │   └── notification/         # 通知
│   │       ├── NotificationScreen.kt
│   │       └── NotificationViewModel.kt
│   └── navigation/               # 導航
│       ├── NavGraph.kt
│       └── Screen.kt
│
├── di/                           # 依賴注入 (Hilt)
│   ├── AppModule.kt
│   ├── NetworkModule.kt
│   └── RepositoryModule.kt
│
└── utils/                        # 工具類
    ├── Constants.kt              # 常數定義
    ├── NetworkResult.kt          # 網路結果封裝
    ├── DateUtils.kt              # 日期工具
    └── ImageUtils.kt             # 圖片處理
```

---

## 🛠️ 技術棧詳解

### **核心技術**

#### 1. **Kotlin**
- 現代化 Android 開發語言
- Google 官方推薦
- 簡潔、安全

#### 2. **Jetpack Compose**
- 聲明式 UI 框架
- 取代傳統 XML Layout
- 更快的開發速度
- 更少的程式碼

#### 3. **MVVM 架構**
```
View (Compose UI)
    ↓
ViewModel (業務邏輯)
    ↓
Repository (數據管理)
    ↓
API/Database (數據源)
```

### **主要依賴庫**

```kotlin
// build.gradle.kts (app)

dependencies {
    // 核心 Compose
    implementation("androidx.compose.ui:ui:1.5.4")
    implementation("androidx.compose.material3:material3:1.1.2")
    implementation("androidx.compose.ui:ui-tooling-preview:1.5.4")
    implementation("androidx.activity:activity-compose:1.8.1")

    // 導航
    implementation("androidx.navigation:navigation-compose:2.7.5")

    // ViewModel
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")

    // 網路請求 - Retrofit
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // 依賴注入 - Hilt
    implementation("com.google.dagger:hilt-android:2.48")
    kapt("com.google.dagger:hilt-compiler:2.48")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")

    // 圖片載入 - Coil
    implementation("io.coil-kt:coil-compose:2.5.0")

    // 異步處理 - Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // DataStore (取代 SharedPreferences)
    implementation("androidx.datastore:datastore-preferences:1.0.0")

    // 地圖 - Google Maps
    implementation("com.google.maps.android:maps-compose:4.3.0")
    implementation("com.google.android.gms:play-services-maps:18.2.0")

    // 相機 - CameraX
    implementation("androidx.camera:camera-camera2:1.3.1")
    implementation("androidx.camera:camera-lifecycle:1.3.1")
    implementation("androidx.camera:camera-view:1.3.1")

    // 推播通知 - Firebase
    implementation("com.google.firebase:firebase-messaging:23.4.0")

    // JSON 處理
    implementation("com.google.code.gson:gson:2.10.1")
}
```

---

## 📐 UI/UX 頁面流程

### **頁面導航圖**

```
┌─────────────────┐
│  Splash Screen  │ (啟動頁)
│  (2秒)          │
└────────┬────────┘
         │
         ↓
    有 Token?
    ↙      ↘
  YES      NO
   ↓        ↓
┌──────┐  ┌──────────┐
│ Home │  │  Login   │ (登入頁)
└──────┘  └────┬─────┘
              ↓
         ┌──────────┐
         │ Register │ (註冊頁)
         └──────────┘

=============== 主要頁面 ===============

┌─────────────────────────────────────┐
│          Bottom Navigation           │
│  [首頁] [發表] [通知] [我的]        │
└─────────────────────────────────────┘

1️⃣ 首頁 (Home)
   ├─ 意見列表
   ├─ 篩選/搜尋
   ├─ 點擊 → 意見詳情
   └─ 意見詳情
       ├─ 內容顯示
       ├─ 留言列表
       ├─ 投票/收藏按鈕
       └─ 發表留言

2️⃣ 發表 (Create)
   ├─ 標題輸入
   ├─ 內容輸入
   ├─ 分類選擇
   ├─ 上傳照片
   │   ├─ 拍照
   │   └─ 從相簿選擇
   ├─ 選擇地點（地圖）
   └─ 送出

3️⃣ 通知 (Notification)
   ├─ 通知列表
   └─ 點擊 → 對應意見詳情

4️⃣ 我的 (Profile)
   ├─ 個人資訊
   ├─ 我的意見
   ├─ 我的收藏
   ├─ 設定
   └─ 登出
```

---

## 🎨 UI 設計指南

### **Material 3 Design 配色**

```kotlin
// Color.kt
val Primary = Color(0xFF2196F3)      // 主色：藍色
val Secondary = Color(0xFF4CAF50)     // 次要色：綠色
val Background = Color(0xFFF5F5F5)    // 背景色
val Surface = Color(0xFFFFFFFF)       // 表面色
val Error = Color(0xFFF44336)         // 錯誤色

// 深色模式（選做）
val DarkPrimary = Color(0xFF1976D2)
val DarkBackground = Color(0xFF121212)
```

### **組件設計規範**

#### **意見卡片 (OpinionCard)**
```
┌────────────────────────────────────┐
│ 👤 用戶名   |   🏷️ 交通運輸        │
│ 📅 2024-10-24                      │
├────────────────────────────────────┤
│ 標題：改善公園設施                  │
│                                    │
│ 內容：希望能在公園增加...          │
│                                    │
│ [📷 圖片縮圖]                      │
├────────────────────────────────────┤
│ 👍 128  💬 32  ⭐ 已收藏           │
└────────────────────────────────────┘
```

---

## 📅 6 週開發時程（4 人 Android 團隊）

### **第 1 週：環境建置 + 學習**

**目標**：所有人建立好開發環境，理解基礎概念

| 日期 | 成員 1 | 成員 2 | 成員 3 | 成員 4 |
|------|--------|--------|--------|--------|
| Day 1-2 | 安裝 Android Studio<br/>Kotlin 基礎教學 | 同左 | 同左 | 同左 |
| Day 3-4 | Jetpack Compose 教學<br/>建立專案 | Retrofit API 學習<br/>測試 API | MVVM 架構學習<br/>設計模式 | 導航系統學習<br/>頁面框架 |
| Day 5-7 | 實作登入頁面 UI | 實作 API Service | 實作 Repository | 實作導航框架 |

**交付成果**：
- ✅ Android 專案可以編譯運行
- ✅ 登入頁面 UI 完成
- ✅ API 呼叫框架完成

---

### **第 2 週：認證系統 + 意見列表**

**目標**：完成登入/註冊，可以看到意見列表

| 功能 | 成員 1 | 成員 2 | 成員 3 | 成員 4 |
|------|--------|--------|--------|--------|
| 認證系統 | 登入/註冊 UI | 認證 API 整合 | Token 管理 | 導航流程 |
| 意見列表 | 列表 UI 設計 | 意見 API 整合 | ViewModel 邏輯 | 下拉刷新/分頁 |

**交付成果**：
- ✅ 可以註冊新帳號
- ✅ 可以登入並儲存 Token
- ✅ 可以看到意見列表
- ✅ 可以下拉刷新

---

### **第 3 週：意見詳情 + 互動功能**

**目標**：完成意見詳情頁、留言、投票、收藏

| 功能 | 成員 1 | 成員 2 | 成員 3 | 成員 4 |
|------|--------|--------|--------|--------|
| 意見詳情 | 詳情頁 UI | 詳情 API | ViewModel | 圖片展示 |
| 留言功能 | 留言列表 UI | 留言 API | 發表留言 | 留言分頁 |
| 互動功能 | 投票/收藏 UI | 投票/收藏 API | 狀態管理 | 動畫效果 |

**交付成果**：
- ✅ 可以查看意見詳情
- ✅ 可以發表留言
- ✅ 可以投票/收藏
- ✅ UI 動畫流暢

---

### **第 4 週：發表意見 + 圖片上傳**

**目標**：可以發表新意見，包含照片上傳

| 功能 | 成員 1 | 成員 2 | 成員 3 | 成員 4 |
|------|--------|--------|--------|--------|
| 表單 UI | 輸入表單設計 | 分類選擇器 | 圖片選擇 UI | 地圖選位置 |
| 相機功能 | CameraX 整合 | 拍照邏輯 | 圖片壓縮 | 預覽功能 |
| 上傳功能 | 表單驗證 | 多圖上傳 API | 上傳進度 | 錯誤處理 |

**交付成果**：
- ✅ 可以填寫表單
- ✅ 可以拍照或選圖
- ✅ 可以選擇位置
- ✅ 可以成功發表意見

---

### **第 5 週：個人中心 + 通知 + 優化**

**目標**：完成個人頁面、通知系統、整體優化

| 功能 | 成員 1 | 成員 2 | 成員 3 | 成員 4 |
|------|--------|--------|--------|--------|
| 個人中心 | 個人資料 UI | 我的意見列表 | 我的收藏 | 設定頁面 |
| 通知系統 | 通知列表 UI | 通知 API | 已讀狀態 | 推播（選做）|
| UI 優化 | 全局樣式統一 | 載入動畫 | 錯誤提示 | 空狀態設計 |

**交付成果**：
- ✅ 個人中心完整
- ✅ 通知功能正常
- ✅ UI/UX 優化完成

---

### **第 6 週：測試 + 打包 + 展示準備**

**目標**：全面測試、修復 Bug、準備展示

| 任務 | 成員 1 | 成員 2 | 成員 3 | 成員 4 |
|------|--------|--------|--------|--------|
| Day 36-38 | 功能測試 | 真機測試 | Bug 修復 | 效能優化 |
| Day 39-40 | APK 打包 | 準備展示數據 | 錄製展示影片 | 準備簡報 |
| Day 41-42 | 最後調整 | 展示彩排 | 準備 Q&A | 備用方案 |

**交付成果**：
- ✅ 所有功能測試通過
- ✅ APK 打包成功
- ✅ 展示影片準備好
- ✅ 簡報準備完成

---

## 👥 團隊分工建議

### **成員 1：UI/UX Leader**
- **專長**：頁面設計、組件開發
- **負責**：
  - 所有頁面的 UI 實作
  - 可重用組件開發
  - 動畫效果設計
  - 整體視覺統一

### **成員 2：網路 & API Leader**
- **專長**：網路請求、API 整合
- **負責**：
  - Retrofit 配置
  - 所有 API 介面定義
  - 網路錯誤處理
  - API 測試

### **成員 3：架構 & 邏輯 Leader**
- **專長**：架構設計、業務邏輯
- **負責**：
  - Repository 實作
  - ViewModel 開發
  - 狀態管理
  - 數據流設計

### **成員 4：功能整合 Leader**
- **專長**：功能整合、特殊功能
- **負責**：
  - 相機功能
  - 地圖整合
  - 推播通知
  - 本地儲存

---

## 📚 學習資源

### **第 1 週必讀/必看**

#### **Kotlin 基礎（1-2 天）**
```
🎥 影片教學：
1. Kotlin 入門教學（菜鳥工程師）
   https://www.youtube.com/watch?v=xxx

2. Kotlin for Android Developers
   https://developer.android.com/kotlin

📖 文章：
1. Kotlin 官方文檔（中文）
   https://kotlinlang.org/docs/home.html
```

#### **Jetpack Compose（2-3 天）**
```
🎥 影片教學：
1. Jetpack Compose 完整教學
   https://developer.android.com/courses/jetpack-compose/course

2. Compose 實戰教學（Phillip Lackner）
   https://www.youtube.com/c/PhilippLackner

📖 文章：
1. Compose 官方教學
   https://developer.android.com/jetpack/compose/tutorial
```

#### **MVVM 架構（1 天）**
```
🎥 影片：
1. Android MVVM 架構完整講解
   https://www.youtube.com/watch?v=xxx

📖 文章：
1. Android Architecture Components
   https://developer.android.com/topic/architecture
```

### **推薦練習專案（第 1 週完成）**

```kotlin
// 簡單的 Todo App
// 練習目標：
1. Compose UI 基礎
2. ViewModel 使用
3. State 管理
4. 列表展示

// 參考：
https://github.com/android/compose-samples
```

---

## 🔧 開發工具配置

### **Android Studio 設定**

1. **安裝 Android Studio**
   - 下載：https://developer.android.com/studio
   - 版本：Hedgehog (2023.1.1) 或更新

2. **必裝插件**
   ```
   - Kotlin (預設)
   - Android SDK
   - Gradle
   - Git Integration
   ```

3. **模擬器設定**
   ```
   推薦配置：
   - Device: Pixel 5
   - Android Version: 13 (API 33)
   - RAM: 2048 MB
   ```

### **Git 工作流程**

```bash
# 分支策略
main            # 穩定版本
  ├─ develop   # 開發主分支
       ├─ feature/login       # 成員 1
       ├─ feature/api         # 成員 2
       ├─ feature/viewmodel   # 成員 3
       └─ feature/navigation  # 成員 4

# 工作流程
1. 從 develop 建立 feature 分支
   git checkout -b feature/your-feature develop

2. 開發完成後提交
   git add .
   git commit -m "feat: add login screen"

3. 推送到遠端
   git push origin feature/your-feature

4. 在 GitHub 建立 Pull Request
   feature/your-feature → develop

5. 程式碼審查後合併
   (CI/CD 自動測試通過後)
```

---

## 🎯 API 整合指南

### **API Base URL**
```kotlin
object Constants {
    const val BASE_URL = "http://10.0.2.2:8000/"  // 模擬器
    // const val BASE_URL = "http://localhost:8000/"  // 真機需改為電腦 IP

    const val TIMEOUT = 30L  // 秒
}
```

### **Retrofit 配置範例**

```kotlin
// NetworkModule.kt
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(
        tokenManager: TokenManager
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                tokenManager.getToken()?.let {
                    request.addHeader("Authorization", "Bearer $it")
                }
                chain.proceed(request.build())
            }
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(Constants.TIMEOUT, TimeUnit.SECONDS)
            .readTimeout(Constants.TIMEOUT, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(Constants.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi {
        return retrofit.create(AuthApi::class.java)
    }
}
```

### **API 介面範例**

```kotlin
// AuthApi.kt
interface AuthApi {
    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<User>

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<Token>

    @GET("auth/me")
    suspend fun getCurrentUser(): Response<User>
}

// OpinionApi.kt
interface OpinionApi {
    @GET("opinions")
    suspend fun getOpinions(
        @Query("page") page: Int,
        @Query("page_size") pageSize: Int,
        @Query("category_id") categoryId: Int? = null,
        @Query("status") status: String? = null
    ): Response<OpinionList>

    @GET("opinions/{id}")
    suspend fun getOpinionDetail(@Path("id") id: Int): Response<Opinion>

    @POST("opinions")
    suspend fun createOpinion(@Body request: CreateOpinionRequest): Response<Opinion>

    @POST("opinions/{id}/vote")
    suspend fun voteOpinion(@Path("id") id: Int): Response<Unit>
}
```

---

## ⚠️ 常見問題與解決方案

### **Q1: 模擬器無法連接本機 API？**
```kotlin
// A: 使用特殊 IP
// 模擬器：10.0.2.2 指向本機 localhost
const val BASE_URL = "http://10.0.2.2:8000/"

// 真機測試：使用電腦的區域網路 IP
// 例如：http://192.168.1.100:8000/
```

### **Q2: Compose 預覽不顯示？**
```kotlin
// A: 確保有 @Preview 註解
@Preview(showBackground = true)
@Composable
fun LoginScreenPreview() {
    AppTheme {
        LoginScreen()
    }
}
```

### **Q3: 圖片上傳失敗？**
```kotlin
// A: 檢查 AndroidManifest.xml 權限
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

### **Q4: Token 過期怎麼處理？**
```kotlin
// A: 使用 Interceptor 自動處理
class AuthInterceptor(private val tokenManager: TokenManager) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val response = chain.proceed(chain.request())
        if (response.code == 401) {
            // Token 過期，清除並跳轉登入
            tokenManager.clearToken()
            // 發送事件到 UI 層
        }
        return response
    }
}
```

---

## 📊 進度追蹤與檢查點

### **每週檢查點**

**第 1 週結束**：
- [ ] 所有成員完成環境建置
- [ ] 專案可以編譯運行
- [ ] 登入頁面 UI 完成
- [ ] API 呼叫框架完成

**第 2 週結束**：
- [ ] 可以註冊/登入
- [ ] Token 正常儲存
- [ ] 意見列表顯示正常
- [ ] 下拉刷新功能正常

**第 3 週結束**：
- [ ] 意見詳情頁完成
- [ ] 可以發表留言
- [ ] 投票/收藏功能正常
- [ ] UI 動畫流暢

**第 4 週結束**：
- [ ] 發表意見表單完成
- [ ] 可以拍照/選圖
- [ ] 圖片上傳成功
- [ ] 可以選擇地點

**第 5 週結束**：
- [ ] 個人中心完成
- [ ] 通知系統正常
- [ ] 所有頁面 UI 統一
- [ ] 錯誤處理完善

**第 6 週結束**：
- [ ] 所有功能測試通過
- [ ] APK 打包成功
- [ ] 展示環境準備好
- [ ] 簡報與影片完成

---

## 🎉 展示準備清單

### **功能展示順序**（5-7 分鐘）

```
1. 啟動 APP (10 秒)
   └─ 展示 Splash Screen 與載入

2. 註冊/登入 (30 秒)
   ├─ 展示註冊流程
   └─ 登入並進入首頁

3. 瀏覽意見 (1 分鐘)
   ├─ 下拉刷新
   ├─ 篩選功能
   ├─ 點擊查看詳情
   └─ 投票/收藏

4. 發表留言 (30 秒)
   ├─ 在詳情頁發表留言
   └─ 展示即時更新

5. 發表意見 (2 分鐘) ⭐ 重點
   ├─ 填寫標題與內容
   ├─ 選擇分類
   ├─ 拍照上傳（展示相機功能）
   ├─ 選擇地點（展示地圖）
   └─ 提交成功

6. AI 自動分類 (30 秒) ⭐ 亮點
   └─ 展示後端 AI 自動分類結果

7. 個人中心 (30 秒)
   ├─ 我的意見列表
   ├─ 我的收藏
   └─ 設定

8. 通知系統 (20 秒)
   └─ 展示通知列表

9. 總結 (30 秒)
   └─ 說明技術棧與特色
```

### **展示數據準備**

```bash
# 預先建立：
- 10-15 筆測試意見（不同分類、狀態）
- 5-8 筆測試留言
- 2-3 個測試帳號
- 準備好要拍照的場景

# 測試環境：
- 確保網路穩定
- 後端 API 運行正常
- 手機電量充足
- 螢幕投影測試
```

---

## 📞 支援與資源

### **技術支援**
- **後端 API 文件**：http://localhost:8000/api/docs
- **GitHub 倉庫**：https://github.com/CHUN983/CCU_Citizen-APP
- **CI/CD 監控**：https://github.com/CHUN983/CCU_Citizen-APP/actions

### **學習社群**
- **Android Developers**：https://developer.android.com
- **Kotlin 官方**：https://kotlinlang.org
- **Stack Overflow**：搜尋問題的好地方

### **開發工具**
- **Android Studio**：主要 IDE
- **Postman**：API 測試
- **Figma**：UI 設計參考

---

## 🎯 成功標準

### **技術指標**
- ✅ 所有 MVP 功能完成
- ✅ API 整合正常，錯誤率 < 5%
- ✅ APP 啟動時間 < 3 秒
- ✅ 頁面切換流暢，無卡頓
- ✅ 無嚴重 Bug 或 Crash

### **展示指標**
- ✅ 展示流程順暢
- ✅ 功能正常運作
- ✅ UI 美觀專業
- ✅ 特色功能突出（AI 分類）
- ✅ 老師/評審認可

---

**文件版本**：1.0
**建立日期**：2025-10-24
**維護者**：Android 開發組
**狀態**：規劃階段

---

**下一步行動**：
1. ✅ 閱讀本文件
2. [ ] 第 1 週學習資源開始
3. [ ] 建立 Android 專案
4. [ ] 團隊每日站會（15 分鐘）
