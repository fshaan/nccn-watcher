# TODOS

## Enhancement: 多类型 PDF 下载
- **Priority**: Low
- **Status**: Planned
- **What**: 支持下载 detail 页面上的其他 PDF 类型（Evidence Blocks、Frameworks、翻译版、患者指南）
- **Why**: 目前只下载主指南 PDF，但 detail 页面有 5-6 种 PDF 可下载
- **Added**: 2026-03-20 by /plan-eng-review

## Vision: 多指南体系支持（ESMO、CSCO、ASCO）
- **Priority**: Low (v2+)
- **Status**: Planned (post-MVP validation)
- **What**: 扩展监控范围到 ESMO、CSCO、ASCO 等其他肿瘤临床指南体系
- **Why**: 不同地区医生关注不同指南体系（如中国医生关注 CSCO），扩大工具覆盖面
- **Risk**: 每个指南体系网站结构不同，需单独开发爬虫
- **Depends on**: MVP 在 NCCN 上验证模式成功后
- **Added**: 2026-03-20 by /plan-eng-review

## Completed

### NCCN 指南索引缓存
- **Completed**: v1.2 (2026-03-20)
- **What**: 爬取 NCCN 92 个 detail 页面构建完整 PDF URL 索引（7 天 YAML 缓存），用户可通过 `download_guideline` 按名搜索并下载任意指南
- **Resolved by**: `fetch_pdf_index()` + `browse_guidelines` + `find_guideline` + `download_guideline` MCP tools
