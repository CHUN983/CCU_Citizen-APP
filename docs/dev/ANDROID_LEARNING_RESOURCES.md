# Android 學習資源完整指南

## 🎯 學習路徑（推薦順序）

```
第1天     第2-3天        第4-5天       第6-7天        第2週開始
  ↓          ↓             ↓            ↓              ↓
Kotlin   Jetpack      MVVM 架構    Retrofit    開始實戰專案
基礎     Compose       +依賴注入     +網路       建立完整功能
```

---

## 📚 第 1 週學習資源（必讀/必看）

### **Day 1-2: Kotlin 基礎**

#### 🎥 **影片教學（選一）**

1. **Kotlin 快速入門（中文，1-2小時）**
   - [Kotlin 程式設計教學](https://www.youtube.com/watch?v=F9UC9DY-vIU)
   - 涵蓋：變數、函數、類別、Lambda

2. **Kotlin for Beginners（英文，推薦）**
   - [Kotlin Course - Tutorial for Beginners](https://www.youtube.com/watch?v=F9UC9DY-vIU)
   - FreeCodeCamp 出品，品質保證

3. **官方 Kotlin Bootcamp（英文，完整）**
   - [Kotlin Bootcamp for Programmers](https://developer.android.com/courses/kotlin-bootcamp/overview)
   - Google 官方課程

#### 📖 **文章教學**

1. **Kotlin 官方文檔（中文）**
   - https://kotlinlang.org/docs/home.html
   - 查詢語法的最佳參考

2. **Kotlin 中文教學**
   - https://www.runoob.com/kotlin/kotlin-tutorial.html
   - 菜鳥教程，適合新手

#### 💻 **實作練習**

```kotlin
// 練習 1: 基本語法
fun main() {
    val name = "Kotlin"  // 不可變變數
    var age = 10         // 可變變數

    println("Hello, $name!")

    // 條件判斷
    if (age > 5) {
        println("Age is greater than 5")
    }

    // when 表達式（類似 switch）
    when (age) {
        0 -> println("Baby")
        in 1..12 -> println("Child")
        else -> println("Adult")
    }
}

// 練習 2: 函數
fun greet(name: String): String {
    return "Hello, $name!"
}

// 簡化寫法
fun greet2(name: String) = "Hello, $name!"

// 練習 3: 類別與數據類
data class User(
    val id: Int,
    val name: String,
    val email: String
)

fun main() {
    val user = User(1, "John", "john@example.com")
    println(user)  // 自動生成 toString()
}

// 練習 4: Lambda 表達式
fun main() {
    val numbers = listOf(1, 2, 3, 4, 5)

    // filter + map
    val doubled = numbers
        .filter { it > 2 }
        .map { it * 2 }

    println(doubled)  // [6, 8, 10]
}

// 練習 5: 協程基礎
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch {
        delay(1000L)
        println("World!")
    }
    println("Hello,")
}
```

#### ✅ **第 1-2 天檢查點**
- [ ] 理解 val vs var
- [ ] 會寫函數和類別
- [ ] 理解 data class
- [ ] 會用 Lambda 表達式
- [ ] 了解基本協程概念

---

### **Day 3-5: Jetpack Compose**

#### 🎥 **影片教學（選一）**

1. **Jetpack Compose 官方課程（推薦）**
   - [Jetpack Compose Basics](https://developer.android.com/courses/jetpack-compose/course)
   - Google 官方，最權威

2. **Compose 實戰教學（英文）**
   - [Philipp Lackner - Jetpack Compose Playlist](https://www.youtube.com/playlist?list=PLQkwcJG4YTCSpJ2NLhDTHhi6XBNfk9WiC)
   - 實戰導向，很實用

3. **Compose 中文教學**
   - [Jetpack Compose 入門教學](https://www.youtube.com/results?search_query=jetpack+compose+%E4%B8%AD%E6%96%87)
   - 搜尋關鍵字找最新的

#### 📖 **文章教學**

1. **Compose 官方文檔**
   - https://developer.android.com/jetpack/compose
   - 最完整的參考資料

2. **Compose 範例程式碼**
   - https://github.com/android/compose-samples
   - 官方範例集合

#### 💻 **實作練習**

```kotlin
// 練習 1: 基本 Composable
@Composable
fun Greeting(name: String) {
    Text(text = "Hello, $name!")
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    Greeting("Android")
}

// 練習 2: 狀態管理
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}

// 練習 3: 列表
@Composable
fun NameList(names: List<String>) {
    LazyColumn {
        items(names) { name ->
            Text(
                text = name,
                modifier = Modifier.padding(16.dp)
            )
        }
    }
}

// 練習 4: 表單輸入
@Composable
fun LoginForm() {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    Column(modifier = Modifier.padding(16.dp)) {
        OutlinedTextField(
            value = username,
            onValueChange = { username = it },
            label = { Text("Username") }
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation()
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = { /* TODO: Login */ },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Login")
        }
    }
}
```

#### ✅ **第 3-5 天檢查點**
- [ ] 會寫基本 Composable 函數
- [ ] 理解 State 與 remember
- [ ] 會用 LazyColumn 顯示列表
- [ ] 會用 TextField 處理輸入
- [ ] 理解 Modifier 的用法

---

### **Day 6-7: MVVM + Retrofit**

#### 🎥 **影片教學**

1. **MVVM 架構講解**
   - [Android MVVM Architecture](https://www.youtube.com/watch?v=_T4zjIEkGOM)
   - Philipp Lackner

2. **Retrofit 教學**
   - [Retrofit Android Tutorial](https://www.youtube.com/watch?v=t6Sql3WMAnk)
   - 網路請求完整教學

#### 💻 **實作練習**

```kotlin
// 練習 1: ViewModel 基礎
class MainViewModel : ViewModel() {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.value++
    }
}

// 在 Composable 中使用
@Composable
fun CounterScreen(viewModel: MainViewModel = viewModel()) {
    val count by viewModel.count.collectAsState()

    Column {
        Text("Count: $count")
        Button(onClick = { viewModel.increment() }) {
            Text("Increment")
        }
    }
}

// 練習 2: Retrofit API 定義
interface ApiService {
    @GET("users")
    suspend fun getUsers(): Response<List<User>>

    @POST("login")
    suspend fun login(@Body request: LoginRequest): Response<Token>
}

// 練習 3: Repository
class UserRepository(private val api: ApiService) {
    suspend fun getUsers(): Flow<NetworkResult<List<User>>> = flow {
        emit(NetworkResult.Loading())
        try {
            val response = api.getUsers()
            if (response.isSuccessful && response.body() != null) {
                emit(NetworkResult.Success(response.body()!!))
            } else {
                emit(NetworkResult.Error("Error: ${response.message()}"))
            }
        } catch (e: Exception) {
            emit(NetworkResult.Error(e.message ?: "Unknown error"))
        }
    }
}
```

---

## 🎓 進階學習資源

### **Hilt 依賴注入**
- 📖 [Hilt 官方文檔](https://developer.android.com/training/dependency-injection/hilt-android)
- 🎥 [Hilt Tutorial](https://www.youtube.com/watch?v=bbMsuI2p1DQ)

### **Jetpack Navigation**
- 📖 [Navigation 官方文檔](https://developer.android.com/guide/navigation)
- 🎥 [Navigation Compose](https://www.youtube.com/watch?v=glyqjzkc4fk)

### **Coil 圖片載入**
- 📖 [Coil 官方文檔](https://coil-kt.github.io/coil/compose/)

### **Room 本地資料庫（選學）**
- 📖 [Room 官方文檔](https://developer.android.com/training/data-storage/room)

---

## 📱 推薦實作專案（第 1 週完成）

### **專案 1: Todo App**
```
功能：
- 新增/刪除 Todo
- 標記完成
- 列表顯示

學習重點：
- Compose UI
- State 管理
- LazyColumn
```

### **專案 2: 簡單天氣 APP**
```
功能：
- 輸入城市名稱
- 呼叫天氣 API
- 顯示天氣資訊

學習重點：
- Retrofit 網路請求
- ViewModel + Repository
- 錯誤處理
```

---

## 🛠️ 開發工具教學

### **Android Studio**
- 🎥 [Android Studio 基礎操作](https://www.youtube.com/watch?v=fis26HvvDII)
- 📖 [官方使用指南](https://developer.android.com/studio/intro)

### **Gradle**
- 📖 [Gradle 構建基礎](https://developer.android.com/studio/build)

### **Git 工作流程**
- 🎥 [Git 與 GitHub 教學](https://www.youtube.com/watch?v=SWYqp7iY_Tc)
- 📖 [Git 基礎教學](https://git-scm.com/book/zh-tw/v2)

---

## 📚 推薦書籍（選讀）

1. **《Kotlin 程式設計》**
   - 適合：初學者
   - 中文書籍

2. **《Android 開發藝術探索》**
   - 適合：進階學習
   - 深入理解 Android

3. **《Jetpack Compose 實戰》**
   - 適合：Compose 深入學習

---

## 🌐 社群資源

### **問題求助**
1. **Stack Overflow**
   - https://stackoverflow.com/questions/tagged/android
   - 搜尋你的錯誤訊息

2. **GitHub Discussions**
   - 各大開源專案的討論區

3. **Reddit**
   - r/androiddev
   - 英文社群，很活躍

### **中文社群**
1. **CSDN**
   - https://www.csdn.net/
   - 中文技術文章

2. **掘金**
   - https://juejin.cn/
   - 高質量中文技術社群

---

## 🎯 學習檢查表（第 1 週結束前）

### **Kotlin 基礎**
- [ ] 變數宣告（val, var）
- [ ] 函數定義
- [ ] 類別與數據類
- [ ] Lambda 表達式
- [ ] 協程基礎

### **Jetpack Compose**
- [ ] 基本 Composable
- [ ] State 管理
- [ ] LazyColumn 列表
- [ ] TextField 輸入
- [ ] Navigation 導航

### **MVVM 架構**
- [ ] ViewModel 概念
- [ ] Repository 模式
- [ ] StateFlow/LiveData
- [ ] 依賴注入基礎

### **Retrofit 網路**
- [ ] API 介面定義
- [ ] 網路請求發送
- [ ] 錯誤處理
- [ ] 結果封裝

### **開發工具**
- [ ] Android Studio 熟練使用
- [ ] 模擬器運行
- [ ] Logcat 查看日誌
- [ ] Git 基本操作

---

## 💡 學習建議

### **時間安排**
```
每天 2 小時學習：
- 1 小時：看影片/讀文章
- 1 小時：實作練習

重點：
- 不要只看不做
- 遇到問題立即搜尋
- 做筆記整理
```

### **學習策略**
1. **快速瀏覽**：先看一遍了解全貌
2. **重點深入**：針對不懂的部分深入學習
3. **立即實作**：學完馬上寫程式碼
4. **問題記錄**：遇到的問題記下來
5. **定期複習**：每天複習前一天的內容

### **常見錯誤**
❌ **錯誤做法**：
- 只看影片不寫程式碼
- 遇到問題就放棄
- 想一次學會所有內容

✅ **正確做法**：
- 邊學邊做
- 遇到問題搜尋解決
- 循序漸進，專注當前階段

---

## 🆘 遇到問題怎麼辦？

### **步驟 1: 仔細閱讀錯誤訊息**
```
例如：
Error: Unresolved reference: Button

解決：
- 檢查 import 是否正確
- 是否少了依賴套件
```

### **步驟 2: Google 搜尋**
```
搜尋技巧：
- 複製完整錯誤訊息
- 加上 "android" 關鍵字
- 查看 Stack Overflow 結果
```

### **步驟 3: 查看官方文檔**
```
Android Developer:
https://developer.android.com
```

### **步驟 4: 詢問團隊成員**
```
在團隊群組中提問：
1. 描述問題
2. 貼上錯誤訊息
3. 說明已嘗試的解決方法
```

---

## 🎉 激勵與鼓勵

### **第 1 週目標**
- 不要求完美掌握
- 重點是建立基礎概念
- 能寫出簡單的 APP 即可

### **記住**
- 每個人都是從初學者開始
- 錯誤是學習的一部分
- 堅持就能成功

### **團隊力量**
- 4 個人一起學習
- 互相幫助解決問題
- 共同進步

---

## 📅 每日學習計畫（範例）

### **第 1 天**
- 09:00-10:00：看 Kotlin 基礎影片
- 10:00-11:00：實作 Kotlin 練習 1-3

### **第 2 天**
- 09:00-10:00：繼續 Kotlin 學習
- 10:00-11:00：實作 Kotlin 練習 4-5

### **第 3 天**
- 09:00-10:00：Jetpack Compose 影片
- 10:00-11:00：實作 Compose 練習 1-2

### **第 4 天**
- 09:00-10:00：繼續 Compose 學習
- 10:00-11:00：實作 Compose 練習 3-4

### **第 5 天**
- 09:00-10:00：MVVM 架構學習
- 10:00-11:00：實作 ViewModel 範例

### **第 6 天**
- 09:00-10:00：Retrofit 網路請求
- 10:00-11:00：實作 API 呼叫

### **第 7 天**
- 09:00-10:00：整合練習
- 10:00-11:00：建立 Todo APP

---

**祝學習順利！加油！** 🚀

**有任何問題隨時在團隊群組中提問！**
