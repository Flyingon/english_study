英语个人记忆智能体 — 技术方案文档
1. 项目定位
解决痛点：英语单词学过就忘、想用想不起来、不知道在真实场景 / 文章中怎么用。核心功能：
记录单词 + 学习场景 + 来源 + 参考资料（文章 / 链接 / 片段）
按自然语言描述召回遗忘单词（语义检索）
基于个人历史记忆，给出地道用法、造句、对比
一句话架构：第三方 LLM API + 向量检索 + 本地向量库（Chroma）不训练模型、不部署本地大模型、快速开发、稳定上线。
2. 技术栈（固定，不许改）
后端：Python + FastAPI
向量数据库：Chroma（本地文件型，零部署）
大模型能力：第三方 LLM API（生成、造句、总结）
向量能力：第三方 Embedding API
存储：所有个人记忆存在本地 Chroma，不上传私有库
3. 数据结构（直接用）
3.1 单条单词记忆结构（存入 Chroma metadata）
json
{
  "word": "ambiguous",
  "phonetic": "æmˈbɪɡjuəs",
  "meaning_you_learned": "模糊的、不明确的、有歧义的",
  "learn_scene": "外刊阅读/工作文档/美剧/课程",
  "learn_source": "《经济学人》2026-03-02",
  "reference_type": "web/article/book/pdf",
  "reference_url": "https://...",
  "reference_title": "文章标题",
  "reference_snippet": "原文段落...",
  "usage_old": "当时学的例句",
  "usage_now": "现在适用场景：邮件/写作/口语",
  "your_note": "易混淆、词根、个人理解",
  "create_time": "2026-03-02 15:30:00",
  "review_count": 0,
  "last_review_time": ""
}
3.2 Chroma 存储结构（必须遵守）
每条记录固定四部分：
id：唯一标识
embedding：向量（由 Embedding API 生成）
document：用于检索的拼接文本（单词 + 释义 + 场景 + 用法 + 片段）
metadata：上面完整 JSON
4. 接口协议（4 个核心接口）
4.1 添加单词记忆
地址：/api/word/add
入参：上面完整单词 JSON
出参：code、msg、record_id、create_time
4.2 语义召回遗忘单词（核心）
地址：/api/word/retrieve
入参：
json
{"query":"描述你忘了的词","filter_scene":"","top_k":3}
出参：匹配列表 + AI 总结
4.3 单词详情
地址：/api/word/detail
入参：record_id
出参：完整记忆信息
4.4 词库列表（分页）
地址：/api/word/list
入参：page、size、keyword、learn_scene
出参：分页列表
5. 核心流程（AI 必须按这个写）
5.1 录入流程
接收用户填写的单词信息
拼接 document 检索文本
调用 Embedding API 得到向量
存入 Chroma：id + embedding + document + metadata
5.2 召回流程（最关键）
用户自然语言查询 → 调用 Embedding
Chroma 做相似度检索，返回 top3～5 条个人记忆
将检索结果拼进 Prompt
调用 LLM API 输出：
你学过的单词
当时场景
现在怎么用
地道句子
6. 为什么不用训练模型（写在方案里）
通用 LLM 已经具备完整语言能力，专用模型效果不如它
训练垂直 Transformer：数据贵、算力贵、周期长、难迭代
本方案：LLM 负责智能 + Chroma 负责记忆，成本极低、迭代极快
所有私有数据存在本地，隐私安全
7. 交付要求（给 AI 开发者看）
实现以上 4 个接口
实现 Chroma 增、删、检索逻辑
实现拼接 document、Prompt 模板
提供可运行的 Python 最小版本
配置文件分离 API Key，不硬编码