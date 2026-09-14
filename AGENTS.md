# Agent & Coding Guidelines

本文件定義本專案（momo-web-testing-assignment）的開發、測試與維護原則。所有在此專案工作的工程師與 AI Agent 皆須嚴格遵守以下規範。

---

## 核心原則 (Core Principles)

1. **優先追求易讀性**：
   - 程式碼是寫給人看的，測試程式更是產品行為的活文件。
   - 確保任何工程師在 Code Review 時，能快速理解「這段 code 在測什麼、為什麼這樣寫」。

2. **避免 Over-Engineering 與過早抽象**：
   - 先解決具體問題，不要為了「可能未來會用」而預先建立過度設計或額外抽象層。
   - 保持最小必要程式碼，去除不切實際的複雜度。

3. **職責單一與清楚命名**：
   - Function 與 Class 名稱必須能直接表達其意圖與用途。
   - 一個 Function 只處理一個清楚且專一的責任。

---

## 測試撰寫規範 (Test Authoring Guidelines)

1. **測試目的直觀清晰**：
   - 每個 testcase 的名稱與步驟應能直觀表達測試情境與預期結果（Arrange-Act-Assert）。
   - 避免將 Locator、操作行為（Actions）與斷言（Assertions）全部揉合在單一雜亂的長段落中，保持適當分段與清晰結構。

2. **Page Object 與抽象時機**：
   - 只有當 UI 操作重複出現且具有明確跨測試語意時，才抽成 Page Object 或共用函式。
   - 避免一開始建立空泛或過早的包裝。

3. **等待與斷言策略**：
   - **嚴禁使用 `time.sleep()`**。
   - 優先運用 Playwright 的 Auto-waiting 機制，並搭配明確的 State-based Assertion（例如 `expect(locator).to_be_visible()`、`expect(page).to_have_title(...)`）。

4. **避免 Magic Value**：
   - 測試資料、重要 URL、預期值若具特殊語意，應使用具意義的常數或變數名稱，切勿在程式碼中散落未說明的常數值。

---

## 專案架構原則 (Project Structure Principles)

- **保持結構小而清楚**：
  - 專案結構應隨實際功能需求演進，不預先建立空的目錄架構。
  - **不要一開始建立大量空的目錄**（例如未使用的 `pages/`, `components/`, `utils/`, `services/`, `helpers/` 等）。
  - 若目前無實際使用的模組或目錄，一律不建立。
