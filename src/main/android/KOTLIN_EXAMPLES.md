# Android Kotlin 程式碼範例

本文件提供關鍵功能的實作範例，幫助團隊快速上手。

---

## 📦 1. 資料模型 (Data Models)

### User.kt
```kotlin
package com.citizenapp.data.model

data class User(
    val id: Int,
    val username: String,
    val email: String,
    val full_name: String?,
    val role: String,
    val is_active: Boolean,
    val created_at: String,
    val updated_at: String
)

data class LoginRequest(
    val username: String,
    val password: String
)

data class RegisterRequest(
    val username: String,
    val email: String,
    val password: String,
    val full_name: String?
)

data class Token(
    val access_token: String,
    val token_type: String = "bearer"
)
```

### Opinion.kt
```kotlin
package com.citizenapp.data.model

data class Opinion(
    val id: Int,
    val user_id: Int,
    val title: String,
    val content: String,
    val category_id: Int?,
    val status: OpinionStatus,
    val region: String?,
    val latitude: Double?,
    val longitude: Double?,
    val view_count: Int,
    val vote_count: Int,
    val comment_count: Int,
    val is_public: Boolean,
    val created_at: String,
    val updated_at: String,
    val username: String,
    val user_full_name: String?,
    val media: List<OpinionMedia>?
)

enum class OpinionStatus {
    DRAFT, PENDING, APPROVED, REJECTED, RESOLVED
}

data class OpinionMedia(
    val id: Int,
    val media_type: MediaType,
    val file_path: String,
    val file_size: Int?,
    val mime_type: String?
)

enum class MediaType {
    IMAGE, VIDEO, AUDIO
}

data class OpinionList(
    val total: Int,
    val page: Int,
    val page_size: Int,
    val items: List<Opinion>
)

data class CreateOpinionRequest(
    val title: String,
    val content: String,
    val category_id: Int?,
    val region: String?,
    val latitude: Double?,
    val longitude: Double?,
    val tags: List<String>?
)
```

---

## 🌐 2. API 介面 (Retrofit)

### AuthApi.kt
```kotlin
package com.citizenapp.data.api

import com.citizenapp.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface AuthApi {
    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<User>

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<Token>

    @GET("auth/me")
    suspend fun getCurrentUser(): Response<User>
}
```

### OpinionApi.kt
```kotlin
package com.citizenapp.data.api

import com.citizenapp.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface OpinionApi {
    @GET("opinions")
    suspend fun getOpinions(
        @Query("page") page: Int,
        @Query("page_size") pageSize: Int,
        @Query("category_id") categoryId: Int? = null,
        @Query("status") status: String? = null,
        @Query("region") region: String? = null
    ): Response<OpinionList>

    @GET("opinions/{id}")
    suspend fun getOpinionDetail(@Path("id") id: Int): Response<Opinion>

    @POST("opinions")
    suspend fun createOpinion(@Body request: CreateOpinionRequest): Response<Opinion>

    @POST("opinions/{id}/vote")
    suspend fun voteOpinion(@Path("id") id: Int): Response<Unit>

    @POST("opinions/{id}/collect")
    suspend fun collectOpinion(@Path("id") id: Int): Response<Unit>

    @DELETE("opinions/{id}/collect")
    suspend fun uncollectOpinion(@Path("id") id: Int): Response<Unit>

    @POST("opinions/{id}/comments")
    suspend fun addComment(
        @Path("id") id: Int,
        @Body request: CommentRequest
    ): Response<Comment>
}

data class Comment(
    val id: Int,
    val user_id: Int,
    val content: String,
    val created_at: String,
    val username: String
)

data class CommentRequest(
    val content: String
)
```

### MediaApi.kt
```kotlin
package com.citizenapp.data.api

import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.*

interface MediaApi {
    @Multipart
    @POST("media/upload")
    suspend fun uploadImage(
        @Part file: MultipartBody.Part
    ): Response<MediaUploadResponse>
}

data class MediaUploadResponse(
    val filename: String,
    val media_type: String,
    val file_path: String,
    val file_size: Int,
    val mime_type: String,
    val url: String,
    val thumbnail_url: String?
)
```

---

## 🏗️ 3. Repository (數據管理層)

### AuthRepository.kt
```kotlin
package com.citizenapp.data.repository

import com.citizenapp.data.api.AuthApi
import com.citizenapp.data.model.*
import com.citizenapp.utils.NetworkResult
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import javax.inject.Inject

class AuthRepository @Inject constructor(
    private val authApi: AuthApi
) {
    suspend fun login(username: String, password: String): Flow<NetworkResult<Token>> = flow {
        emit(NetworkResult.Loading())
        try {
            val response = authApi.login(LoginRequest(username, password))
            if (response.isSuccessful && response.body() != null) {
                emit(NetworkResult.Success(response.body()!!))
            } else {
                emit(NetworkResult.Error(response.message() ?: "登入失敗"))
            }
        } catch (e: Exception) {
            emit(NetworkResult.Error(e.message ?: "網路錯誤"))
        }
    }

    suspend fun register(
        username: String,
        email: String,
        password: String,
        fullName: String?
    ): Flow<NetworkResult<User>> = flow {
        emit(NetworkResult.Loading())
        try {
            val response = authApi.register(
                RegisterRequest(username, email, password, fullName)
            )
            if (response.isSuccessful && response.body() != null) {
                emit(NetworkResult.Success(response.body()!!))
            } else {
                emit(NetworkResult.Error(response.message() ?: "註冊失敗"))
            }
        } catch (e: Exception) {
            emit(NetworkResult.Error(e.message ?: "網路錯誤"))
        }
    }

    suspend fun getCurrentUser(): Flow<NetworkResult<User>> = flow {
        emit(NetworkResult.Loading())
        try {
            val response = authApi.getCurrentUser()
            if (response.isSuccessful && response.body() != null) {
                emit(NetworkResult.Success(response.body()!!))
            } else {
                emit(NetworkResult.Error(response.message() ?: "獲取用戶失敗"))
            }
        } catch (e: Exception) {
            emit(NetworkResult.Error(e.message ?: "網路錯誤"))
        }
    }
}
```

---

## 🎭 4. ViewModel (UI 邏輯層)

### LoginViewModel.kt
```kotlin
package com.citizenapp.ui.screens.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.citizenapp.data.local.TokenManager
import com.citizenapp.data.repository.AuthRepository
import com.citizenapp.utils.NetworkResult
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val tokenManager: TokenManager
) : ViewModel() {

    private val _loginState = MutableStateFlow<LoginState>(LoginState.Idle)
    val loginState: StateFlow<LoginState> = _loginState.asStateFlow()

    fun login(username: String, password: String) {
        viewModelScope.launch {
            authRepository.login(username, password).collect { result ->
                when (result) {
                    is NetworkResult.Loading -> {
                        _loginState.value = LoginState.Loading
                    }
                    is NetworkResult.Success -> {
                        tokenManager.saveToken(result.data.access_token)
                        _loginState.value = LoginState.Success
                    }
                    is NetworkResult.Error -> {
                        _loginState.value = LoginState.Error(result.message ?: "登入失敗")
                    }
                }
            }
        }
    }

    fun resetState() {
        _loginState.value = LoginState.Idle
    }
}

sealed class LoginState {
    object Idle : LoginState()
    object Loading : LoginState()
    object Success : LoginState()
    data class Error(val message: String) : LoginState()
}
```

---

## 🎨 5. Compose UI (頁面)

### LoginScreen.kt
```kotlin
package com.citizenapp.ui.screens.auth

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun LoginScreen(
    viewModel: LoginViewModel = hiltViewModel(),
    onLoginSuccess: () -> Unit,
    onNavigateToRegister: () -> Unit
) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    val loginState by viewModel.loginState.collectAsState()

    LaunchedEffect(loginState) {
        when (loginState) {
            is LoginState.Success -> {
                onLoginSuccess()
                viewModel.resetState()
            }
            else -> {}
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "市民參與城市規劃",
            style = MaterialTheme.typography.headlineLarge
        )

        Spacer(modifier = Modifier.height(32.dp))

        OutlinedTextField(
            value = username,
            onValueChange = { username = it },
            label = { Text("帳號") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("密碼") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            visualTransformation = PasswordVisualTransformation()
        )

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = { viewModel.login(username, password) },
            modifier = Modifier.fillMaxWidth(),
            enabled = loginState !is LoginState.Loading
        ) {
            if (loginState is LoginState.Loading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Text("登入")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(onClick = onNavigateToRegister) {
            Text("還沒有帳號？立即註冊")
        }

        // 顯示錯誤訊息
        if (loginState is LoginState.Error) {
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = (loginState as LoginState.Error).message,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodyMedium
            )
        }
    }
}
```

### OpinionListScreen.kt
```kotlin
package com.citizenapp.ui.screens.opinion

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun OpinionListScreen(
    viewModel: OpinionViewModel = hiltViewModel(),
    onOpinionClick: (Int) -> Unit
) {
    val opinionsState by viewModel.opinionsState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadOpinions()
    }

    Column(modifier = Modifier.fillMaxSize()) {
        // 標題列
        TopAppBar(
            title = { Text("意見列表") }
        )

        // 內容
        when (val state = opinionsState) {
            is OpinionListState.Loading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            is OpinionListState.Success -> {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp)
                ) {
                    items(state.opinions) { opinion ->
                        OpinionCard(
                            opinion = opinion,
                            onClick = { onOpinionClick(opinion.id) }
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                }
            }
            is OpinionListState.Error -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = state.message,
                        color = MaterialTheme.colorScheme.error
                    )
                }
            }
            else -> {}
        }
    }
}

@Composable
fun OpinionCard(
    opinion: Opinion,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            // 標題
            Text(
                text = opinion.title,
                style = MaterialTheme.typography.titleMedium
            )

            Spacer(modifier = Modifier.height(8.dp))

            // 內容預覽
            Text(
                text = opinion.content,
                style = MaterialTheme.typography.bodyMedium,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(modifier = Modifier.height(8.dp))

            // 底部資訊
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "by ${opinion.username}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Row {
                    Text(
                        text = "👍 ${opinion.vote_count}",
                        style = MaterialTheme.typography.bodySmall
                    )
                    Spacer(modifier = Modifier.width(16.dp))
                    Text(
                        text = "💬 ${opinion.comment_count}",
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }
    }
}
```

---

## 🔧 6. 依賴注入 (Hilt)

### AppModule.kt
```kotlin
package com.citizenapp.di

import android.content.Context
import com.citizenapp.data.local.TokenManager
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideTokenManager(
        @ApplicationContext context: Context
    ): TokenManager {
        return TokenManager(context)
    }
}
```

### NetworkModule.kt
```kotlin
package com.citizenapp.di

import com.citizenapp.data.api.*
import com.citizenapp.data.local.TokenManager
import com.citizenapp.utils.Constants
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(tokenManager: TokenManager): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                tokenManager.getToken()?.let {
                    request.addHeader("Authorization", "Bearer $it")
                }
                chain.proceed(request.build())
            }
            .addInterceptor(
                HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY
                }
            )
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

    @Provides
    @Singleton
    fun provideOpinionApi(retrofit: Retrofit): OpinionApi {
        return retrofit.create(OpinionApi::class.java)
    }

    @Provides
    @Singleton
    fun provideMediaApi(retrofit: Retrofit): MediaApi {
        return retrofit.create(MediaApi::class.java)
    }
}
```

---

## 🛠️ 7. 工具類

### Constants.kt
```kotlin
package com.citizenapp.utils

object Constants {
    const val BASE_URL = "http://10.0.2.2:8000/"  // 模擬器
    const val TIMEOUT = 30L  // 秒
}
```

### NetworkResult.kt
```kotlin
package com.citizenapp.utils

sealed class NetworkResult<T>(
    val data: T? = null,
    val message: String? = null
) {
    class Loading<T> : NetworkResult<T>()
    class Success<T>(data: T) : NetworkResult<T>(data)
    class Error<T>(message: String, data: T? = null) : NetworkResult<T>(data, message)
}
```

### TokenManager.kt
```kotlin
package com.citizenapp.data.local

import android.content.Context
import android.content.SharedPreferences
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TokenManager @Inject constructor(
    @ApplicationContext context: Context
) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_TOKEN = "access_token"
    }

    fun saveToken(token: String) {
        prefs.edit().putString(KEY_TOKEN, token).apply()
    }

    fun getToken(): String? {
        return prefs.getString(KEY_TOKEN, null)
    }

    fun clearToken() {
        prefs.edit().remove(KEY_TOKEN).apply()
    }

    fun hasToken(): Boolean {
        return getToken() != null
    }
}
```

---

## 📱 8. 導航 (Navigation)

### NavGraph.kt
```kotlin
package com.citizenapp.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.citizenapp.ui.screens.auth.*
import com.citizenapp.ui.screens.opinion.*
import com.citizenapp.ui.screens.home.HomeScreen

@Composable
fun AppNavGraph(
    navController: NavHostController,
    startDestination: String
) {
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        // 認證流程
        composable(Screen.Login.route) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                },
                onNavigateToRegister = {
                    navController.navigate(Screen.Register.route)
                }
            )
        }

        composable(Screen.Register.route) {
            RegisterScreen(
                onRegisterSuccess = {
                    navController.popBackStack()
                },
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }

        // 主要頁面
        composable(Screen.Home.route) {
            HomeScreen(
                onOpinionClick = { opinionId ->
                    navController.navigate(Screen.OpinionDetail.createRoute(opinionId))
                }
            )
        }

        composable(Screen.OpinionDetail.route) { backStackEntry ->
            val opinionId = backStackEntry.arguments?.getString("opinionId")?.toIntOrNull()
            if (opinionId != null) {
                OpinionDetailScreen(
                    opinionId = opinionId,
                    onNavigateBack = { navController.popBackStack() }
                )
            }
        }
    }
}
```

### Screen.kt
```kotlin
package com.citizenapp.ui.navigation

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object Login : Screen("login")
    object Register : Screen("register")
    object Home : Screen("home")
    object OpinionDetail : Screen("opinion/{opinionId}") {
        fun createRoute(opinionId: Int) = "opinion/$opinionId"
    }
    object CreateOpinion : Screen("create_opinion")
    object Profile : Screen("profile")
    object Notification : Screen("notification")
}
```

---

## 📝 9. MainActivity

### MainActivity.kt
```kotlin
package com.citizenapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.rememberNavController
import com.citizenapp.data.local.TokenManager
import com.citizenapp.ui.navigation.AppNavGraph
import com.citizenapp.ui.navigation.Screen
import com.citizenapp.ui.theme.CitizenAppTheme
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var tokenManager: TokenManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            CitizenAppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val navController = rememberNavController()
                    val startDestination = if (tokenManager.hasToken()) {
                        Screen.Home.route
                    } else {
                        Screen.Login.route
                    }

                    AppNavGraph(
                        navController = navController,
                        startDestination = startDestination
                    )
                }
            }
        }
    }
}
```

---

## 🎉 總結

這些範例涵蓋了：
1. ✅ 資料模型定義
2. ✅ API 介面設計
3. ✅ Repository 實作
4. ✅ ViewModel 邏輯
5. ✅ Compose UI 頁面
6. ✅ 依賴注入配置
7. ✅ 工具類
8. ✅ 導航系統
9. ✅ 主活動設定

團隊可以直接複製這些程式碼作為起點！

**下一步**：
1. 建立 Android Studio 專案
2. 複製這些程式碼
3. 配置 Gradle 依賴
4. 開始開發！
