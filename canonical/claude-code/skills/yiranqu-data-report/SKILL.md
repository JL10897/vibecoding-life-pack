---
name: yiranqu-data-report
description: "yiranqu's data analysis HTML report design system (Morandi tones). Use this skill when building data analysis dashboards, reports, or interactive HTML pages. Defines the complete visual language: color palette (Morandi tones), typography hierarchy, card/section/chart layout, tag/badge system, parent-child content hierarchy with collapsible details, Chart.js integration patterns, and interactive simulator design. Triggers on: creating HTML reports, data dashboards, analysis pages, visualization layouts."
description_zh: "yiranqu 数据分析报告设计系统"
description_en: "yiranqu data report style guide"
disable: false
agent_created: true
---

# yiranqu-data-report — 数据分析HTML报告设计系统

一套完整的数据分析可视化HTML报告设计规范，适用于游戏数据分析、业务指标看板、实验报告等场景。

## When to use

- 构建数据分析HTML报告/仪表盘
- 需要可视化展示统计数据、分布图、漏斗图、归因分析
- 需要交互式模拟器（滑块/开关→实时图表联动）
- 需要多Tab多层级的数据展示
- 用户要求"莫兰迪色系"或"数据报告"风格

## 1. 色彩系统（Morandi Palette）

### 1.1 基础色板

```
背景色
  页面背景:  #f5f3f0（暖灰米色）
  卡片/Section: #fff
  代码/Note背景: #faf8f5 / #faf9f7
  高亮行背景: #f5f0fa（浅紫）/ #fdf0ee（浅红）/ #fef8ee（浅黄）/ #f0f4f8（浅蓝）

语义色（6色系统）
  v-purple:  #7b6b8f  — 主色调，用于command/指令/主指标
  v-green:   #6b8f71  — 正向/成功/增长
  v-blue:    #5a7a9a  — 中性信息/链接
  v-red:     #c75a3a  — 警告/负向/战斗（非纯红，偏砖红）
  v-orange:  #c48f3a  — 次级强调/PvE
  v-brown:   #8b7b6b  — 辅助/说明

扩展色
  浅紫:    #9b8fb5 / #b8a9c8  — command面积图/跟随
  浅橙:    #e8a87c  — 不耐烦impatient
  浅绿:    #8bab91  — 搜刮loot/joy
  浅蓝:    #7a9fb5  — 警戒wait/fear
  浅灰:    #bbb / #a0a0a0  — sadness/其他
  暖黄:    #c9a66b  — 管理manage/surprise
  neutral: #eae8e4  — 堆叠图中性色（要够浅不"压"其他色）
```

### 1.2 色彩使用规则

- **数据·颜色绑定**：同一数据维度在整个报告中使用同一颜色（如"战斗"始终用 `#d4816b`）
- **面积图**：颜色加 `0.3~0.5` 透明度（`rgba(123,107,143,0.35)`）
- **边框**：比填充色深一档，`borderWidth: 1`
- **文字色**：正文 `#3d3d3d`，次要 `#6a6a6a`，辅助 `#8a8a8a`，极弱 `#a0a0a0`
- **禁止纯黑纯白**：最深用 `#1a1a1a`，最浅用 `#faf8f5`

## 2. 排版层级

### 2.1 字号体系

```
H1 标题:      26px, font-weight:700, letter-spacing:-0.5px, color:#2c2c2c
H2 Section:   15px, font-weight:600, color:#3d3d3d
H3 子标题:    12-13px, font-weight:600, color:#1a1a1a
正文:          12-13px, color:#3d3d3d
表格:          10-12px
Note注释:      10-12px, color:#6a6a6a
Badge标签:     10px, font-weight:500
折叠Summary:   11-12px, color:#8a8a8a → hover:#5a7a9a → open:#5a7a9a
```

### 2.2 间距规范

```
页面padding:       24px
Section内padding:  24px
Section间距:       margin-bottom: 16px
卡片内padding:     14px
Grid间距:          gap: 10-16px
表格cell:          padding: 8px 10px（正常）/ 5-6px 8px（紧凑）
```

## 3. 组件规范

### 3.1 指标卡片（Card）

```html
<div class="card">
  <div class="card-label">指标名称</div>      <!-- 10px, #8a8a8a -->
  <div class="card-value v-purple">6.39</div>  <!-- 22px, font-weight:700 -->
  <div class="card-sub">补充说明</div>          <!-- 10px, #a0a0a0 -->
</div>
```
- 布局：`grid-template-columns: repeat(auto-fit, minmax(155px, 1fr))`
- 圆角：`12px`，阴影：`0 1px 3px rgba(0,0,0,.06)`

### 3.2 Section 白卡

```html
<div class="section">
  <h2>标题<span class="badge">200局抽样 · 0529</span></h2>
  <!-- 内容 -->
</div>
```
- 圆角 `12px`，白底，padding `24px`
- 阴影 `0 1px 3px rgba(0,0,0,.06)`

### 3.3 Badge标签

```html
<span class="badge">200局抽样 · 0529 · 2,539次</span>
```
- 样式：`font-size:10px; background:rgba(107,143,113,.12); color:#6b8f71; padding:2px 8px; border-radius:4px`
- 位置：紧跟h2/h3标题后，`margin-left:8px`
- 格式：`数据源 · 日期 · 数量`，用中文间隔号 `·` 分隔
- **不加括号**，不加emoji
- h2和h3都要生效：`.section h2 .badge, .section h3 .badge`

### 3.4 Note注释

```html
<div class="note">
  command 50%·neutral 34%·impatient 8%——玩家对Bot <strong>91%是中性或指令性</strong>语音
</div>
```
- 左侧3px竖线 `border-left:3px solid #d4c5b0`
- 背景 `#faf8f5`，圆角 `0 8px 8px 0`
- 用于**核心发现**的行内格式：`数据·数据·数据——结论`
- 不用框式卡片包裹核心发现

### 3.5 Grid布局

```css
.grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; align-items:center; }
.grid-3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; }
```
- 移动端自适应：`@media(max-width:768px) { grid-template-columns:1fr }`
- 表格与note左右排列时：`align-items:start`（顶部对齐）

### 3.6 Tab导航

```html
<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('tab-id', this)">标签名</button>
</div>
<div id="tab-id" class="tab-content active">...</div>
```
- 底部 `2px` 线，active色 `#5a7a9a`
- padding `10px 20px`，字号 `13px`

## 4. 父子层级与交互方式

### 4.1 层级结构

```
Tab（最外层）
  └─ Section（白卡，h2标题 + badge）
      ├─ Card Grid（指标卡片行）
      ├─ Chart + Table 并排（grid-2）
      ├─ 子模块（border-top分隔线 + h3标题 + badge）
      │   ├─ 内容表格/图表
      │   └─ <details>折叠展开
      │       ├─ summary（12px粗体，按场景用不同颜色）
      │       └─ 展开内容（table + note）
      └─ Note（行内核心发现）
```

### 4.2 折叠交互（details/summary）

```html
<details style="margin-bottom:10px">
  <summary style="font-size:12px;font-weight:600;color:#7b6b8f;cursor:pointer">
    原地等待 → 后续 action list（549次）
  </summary>
  <div style="padding:8px 0">
    <table>...</table>
    <div class="note">总结性结论</div>
  </div>
</details>
```

- 用于**子类型展开**：不同前序场景的详情
- summary颜色按类别区分（purple/red/blue/green/orange）
- **不加icon/emoji**
- 展开后包含：详情表格 + note总结

### 4.3 子模块嵌套

在同一个Section内，子分析模块用 `border-top:1px solid #eae8e4; padding-top:16px` 分隔：
```html
<div style="margin-top:20px;border-top:1px solid #eae8e4;padding-top:16px">
  <h3>子模块标题<span class="badge">数据标签</span></h3>
  <!-- 子模块内容 -->
</div>
```

### 4.4 类型标签（Lever Tag）

用于区分策略/参数的类别：
```html
<span class="lever-tag tag-intent">意图</span>
<span class="lever-tag tag-event">事件</span>
<span class="lever-tag tag-rearrange">Rearrange</span>
```
颜色映射：
- intent: `background:#f0e6fa; color:#7b6b8f`
- event: `background:#fef0e6; color:#c48f3a`
- rearrange: `background:#e6f0f5; color:#5a7a9a`

## 5. Chart.js 使用规范

### 5.1 通用配置

```javascript
// 必须内联Chart.js（不依赖CDN），放在<script>标签中
// 版本: Chart.js v4.4.x UMD

// Doughnut饼图
new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['类别A 45.4%', '类别B 26.0%'],  // label中带百分比
    datasets: [{
      data: [269, 154],
      backgroundColor: ['#c75a3a', '#7b6b8f'],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '45%~55%',  // 环形
    plugins: {
      legend: { position: 'bottom', labels: { font: { size: 9~10 }, padding: 6~8 } }
    }
  }
});
```

### 5.2 Tooltip百分比

```javascript
plugins: {
  tooltip: {
    callbacks: {
      label: function(ctx) {
        var total = 231714;
        var val = ctx.raw;
        return val.toLocaleString() + ' 次 (' + (val/total*100).toFixed(1) + '%)';
      }
    }
  }
}
```

### 5.3 堆叠面积图

```javascript
type: 'line',
fill: true,
// 颜色按情绪/行为类别分配
// Y轴堆叠：stacked: true
// legend在top，padding:8
```

### 5.4 柱状图

```javascript
type: 'bar',
borderRadius: 3,  // 圆角柱
// 水平柱状图：indexAxis: 'y'
```

## 6. 交互式模拟器设计

### 6.1 布局

```
左侧控制面板(400px固定宽) | 右侧结果区(自适应)
```

### 6.2 控制面板（Lever）

```html
<div class="lever active">  <!-- active时紫色边框+浅紫底 -->
  <div class="lever-header">
    <span class="lever-name">策略名称</span>
    <span class="lever-tag tag-event">类别</span>
  </div>
  <div class="lever-desc">策略描述</div>
  <div class="lever-row">
    <input type="checkbox" checked>  <!-- 开关 -->
    <input type="range" min="0" max="100">  <!-- 滑块 -->
    <span class="lever-value">数值</span>
  </div>
  <div class="lever-detail">数据细节（9px灰色，虚线分隔）</div>
  <div class="lever-impact">影响量化（10px绿色粗体）</div>
</div>
```

### 6.3 结果区指标卡

```html
<div class="metric">
  <div class="metric-label">指标名</div>
  <div class="metric-value v-green">5.89</div>
  <div class="metric-sub">补充说明</div>
</div>
```
- 值: `22px, font-weight:800`
- 颜色动态变化（reduction>5%→绿，>0%→橙，=0→灰）

### 6.4 漏斗图（HTML/CSS实现）

```html
<div class="funnel-step">
  <div class="funnel-label">步骤名</div>
  <div class="funnel-bar" style="width:80%;background:#7b6b8f">数值</div>
  <div class="funnel-value">占比</div>
</div>
```
- bar宽度按百分比动态设置
- `transition: width .6s ease` 平滑动画

## 7. 数据展示规范

### 7.1 表格

- 表头：`background:#f9f8f6; color:#6a6a6a; font-weight:500`
- 分割线：`border-bottom:1px solid #eee`（表头）/ `#f0f0f0`（行）
- 代码/action用 `font-family:monospace`
- 重要数据用 `<strong>` 加粗
- 高亮用 `.highlight`（`color:#c75a3a; font-weight:600`）

### 7.2 行内核心发现

不用框/卡片，用 `.note` 格式：
```
数据A X%·数据B Y%·数据C Z%——<strong>结论性文字</strong>
```

### 7.3 数据精度

- 百分比：1位小数（`45.4%`）
- QPM/频率：2位小数（`6.39`）
- 次数：千分位分隔（`17,839`）
- 时间：`X.Xmin` / `Xs`

### 7.4 action list展示

用monospace + 简化参数：
```
walk(pos); condition_nearby_enemy(); battle()
walk(target); open_box(pos); loot_box() ×2
```

## 8. 响应式设计

```css
@media(max-width:900px) {
  .main-grid { grid-template-columns: 1fr; }  /* 模拟器两栏→单栏 */
}
@media(max-width:768px) {
  .grid-2, .grid-3 { grid-template-columns: 1fr; }  /* 报告Grid→单栏 */
}
```

## 9. 自包含原则

- **Chart.js必须内联**（不依赖CDN），放在HTML开头的`<script>`中
- **数据必须内联**（JSON直接赋值给JS变量），不用fetch
- 单个HTML文件 = 完整可离线运行的报告
- 文件大小控制在500KB以内

## Pitfalls

- Badge不加括号、不加emoji，格式固定为 `数据源 · 日期 · 数量`
- Note中的核心发现用"数据·数据——结论"行内格式，不用框
- 折叠details中的summary不加icon
- 堆叠面积图的neutral颜色要足够浅（`#eae8e4`），避免"压"住其他色
- Chart.js的doughnut label中自带百分比（`'类别 45.4%'`）
- 表格与note并排时用 `align-items:start` 保持顶部对齐
- 颜色语义一致：同一数据维度在全报告中颜色不变

## Verification

- [ ] 页面背景色是否为 `#f5f3f0`
- [ ] 所有Section用白卡+圆角12px+阴影
- [ ] Badge使用统一格式（无括号、·分隔）
- [ ] Chart.js已内联（无CDN依赖）
- [ ] 移动端Grid自适应生效
- [ ] 折叠交互正常（details/summary）
- [ ] 颜色语义一致性检查
- [ ] 核心发现用note行内格式而非框
