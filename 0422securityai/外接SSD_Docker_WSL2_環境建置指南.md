# 外接式 SSD + Docker/WSL2 本機訓練環境建置指南
## 視覺化網路攻擊自動化分析平台 — 開發環境篇

> 目標：在**不弄髒本機 C 槽、可隨時砍掉重建、資料與模型都放在外接 SSD** 的前提下，
> 建置一套能跑 n8n、Django、AI 訓練（PyTorch + CUDA）的完整開發環境。

---

## /*/. 開啟/關閉/other

### 1.開啟

### 2.關閉



### 實際存放路徑
目前這個環境裡,幾個重要檔案/資料夾的實際存放路徑

方式一:在終端機裡直接用指令看(適合看文字內容、改設定)
'''
bash
cd ~/ai-cyber-project
cat .env                    # 看內容
nano .env                   # 編輯
ls -la n8n_data              # 看 n8n 資料夾裡有什麼

方式二:在 Windows 檔案總管用滑鼠看(適合看整體結構、拖拉檔案)
=>直接在檔案總管網址列貼上:
\\wsl$\cyber-ai-dev\home\incent\ai-cyber-project

---

## 0. 先建立一個心裡的架構圖

在動手之前，先搞懂「東西分別放在哪裡」這件事最重要，之後所有設計都是為了服務這張圖：

```
Windows 本機（C 槽）
    │
    ├── Docker Desktop（只是「引擎」，程式本體很小）
    │
    └── WSL2（Linux 核心 + 你的 Ubuntu 發行版）
              │
              ├── 發行版本體（.vhdx 檔）──→ 搬到外接SSD ★
              └── Docker 的資料層（image/volume）──→ 也指到外接SSD ★

外接式 SSD（例如 D:\ 或 E:\）
    │
    ├── wsl-distros/          ← WSL2 發行版本體放這裡
    ├── docker-data/          ← Docker 的 image/volume 資料放這裡
    └── ai-cyber-project/     ← 你的專案原始碼、資料集、模型權重
              ├── docker/
              ├── backend(django)/
              ├── n8n_data/
              ├── ai_training/
              └── data/  (CIC-IDS2017、NSL-KDD 等資料集)
```

**核心原則只有一句話：任何「會變大、會下載、會產生檔案」的東西，都不要留在 C 槽，全部導到外接 SSD。**
C 槽只留「Docker Desktop 這個 App 本身」，其他都是可以刪掉重建的。

---

## 1. 如何避免訓練 AI 模型時汙染 / 感染本機環境？

初學者最常見的誤區是「直接在 Windows 上裝一堆 pip 套件、下載一堆不明資料集」。這裡用三層隔離來解決：

### 第一層：容器隔離（Docker）
- 所有 Python 套件（torch、pandas、scapy...）都裝在 Docker image 裡，**不要在 Windows 本機直接 `pip install`**。
- 好處：不管裝壞幾次，`docker compose down` 之後刪掉重來就好，Windows 本身完全沒有痕跡。

### 第二層：系統隔離（WSL2 專用發行版）
- 不要把這個專題塞進你原本的預設 Ubuntu（如果你已經有一個在用的）。
- 另外開一個**專用的 WSL2 發行版**，例如命名為 `cyber-ai-dev`，未來如果這個環境壞掉、中毒、跑壞了，直接：
  ```powershell
  wsl --unregister cyber-ai-dev
  ```
  整個環境瞬間消失，完全不影響 Windows 本身或你其他的 WSL 環境。

### 第三層：資料隔離（外接 SSD + 唯讀來源）
- 下載的資料集（PCAP、CSV）一律放在外接 SSD 的 `data/` 資料夾，**用 Docker volume mount 唯讀（`:ro`）方式**給容器讀取，容器內程式沒辦法反過來寫壞你的原始資料。
- 下載資料集後，建議做一次雜湊檢查（MD5/SHA256），確認檔案沒有被竄改或夾帶惡意檔案（尤其是從非官方連結下載時）：
  ```bash
  sha256sum data/cicids2017/*.csv
  ```
- **原則：所有「未知來源」的東西（資料集、範例腳本、n8n community node）都先在容器裡打開檢查，不要直接在 Windows 本機用滑鼠雙擊執行。**

### 額外建議
- 幫這個 WSL2 發行版關掉「跟 Windows 檔案系統緊密整合」的不必要功能，資料盡量留在 Linux 檔案系統內（`/home/xxx/...`），效能也會比走 `/mnt/c/...` 快很多。
- 把 `docker-compose.yml`、`Dockerfile`、程式碼全部放進 Git 版控。這樣「環境」本身也是可重建的——就算 SSD 上的容器資料整個刪掉，只要 `git clone` + `docker compose up` 就能重生。

---

## 2. Windows 原生 Docker Desktop，還是 WSL2 + Docker？

**建議：Docker Desktop（安裝在 Windows），但底層引擎設定為「使用 WSL2」。**

這聽起來像是同時用了兩個，但其實是目前官方推薦、也是最穩定的組合：

| 方案 | 說明 | 適合你嗎 |
|---|---|---|
| Docker Desktop + Hyper-V 後端（舊式） | 效能較差、GPU 支援麻煩 | ❌ 不建議 |
| **Docker Desktop + WSL2 後端（推薦）** | Docker Desktop 是「操作介面 + 引擎管理」，實際運算全部丟進 WSL2 的 Linux 核心執行，效能接近原生 Linux，且**目前 GPU（CUDA）直通給容器，只有 WSL2 後端支援** | ✅ 這個 |
| 純 WSL2（不裝 Docker Desktop，在 WSL2 裡自己裝 docker engine） | 更輕量、更「乾淨」，但要自己處理 systemd、開機自啟、Windows 整合的細節 | 進階可選 |

**為什麼你（做 CNN + CUDA 訓練）一定要 WSL2 後端：**
PyTorch GPU 版本（你的 `requirements.txt` 裡是 `torch==2.1.0+cu121`）要在容器裡吃到顯卡，目前只有透過 WSL2 的 GPU 直通機制才能運作。Windows 原生 Hyper-V 容器基本上無法用 GPU 訓練。

**你需要準備的東西：**
1. Windows 上安裝**最新的 NVIDIA 顯示卡驅動**（不是 CUDA Toolkit，驅動就夠，WSL2 裡的 CUDA 由容器 image 自帶）。
2. 安裝 WSL2（見第 6 節步驟）。
3. 安裝 Docker Desktop，設定中勾選 **Settings → General → Use the WSL 2 based engine**，以及 **Settings → Resources → WSL Integration** 勾選你的專用發行版（`cyber-ai-dev`）。

---

## 3. n8n、Django 後端、AI 模型、資料庫分工建議

用「一個服務只做一件事」的方式拆開，方便未來獨立除錯、獨立重啟：

| 服務 | 角色 | 是否需要 GPU | 說明 |
|---|---|---|---|
| **n8n** | AI Agent 的流程大腦、Gemini API 串接、通知分派（LINE/Telegram/Slack） | 否 | 純邏輯層，跟 Django 之間用內部 REST API 溝通 |
| **Django (DRF)** | 平台後端：接收封包分析結果、提供 Dashboard API、使用者/裝置管理、事件記憶儲存 | 否 | 對外 API，也對內提供資料給 n8n 查詢 |
| **AI 訓練/推論服務** | CNN+Autoencoder 訓練、Grad-CAM、異常分數計算 | ✅ 是 | 建議獨立一個容器（甚至獨立一個 docker-compose profile），因為它是「重量級、偶爾跑」的工作，不需要一直開著 |
| **PostgreSQL** | Django 的正式資料庫 | 否 | 事件記憶、使用者偏好記憶都存這裡 |
| **Redis** | Celery 的訊息佇列 + 快取 | 否 | 給 Django 的非同步任務用（例如：觸發一次訓練/推論不要卡住 API） |
| **Celery Worker** | 背景任務執行者：跑推論、產生報告、呼叫 AI 訓練腳本 | 視任務而定 | Django 收到「請重新訓練」之類的請求時，丟給 Celery 背景處理 |

**資料流大方向：**
```
封包/流量特徵 → AI 訓練/推論服務（模型.pt）→ 寫入結果 → Django API/DB
                                                        │
n8n（讀 Django API，判斷是否要通知，串 Gemini 產生說明）←┘
                                                        │
                                        LINE / Telegram / Slack / Web Dashboard
```

**關鍵設計原則：AI 訓練是「離線批次工作」，不是即時 API。**
訓練跑幾十分鐘到幾小時很正常，所以訓練用 `docker compose run` 手動觸發，或用 Celery 排程觸發，**不要**把訓練塞進 Django 的一般 HTTP request-response 流程裡（那樣會 timeout）。推論（用已訓練好的模型跑一筆新資料）才適合做成即時 API。

---

## 4. 建議的資料夾結構

假設你的外接 SSD 是 `E:\`，在 Windows 檔案總管看到的路徑、對應到 WSL2 裡的路徑如下：

```
E:\ai-cyber-project\                     ← Windows 端看到的路徑
    │  （在 WSL2 裡對應成 /mnt/e/ai-cyber-project/，
    │   但建議實際工作目錄搬進 WSL2 檔案系統內，效能更好，見下方說明）
    │
    ├── docker/
    │   ├── docker-compose.yml
    │   ├── docker-compose.override.yml     ← 本機個人化設定（不進 git）
    │   ├── django.Dockerfile
    │   ├── n8n.Dockerfile（通常用官方 image 即可，不一定需要）
    │   └── ai-training.Dockerfile          ← 含 CUDA base image
    │
    ├── backend/                            ← Django 專案
    │   ├── manage.py
    │   ├── config/
    │   ├── apps/
    │   │   ├── events/                     ← 事件記憶
    │   │   ├── devices/                    ← 裝置/使用者偏好記憶
    │   │   └── reports/                    ← 事後報告
    │   └── requirements.txt                ← 就是你附的這份
    │
    ├── ai_training/                        ← 你的 Training_Guide/EXPERIMENT_GUIDE 對應的程式碼
    │   ├── core/
    │   │   ├── run_training.py
    │   │   ├── run_semi_supervised.py
    │   │   ├── run_threshold_tuning.py
    │   │   ├── comparison_benchmark.py
    │   │   └── cnn_gradcam/
    │   └── output/                         ← 訓練產出（模型、圖表、報告）
    │
    ├── data/                                ← 資料集（唯讀掛載進容器）
    │   ├── cicids2017/
    │   ├── nslkdd/
    │   └── cicddos2019/
    │
    ├── n8n_data/                            ← n8n 的 workflow/憑證資料（用 volume 掛載，不進 git）
    │
    ├── knowledge_base/                       ← 你正在建的三大知識庫（term/scam/remediation）
    │   ├── glossary.csv 或 airtable 同步檔
    │   ├── scam_cases.csv
    │   └── remediation_steps.csv
    │
    ├── .env                                  ← 密鑰、API Key（絕對不進 git）
    ├── .gitignore
    └── README.md
```

**重要：實際「工作目錄」建議放在 WSL2 的 Linux 檔案系統內，而不是 `/mnt/e/...`**
如果專案是放在 `/mnt/e/...`（也就是 Windows 的外接 SSD 透過 WSL2 的「跨系統掛載」），I/O 效能會明顯變差（尤其資料集讀寫很密集的訓練場景）。更好的做法是：

1. 把 WSL2 這個發行版本體（`.vhdx`）整個搬到外接 SSD 上（第 6 節會教怎麼做）。
2. 這樣你在 WSL2 裡用的路徑（例如 `/home/you/ai-cyber-project/`）**實體上就已經住在外接 SSD 裡**，速度是原生 Linux 檔案系統的速度，不是跨系統掛載的速度。
3. Windows 檔案總管仍可以透過 `\\wsl$\cyber-ai-dev\home\you\ai-cyber-project` 看到並編輯這些檔案（VSCode 的 WSL extension 也是走這條路）。

---

## 5. 建議的 docker-compose 架構

以下是簡化過、給你當骨架的版本（欄位可依實際需求增減，重點是「分工」和「volume 對應到外接SSD」的概念）：

```yaml
version: "3.9"

services:

  postgres:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_DB: cyberai
      POSTGRES_USER: cyberai
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redisdata:/data

  django:
    build:
      context: ../backend
      dockerfile: ../docker/django.Dockerfile
    restart: unless-stopped
    env_file: ../.env
    depends_on:
      - postgres
      - redis
    volumes:
      - ../backend:/app
      - ../ai_training/output:/app/model_outputs:ro   # 只讀取訓練結果，不寫入
    ports:
      - "8000:8000"
    command: python manage.py runserver 0.0.0.0:8000

  celery_worker:
    build:
      context: ../backend
      dockerfile: ../docker/django.Dockerfile
    restart: unless-stopped
    env_file: ../.env
    depends_on:
      - postgres
      - redis
    volumes:
      - ../backend:/app
    command: celery -A config worker -l info

  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - GENERIC_TIMEZONE=Asia/Taipei
    volumes:
      - ../n8n_data:/home/node/.n8n
    ports:
      - "5678:5678"

  ai-training:
    build:
      context: ../ai_training
      dockerfile: ../docker/ai-training.Dockerfile
    # 這個服務平常「不」自動啟動，用 profile 隔開，訓練時才手動叫起來
    profiles: ["training"]
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ../ai_training:/workspace
      - ../data:/workspace/data:ro
    command: python core/run_training.py --dataset cicids2017 --data-dir data/cicids2017

volumes:
  pgdata:
  redisdata:
```

**幾個關鍵設計：**
- `ai-training` 用 `profiles: ["training"]`，意思是平常 `docker compose up` 不會啟動它，訓練時你要明確打：
  ```bash
  docker compose --profile training run --rm ai-training
  ```
  這樣它不會 24 小時佔用 GPU 資源，也避免跟 Django 主服務混在一起。
- `deploy.resources.reservations.devices` 這段是讓容器拿到 GPU，前提是 Docker Desktop 已經設定好 WSL2 + GPU 直通（第 2 節提到的驅動安裝）。
- `data` 資料夾用 `:ro`（read-only）掛載進訓練容器，避免程式不小心覆寫原始資料集。
- `pgdata`、`redisdata` 這些 named volume，記得在 Docker Desktop 設定裡把「資料存放位置」指到外接 SSD（第 6 節說明），不然預設還是會佔用 C 槽空間。

---

## 6. 建置順序（照著做，不要跳步）

### 步驟 1：安裝 NVIDIA 顯示卡驅動（Windows 端）
到 NVIDIA 官網下載你顯卡對應的最新「Game Ready」或「Studio」驅動並安裝，重開機。
> 這一步做完，先不用急著裝 CUDA Toolkit，WSL2+Docker 裡用的 CUDA 是 image 自帶的。

### 步驟 2：安裝 / 更新 WSL2
在 Windows PowerShell（系統管理員模式）執行：
```powershell
wsl --install
wsl --update
wsl --set-default-version 2
```
重開機後確認版本：
```powershell
wsl --version
```

### 步驟 3：把「WSL2 存放位置」搬到外接 SSD（最容易忽略的一步）
WSL2 預設會把所有發行版的 `.vhdx` 檔放在 C 槽的使用者資料夾下。要換成外接 SSD，流程是「先在 C 槽裝好一個新發行版，再匯出、刪除、匯入到 SSD 上」：

```powershell
# 1. 到 Microsoft Store 或用 wsl --install 裝一個 Ubuntu，命名時可自訂
wsl --install -d Ubuntu --name cyber-ai-dev

# 2. 匯出成 tar 檔（先確保 SSD 已插好，例如 E 槽）
wsl --export cyber-ai-dev E:\wsl-distros\cyber-ai-dev.tar

# 3. 從系統登錄的清單中移除這個發行版
wsl --unregister cyber-ai-dev

# 4. 匯入回來，這次指定安裝位置在 SSD 上
wsl --import cyber-ai-dev E:\wsl-distros\cyber-ai-dev E:\wsl-distros\cyber-ai-dev.tar --version 2

# 5. 確認一下（Ver 應該是 2，路徑應該指向 E:\）
wsl -l -v
```
之後打開這個發行版：
```powershell
wsl -d cyber-ai-dev
```

### 步驟 4：安裝 Docker Desktop（Windows 端）
- 到官網下載安裝，安裝完成後打開。
- 進 **Settings → General**，勾選 **Use the WSL 2 based engine**。
- 進 **Settings → Resources → WSL Integration**，把 `cyber-ai-dev` 打勾（讓這個發行版可以用 docker 指令）。
- 進 **Settings → Resources → Advanced**（部分版本在 Settings → Resources 底下），把 **Disk image location** 也指到外接 SSD，例如 `E:\docker-data`。這樣 Docker 自己抓的 image、volume 也不會塞爆 C 槽。

### 步驟 5：驗證 GPU 能不能被容器看到
在 `cyber-ai-dev` 的終端機裡跑：
```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```
如果看到顯卡資訊和 CUDA 版本，代表 GPU 直通成功。**這一步一定要先過，才進行下一步**，否則後面訓練會卡在「找不到 GPU」卻不知道問題出在哪一層。

### 步驟 6：把專案放進 WSL2 檔案系統，並拉起服務骨架
```bash
cd ~
1.(
mkdir ai-cyber-project

cd ai-cyber-projectgit 
//確認你現在在 ~/ai-cyber-project 裡面（ pwd 應該顯示 /home/incent/ai-cyber-project，若不是打cd ~/ai-cyber-project)

cp "/mnt/c/Users/User/Downloads/final_project2.zip" . //把壓縮檔從 Downloads 複製進來
ls -lh //應該會看到 final_project2.zip 這個檔案

sudo apt update && sudo apt install -y unzip 
//sudo：以系統管理員（最高權限）執行。
//apt update：更新軟體源清單。
//&&：邏輯與。代表前一個指令成功執行後，才繼續執行下一個

unzip final_project2.zip //解開壓縮檔： 解開後用 ls 確認內容

shopt -s dotglob 
mv final_project/* . 
shopt -u dotglob
//確認目前在 ai-cyber-project 裡： pwd 應該顯示 /home/incent/ai-cyber-project
//這行指令會让 mv 連隱藏檔案（如 .env）也一併移動，避免漏掉重要設定檔：  這會把 final_project 裡面所有東西（包括隱藏檔）搬到上一層，也就是現在這個 ai-cyber-project 資料夾里
//shopt -s dotglob：用途：開啟（set）Shell 的 dotglob 功能；原因：在預設情況下，Linux 的萬用字元 * 代表「除了隱藏檔（檔名開頭為 .）以外的所有檔案」。開啟這個功能後，* 就會包含隱藏檔（例如 .gitignore、.env 等）
//mv final_project/* .：用途：將 final_project/ 底下的所有檔案（*）移動（move）到當前目錄（.）
//shopt -u dotglob：用途：關閉（unset）dotglob 功能。原因：恢復系統預設行為，避免之後誤操作到其他隱藏檔案。

ls final_project //確認 final_project 現在應該是空的

rmdir final_project 
rm final_project2.zip
//刪除空了的資料夾和 zip 檔


//先了解你現有專案的實際結構(a1~a2)/檢查現有環境變數檔(a3~a),再照著實際狀況幫你寫 docker-compose.yml、Dockerfile、.env.example,而不是直接套用範例——不然容器可能連不上正確的資料庫設定、或抓不到正確的 settings 模組路徑

//a1
find . -name settings.py //找到 Django 的設定檔案在哪裡（通常叫 settings.py）
//output=>incent@LAPTOP-2CCJ8SVM:~/ai-cyber-project$ find . -name settings.py
./network_platform/settings.py
=>設定檔在 ./network_platform/settings.py——也就是說你的 Django 專案主模組(config)叫做 network_platform,這個資訊很重要,之後 docker-compose.yml 裡要用到(例如 DJANGO_SETTINGS_MODULE=network_platform.settings)。

//a2
cat network_platform/settings.py
//a2確認目前資料庫設定
確認目前資料庫設定是用 SQLite 還是已經改成 PostgreSQL（把下面指令中的 xxx/settings.py 换成上一步找到的實際路徑）： grep -A 6 "DATABASES" */settings.py 或者直接 cat 那個 settings.py 檔案地內容貼給我。
=>這份 settings.py:
設定模組是 network_platform.settings(對應 manage.py 用的 DJANGO_SETTINGS_MODULE)
資料庫目前是寫死用 SQLite,還沒有做「可用環境變數切換成 PostgreSQL」的設計 → 這代表如果要接 PostgreSQL,需要先小改一下這個檔案,不是只改 docker-compose 就好
CELERY_BROKER_URL、N8N_WEBHOOK_URL 已經是用 os.getenv(...) 寫的,代表已經支援用環境變數覆蓋,很好,容器化時直接設對的網址就行,不用改程式碼
CNN_MODEL_PATH 指向 media/model/best_model.pt,REPORT_OUTPUT_DIR 指向 media/reports → 這些路徑之後要用 volume 掛載,才能讓模型檔案、報告在容器重啟後不會消失

//a3
ls -la | grep env //確認有沒有現成的環境變數檔（包括隱藏檔）
find . -iname "*celery*"
cat requirements.txt
find . -maxdepth 2 -type d | sort //最後確認整體資料夾層級

//這邊決定先維持 SQLite（設定不用改，先求環境跑起來，之後有需要再換）
幾個重要說明
django 和 celery_worker 都給了 GPU 權限——因為你的 settings.py 讓推論邏輯直接讀取 CNN_MODEL_PATH,兩邊都有可能需要載入 PyTorch 模型,先都開權限比較保險,之後如果發現其實只有 Celery 在做推論、Django 純粹轉發請求,可以再把 django 服務那段 GPU 設定拿掉。
celery -A network_platform worker 這行我是用你的 config 資料夾名稱(network_platform)去猜的,如果啟動後 Celery 找不到 app,把它換成 network_platform/celery.py 裡 Celery(...) 實際填的名字告訴我就好。
這階段刻意沒加 PostgreSQL 服務,SQLite 檔案 db.sqlite3 會直接透過 volumes: - ..:/app 這個掛載被容器讀到,不用額外設定。
//接著把四個設定檔案都準備好了,等一下你只要用跟剛剛一樣的方式(下載到 Windows → cp 進 WSL2)把它們放進專案
間,這個我會先提醒你)：Django(DOCKERFILE)、Docker compose(YML)、.env(EXAMPLE)、Gitignore additions(TXT)

cd ~/ai-cyber-project
pwd
//確認在專案根目錄： cd ~/ai-cyber-project pwd

mkdir -p docker //建立 docker 子資料夾

cp /mnt/c/Users/User/Downloads/django.Dockerfile docker/ 
cp /mnt/c/Users/User/Downloads/docker-compose.yml docker/
//把兩個檔案複製進 docker/（假設下載到 Windows 的 Downloads，檔名不變）

cp /mnt/c/Users/User/Downloads/.env.example.txt . 
cp /mnt/c/Users/User/Downloads/gitignore-additions.txt .
//把 .env.example 和 gitignore 建議檔放到專案根目錄
//確認.env.example.txt內容正確： ls -la | grep env; cat .env.example 


//.env.example	範本,只是告訴別人(或未來的你)「這個專案需要哪些設定項目」,裡面的值都是假的、公開也沒關係(例如 change-me-to-a-random-string)	✅ 會進 Git,大家都看得到
.env	真正會被程式讀取的檔案,裡面填的是你實際要用的密碼、金鑰(例如真正的 N8N_PASSWORD)	❌ 絕對不能進 Git(我們前面 .gitignore 裡已經把它排除了)
cp .env.example .env //實際建立你自己的 .env(複製自 .env.example，這個才是真正會被程式讀取的檔)： 

python3 -c "import secrets; print(secrets.token_urlsafe(50))" //生成隨機字串，貼到 .env 裡的 DJANGO_SECRET_KEY= 後面就行
nano .env
..
Ctrl+O
Ctrl+X
//用 nano 這個簡單的終端機編輯器打開 .env： nano .env 進去後至少把這兩行改成你自己的值： - DJANGO_SECRET_KEY 改成一串隨意的長字串(不要用預設的 change-me...) - N8N_PASSWORD 改成你自己設的密碼（之後登入 n8n 網頁會用到） 改完按 Ctrl+O 兒存檔（會問檔名，直接按 Enter 就好），再按 Ctrl+X 離開。
EQmswpHVkIR2aIrW81QctAwWsYyX3ajnZo5fTTrNqkTIVqTSNswIIxxfKd6HT5kQz0o
//ALT+U=>上一步 右鍵=>貼上
cat .env //確認內容

ls -a . | grep -E "env|gitignore" //確認根目錄下的檔案(記得加 -a 才看得到點開頭的隱藏檔)：應該會看到 .env、.env.example、gitignore-additions.txt 三個。
ls docker/  //確認 docker 子資料夾內的檔案： ls docker/ 應該只會看到 django.Dockerfile 與 docker-compose.yml 兩個，不會有 env 或 gitignore相關檔案
(不用執行：ls -la | grep env cat .env.example//
確認檔案存在且內容正確（注意：開頭是點的隱藏檔，ls 需要加 -a 才看得到）)
//確認層級是否正確：  應該看到 docker/django.Dockerfile、docker/docker-compose.yml，以及根目錄下的 .env.example、gitignore-additions.  //

cat gitignore-additions.txt >> .gitignore && rm gitignore-additions.txt
//ls -a 的結果裡發現有一個 .gitignore(注意跟 gitignore-additions.txt 不同),代表你的專案原本就有一份 .gitignore 了——我們該做的是把 gitignore-additions.txt 的內容「併」進去.gitignore
//把 gitignore-additions.txt 的內容接在現有 .gitignore 後面(用 >> 代表「附加」，不會覆蓋掉原本內容)： cat gitignore-additions.txt >> .gitignore rm gitignore-additions.txt
cat .gitignore //確認內容

cd docker 
pwd
進入 docker 資料夾(注意是相對路徑，你現在应該已經在 ai-cyber-project 裡)： cd docker pwd 應該顯示 /home/incent/ai-cyber-project/docker

docker compose build
//第一次 build(重點，會花點時間)
//第一次 build 會要下載 PyTorch 的 GPU 基底圖像(數GB大小)，看你網速可能要等好幾分鐘到一十幾分鐘，這是正常現象，不要中途中斷： docker compose build 看到最後顯示類似 'Successfully built' 或直接回到提示字元且沒有紅色錯誤訊息，代表成功。

docker compose up -d redis n8n django celery_worker -d
//build 成功後，用正確的服務名單拉起來(沒有 postgres)： docker compose up -d redis n8n django celery_worker -d 代表在背景執行，不會占住你的終端機。

docker compose ps
//確認四個服務都正常起來： docker compose ps 每一行的 STATUS 都應該是 Up（或 running）。如果有任何一行顯示 Exit 或 Restarting，把那行貼給我。
=>出現問題N8N_USER/N8N_PASSWORD 讀不到值(導致 n8n 一直重啟)
看這兩行:
WARN[0000] The "N8N_USER" variable is not set. Defaulting to a blank string.
WARN[0000] The "N8N_PASSWORD" variable is not set. Defaulting to a blank string.
原因是:docker-compose.yml 裡 ${N8N_USER} 這種寫法,Docker Compose 只會去讀取跟 docker-compose.yml 同一層資料夾裡名字剛好叫 .env 的檔案。但你的 .env 是放在上一層(專案根目錄),不是在 docker/ 資料夾裡,所以這個變數代換機制找不到它,N8N_USER/N8N_PASSWORD 就變成空字串——n8n 開啟了「需要帳密登入」但帳密是空的,啟動失敗、不斷重開機,就是你看到的 Restarting (1)。
注意:這跟我們之前給 django/celery_worker 用的 env_file: ../.env 是不同機制——那個是「把整份 .env 內容當作容器內的環境變數」,運作正常;但 ${N8N_USER} 這種寫在 YAML 檔裡的變數代換,規則不一樣,需要額外處理。
修法很簡單:在 docker/ 資料夾裡建一個「捷徑」指向根目錄的 .env,這樣兩種機制都能讀到同一份檔案,不用維護兩份://
//確認現在在 docker 資料夾裡： pwd 應該顯示 /home/incent/ai-cyber-project/docker

ln -s ../.env .env 
ls -la | grep env
//建立一個指向上一層 .env 的軟連結（symlink），這樣不用複製內容、也不會有兩分殊途問題： ln -s ../.env .env ls -la | grep env 應該會看到 .env -> ../.env 這樣的箭頭標記

docker compose down 
docker compose up -d redis n8n django celery_worker
//重新拉起服務，讓 Docker Compose 重新讀取環境變數： docker compose down docker compose up -d redis n8n django celery_worker 這次不應該再看到 N8N_USER/N8N_PASSWORD 的 WARN 訊息

docker compose ps
//確認 n8n 不再一直重啟： docker compose ps 如果 docker-n8n-1 這行的 STATUS 變成 Up、不再是 Restarting，代表修復成功

docker compose logs n8n --tail 50
//n8n 還是在重開機,而且 N8N_USER/N8N_PASSWORD 的 WARN 訊息這次消失了——代表軟連結那招確實有效,環境變數問題解決了,但 n8n 崩潰的真正原因是別的東西。
現在需要看 n8n 實際的錯誤訊息,才能知道真正卡在哪:docker compose logs n8n --tail 50

ls -la ../n8n_data
//確認 n8n_data 資料夾的權限狀況:ls -la ../n8n_data
=>原因drwxr-xr-x  2 root   root   4096 Aug 19 14:30 .
=>n8n_data 這個資料夾的擁有者是 root,但 n8n 容器內部是用一個叫 node 的非 root 使用者在跑(這是官方 image 的安全設計,不用 root 執行程式)。這個資料夾是 Docker 第一次啟動時自動幫你建立的,而 Docker 自動建立資料夾預設會用 root 身份,所以容器內的 node 使用者完全沒有寫入權限,才會出現 EACCES: permission denied。
修法是把這個資料夾的擁有者,改成跟容器內 node 使用者一致(官方 n8n image 固定用 UID 1000):

pwd //確認目前在 docker 資料夾裡： pwd

sudo chown -R 1000:1000 ../n8n_data
//把 n8n_data 的擁有者改成 UID 1000（對應 n8n 容器內部的 node 使用者）： sudo chown -R 1000:1000 ../n8n_data 這裡會要你輸入 sudo 密碼

ls -la ../n8n_data
//確認權限修改成功： ls -la ../n8n_data 應該會從 drwxr-xr-x root root 變成擁有者/群組都是 1000。

docker compose up -d n8n
//重新啟動 n8n 容器（不需要重新 build，只是要重新啟動使它重新嘗試寫入）： docker compose up -d n8n

docker compose ps
//等十秒左右，確認不再一直重啟： docker compose ps 如果 docker-n8n-1 這行變成 Up，代表修復成功

docker ps -a
//確認舊容器內容
先看看電腦裡所有容器(不只限現在這份 docker-compose.yml 管的)，確認那些舊容器是什麼： docker ps -a 特別注意名字包含 secai 的那幾行，確認它們的 STATUS。

docker inspect secai-postgres --format '{{json .Mounts}}'
//確認有沒有持久化資料
確認這個舊容器有沒有連著什麼 volume（存資料的地方）： docker inspect secai-postgres --format '{{json .Mounts}}' 如果結果是空陣列 []，代表沒有持久化資料，可以安心刪除。

docker rm secai-postgres //先刪除舊容器本身

docker volume rm docker_postgres_data docker_n8n_data
//再刪除不在使用的舊 volume(注意：不要刪 docker_redisdata，那是你現在 redis 服務正在用的)

docker ps -a 
docker volume ls
//確認結果： docker ps -a docker volume ls 應該只剩下你現在四個服務，以及只有 docker_redisdata 這一個 volume。

//到這裡,原本規劃的**「步驟六:拉起服務骨架」已經全部完成
✅ WSL2 專用發行版 cyber-ai-dev 建立並搬到外接 SSD
✅ Docker Desktop 的映像資料也搬到外接 SSD,GPU 直通驗證成功
✅ 既有的 Django 專案(network_platform)複製進環境,層級整理乾淨
✅ docker-compose.yml、Dockerfile、.env 建置完成
✅ redis、django、celery_worker、n8n 四個服務全部正常運作
✅ 環境變數讀取問題、n8n 權限問題、舊容器汙染問題都排除了
)
1 or 2  (change1)
2.(
//
a.docker compose up -d postgres redis n8n django celery_worker 這裡面有 postgres,但你的 docker-compose.yml 裡我們沒有建立 postgres 服務(因為你選擇先維持 SQLite),打這個指令會直接報錯「找不到叫 postgres 的服務」。
b.cp ../.env.example ../.env 這行你已經做過了(而且你還手動改好了密碼跟金鑰),再跑一次會把你剛剛改好的內容覆蓋回原本的預設值,千萬不要再執行這行。//

clone <你的專案 repo> ai-cyber-project
cd ai-cyber-project/docker
cp ../.env.example ../.env   # 填入密碼、API Key
docker compose up -d postgres redis n8n django celery_worker
)
```
先確認 Django（`http://localhost:8000`） Django 的畫面（可能是你自己實作的首頁，或者登入頁面，取決於你的 urls.py 怎麼寫）、n8n（`http://localhost:5678`）都能開起來，資料庫連線正常。

查詢目前有哪些帳號
在終端機裡執行（你現在應該在 ~/ai-cyber-project/docker 裡，不在就先 cd 進去）： docker compose exec django python manage.py shell -c "from django.contrib.auth import get_user_model; U = get_user_model(); [print(u.username, '| 管理員:', u.is_superuser, '| 啟用中:', u.is_active) for u in U.objects.all()]" 
這會列出目前資料庫裡所有帳號、是不是管理員、有沒有被停用。如果什麼都沒印出來，代表還沒建過任何帳號。

docker compose exec django python manage.py changepassword admin
//（忘記密碼時）直接重設

如果上一步發現帳號存在、但忘了密碼是什麼，直接重設一組新的(把 username 換成你實際建的帳號名)： docker compose exec django python manage.py changepassword 你的使用者名 會要你輸入兩次新密碼確認。

（還沒建的話）建新帳號
如果確認根本還沒建過任何帳號，就回到之前那一步建管理員： docker compose exec django python manage.py createsuperuser
sam000000

翻閱n8n資訊
//看你自己設定的 .env 檔案
cd ~/ai-cyber-project
cat .env | grep N8N
=>
N8N_WEBHOOK_URL=http://n8n:5678/webhook/ai-chat
N8N_USER=admin
N8N_PASSWORD=sam666

想看 n8n 有沒有正常運作、或除錯
//看容器的即時 log
cd ~/ai-cyber-project/docker
docker compose logs -f n8n
//-f 是「持續追蹤」,會即時顯示新的訊息,按 Ctrl+C 可以離開(不會關掉容器,只是離開追蹤畫面)。

想操作 n8n(建 workflow、串 Gemini API、設通知等)
//直接打開瀏覽器連到 n8n 的網頁介面:
http://localhost:5678

### 步驟 7：單獨測試訓練容器
```bash
docker compose --profile training build ai-training
docker compose --profile training run --rm ai-training \
    python core/run_training.py --dataset simulate
```
先用 `--dataset simulate`（模擬資料，不用先下載真實資料集）確認整條訓練流程能跑完，再換成 `cicids2017` 等真實資料集。

### 步驟 8：把資料集放進 `data/` 資料夾
依照你 `Training_Guide` 裡第 3.1 節的路徑規則，把下載好的 CIC-IDS2017 / NSL-KDD 等資料集放進對應子資料夾即可，容器會透過 volume 掛載讀到。

---

## 7. 常見錯誤與檢查方式

| 錯誤現象 | 可能原因 | 檢查/解決方式 |
|---|---|---|
| `docker: Error response from daemon: could not select device driver` | GPU 直通沒設定成功 | 確認顯卡驅動版本夠新、Docker Desktop 是否為 WSL2 後端、重跑步驟 5 的 `nvidia-smi` 測試 |
| WSL2 裡 `nvidia-smi` 有東西，但容器裡沒有 | Docker Desktop 沒有勾選對這個發行版的 WSL Integration | 回到 Settings → Resources → WSL Integration 檢查 |
| C 槽莫名其妙一直變小 | Docker 的 image/volume 資料沒有真的搬到 SSD、或 WSL2 的 vhdx 還在 C 槽 | `wsl -l -v` 檢查發行版位置；Docker Desktop 設定裡確認 Disk image location |
| 訓練容器讀不到 `data/` 底下的資料集 | volume 掛載路徑寫錯，或路徑用了 Windows 的 `\` 而不是 Linux 的 `/` | 在 `docker-compose.yml` 裡一律用相對路徑 + 正斜線，並用 `docker compose config` 指令印出實際解析後的路徑做確認 |
| CUDA out of memory | batch size / latent dim 設太大 | 依你 `Training_Guide` Q2 建議，先縮小 `--batch` 或 `--latent` |
| 容器裡 `pip install` 每次都重新下載，很慢 | 沒有善用 Docker layer cache，或 requirements.txt 常常變動導致 cache 失效 | Dockerfile 裡把 `COPY requirements.txt` 和 `RUN pip install` 放在最前面，程式碼變動不會讓套件重新安裝 |
| n8n 重啟後 workflow 不見了 | `n8n_data` 沒有正確掛載成 volume，資料存在容器內部、容器被砍掉就消失 | 確認 `docker-compose.yml` 裡 `n8n` 服務有掛載 `../n8n_data:/home/node/.n8n` |
| 資料庫連線 `could not connect to server` | Django 啟動時 postgres 還沒完全就緒 | 在 compose 裡加 `depends_on` + 健康檢查（`healthcheck`），或啟動腳本裡加重試邏輯，不要單純用 `depends_on` 當保證 |
| WSL2 發行版整個「壞掉」 | 常見於強制關機、磁碟拔除時機不對 | 因為你有把程式碼進 git、資料集是唯讀外部檔案，直接 `wsl --unregister` 砍掉，照步驟 3 重新 import 一個乾淨的即可，資料不會因此消失 |

---

## 小結：這套設計如何滿足你的三個要求

- **不汙染本機**：所有套件裝在容器裡；WSL2 用專用發行版；C 槽只留 Docker Desktop 本體。
- **安全**：資料集唯讀掛載、下載後做雜湊檢查、密鑰放 `.env` 不進 git、可疑檔案一律在容器內開啟。
- **可重建**：`docker-compose.yml` + `Dockerfile` + 程式碼都進 git；WSL2 發行版壞了直接 `unregister` 重新 `import`；只要外接 SSD 上的 `data/` 和 git repo 還在，整套環境可以在任何一台新電腦上重新生出來。
