# FIFA World Cup 2026 — 待完成任務指令文件
# 按順序執行，完成一個再做下一個

================================================================
任務 A：修復 /health 405 錯誤（5 分鐘）
================================================================

【你需要做的操作】

第一步：修改 app/main.py
找到這段：
    @app.get("/health")
    def health():
        return {"status": "ok"}

替換成：
    @app.api_route("/health", methods=["GET", "HEAD"])
    def health():
        """UptimeRobot keep-alive ping endpoint。支援 GET 和 HEAD 方法。"""
        return {"status": "ok"}

第二步：在 app/main.py 加入 payments router
在所有 import 行加：
    from app.routers import payments

在所有 app.include_router(...) 行的最後加：
    app.include_router(payments.router, prefix="/webhook", tags=["webhook"])

第三步：複製檔案到專案
把以下檔案複製到對應位置：
- payments.py → C:\Users\samli\Desktop\worldcup_api\app\routers\payments.py
- UpgradeButton.tsx → C:\Users\samli\Desktop\worldcup-frontend\components\UpgradeButton.tsx
- MemberGate.tsx → C:\Users\samli\Desktop\worldcup-frontend\components\MemberGate.tsx

在 app/database.py 最下方加入 get_supabase_admin() 函式（見 database_addition.py）

在 app/config.py 的 Settings class 加入（見 config_additions.py）：
    lemonsqueezy_webhook_secret: str = ""
    lemonsqueezy_api_key: str = ""

第四步：Push 到 GitHub
在 CMD 執行：
    cd C:\Users\samli\Desktop\worldcup_api
    git add .
    git commit -m "fix: HEAD method for health, add LemonSqueezy webhook"
    git push

第五步：確認 Render 部署成功
等 2-3 分鐘後瀏覽：
    https://worldcup-api-jryd.onrender.com/health
應該看到：{"status": "ok"}

第六步：確認 UptimeRobot 變綠
等約 5-10 分鐘，到 UptimeRobot Dashboard 確認 monitor 狀態變為 Up。

================================================================
任務 B：LemonSqueezy 設定（平台操作，不需要寫程式）
================================================================

第一步：建立 LemonSqueezy 帳號
1. 前往 https://www.lemonsqueezy.com
2. 點 Sign Up，用 Email 註冊（個人即可，不需要公司）
3. 完成 Email 驗證

第二步：建立商店和產品
1. 登入後點左側 Stores → Create Store
2. 填入商店名稱（例如：worldcup-analytics）
3. 點左側 Products → Add Product
4. 填入：
   - Name：World Cup Pro 分析方案
   - Price：自訂（建議 NT$299 或 US$9.99 一次性）
   - Type：One-time purchase（一次性付款）
5. 儲存後複製產品的 Checkout URL（格式：https://你的店名.lemonsqueezy.com/checkout/buy/產品ID）

第三步：取得 API Key 和 Webhook Secret
1. 點右上角頭像 → Settings → API
2. 複製 API Key（存到 .env 的 LEMONSQUEEZY_API_KEY）
3. 點左側 Webhooks → Add Webhook
4. 填入：
   - URL：https://worldcup-api-jryd.onrender.com/webhook/lemonsqueezy
   - Events：勾選 order_created
   - 儲存後複製 Signing Secret（存到 .env 的 LEMONSQUEEZY_WEBHOOK_SECRET）

第四步：更新環境變數
後端 .env（本機）加入：
    LEMONSQUEEZY_WEBHOOK_SECRET=你的signing_secret
    LEMONSQUEEZY_API_KEY=你的api_key

Render Dashboard → 你的服務 → Environment 加入同樣兩個變數

前端 .env.local（本機）加入：
    NEXT_PUBLIC_LEMONSQUEEZY_CHECKOUT_URL=https://你的店名.lemonsqueezy.com/checkout/buy/產品ID

Vercel Dashboard → 你的專案 → Settings → Environment Variables 加入同樣變數

第五步：在前端比賽列表頁面使用 MemberGate
找到 worldcup-frontend 的比賽列表頁，在 Pro 鎖定的地方改成：

    import MemberGate from "@/components/MemberGate";

    {userTier === "pro" ? (
      <div>詳細賠率...</div>
    ) : (
      <MemberGate userEmail={user?.email} />
    )}

第六步：Push 前端更新
    cd C:\Users\samli\Desktop\worldcup-frontend
    git add .
    git commit -m "feat: add LemonSqueezy upgrade button and MemberGate"
    git push

================================================================
任務 C：測試 Webhook（本機）
================================================================

第一步：安裝 ngrok
1. 前往 https://ngrok.com 免費註冊
2. 下載 Windows 版本
3. 解壓縮後在 CMD 執行：
    ngrok http 8000
4. 複製 ngrok 給你的 https URL（例如：https://abc123.ngrok.io）

第二步：暫時把 Webhook URL 改成 ngrok URL
到 LemonSqueezy Dashboard → Webhooks
把 URL 改成：https://abc123.ngrok.io/webhook/lemonsqueezy

第三步：啟動本機後端
    cd C:\Users\samli\Desktop\worldcup_api
    venv\Scripts\activate
    uvicorn app.main:app --reload --port 8000

第四步：在 LemonSqueezy 觸發測試
到 LemonSqueezy Dashboard → Webhooks → 你的 Webhook → Send Test
選擇 order_created 事件，填入你的測試 email

第五步：確認 Supabase 更新
到 Supabase Dashboard → Table Editor → users
確認剛才測試的 email 的 tier 變成 pro

第六步：測試完成後
把 LemonSqueezy Webhook URL 改回：
    https://worldcup-api-jryd.onrender.com/webhook/lemonsqueezy

================================================================
完成後還要做的事（開賽前）
================================================================

1. 把 SUPABASE_SERVICE_KEY 確認已更新到 Render 環境變數
   （之前提醒過要重新產生 key）

2. 建立一個真實 Pro 測試帳號，完整跑一次付款流程（用 Test Mode）

3. UptimeRobot 確認變綠（任務 A 完成後約 10 分鐘）

================================================================
貼給 DeepSeek 的起手式（每次新對話先貼這段）
================================================================

我有一個 FIFA World Cup 2026 數據分析網站。

後端：Python FastAPI，部署在 Render（https://worldcup-api-jryd.onrender.com）
前端：Next.js，部署在 Vercel（https://worldcup-frontend-pi.vercel.app）
資料庫：Supabase（PostgreSQL）
作業系統：Windows
後端路徑：C:\Users\samli\Desktop\worldcup_api
前端路徑：C:\Users\samli\Desktop\worldcup-frontend

已完成：JWT 認證、會員分層（free/pro）、Poisson 預測模型、
賠率整合（Pinnacle + Bet365）、前端比賽列表 + 預測顯示、
Render + Vercel 部署、UptimeRobot 防睡眠。

現在要做：[說明你要做的任務]

請一步一步帶我，Windows CMD 指令，完成每一步我會告訴你再繼續。
