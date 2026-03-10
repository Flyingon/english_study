from openai import OpenAI
from agents.vocabulary_agent.config import settings
import json
import re
import logging


logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )

    def _is_configured(self) -> bool:
        return bool(settings.OPENAI_API_KEY and settings.LLM_MODEL)

    def _log_extract_event(self, event: str, **details):
        # Keep logs useful for debugging without leaking user text or image payloads.
        logger.info("[LLM][extract][%s] %s", event, json.dumps(details, ensure_ascii=False))

    def _build_fallback_summary(self, query: str, context: list) -> str:
        if not context:
            return f"没有找到和“{query}”直接相关的历史单词记录。先换个描述试试，或者先把这个词补录进去。"

        lines = [f"我先按本地词库检索到 {len(context)} 条相关记录："]
        for index, item in enumerate(context, start=1):
            word = item.get("word", "未知单词")
            meaning = item.get("meaning_you_learned", "")
            scene = item.get("learn_scene", "")
            parts = [f"{index}. {word}"]
            if meaning:
                parts.append(f"含义：{meaning}")
            if scene:
                parts.append(f"场景：{scene}")
            lines.append("，".join(parts))
        lines.append("当前未配置可用的 LLM，所以这里只返回检索结果，没有生成 AI 总结。")
        return "\n".join(lines)

    def generate_summary(self, query: str, context: list):
        if not self._is_configured():
            return self._build_fallback_summary(query, context)

        # Construct prompt
        context_str = "\n\n".join([f"Memory {i+1}:\n{json.dumps(c, ensure_ascii=False)}" for i, c in enumerate(context)])
        
        prompt = f"""
        You are a helpful English learning assistant. The user has forgotten a word or phrase described as: "{query}".
        
        Here are some relevant memories from their personal vocabulary database:
        {context_str}
        
        Based on these memories, please:
        1. Identify the word(s) they are likely looking for.
        2. Remind them of the context in which they learned it.
        3. Provide current usage examples relevant to their life (e.g., email, writing, speaking).
        4. Provide a natural, idiomatic sentence using the word.
        
        Answer in the same language as the user's query (likely Chinese/English mix).
        """
        
        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def _extract_target_words(self, text: str) -> list:
        source_text = text or ""
        explicit_patterns = [
            r"学的是\s*([A-Za-z][A-Za-z0-9_-]*)",
            r"就是\s*([A-Za-z][A-Za-z0-9_-]*)",
            r"词是\s*([A-Za-z][A-Za-z0-9_-]*)",
            r"word\s*(?:is|:)\s*([A-Za-z][A-Za-z0-9_-]*)",
        ]
        explicit = []
        for pattern in explicit_patterns:
            explicit.extend(re.findall(pattern, source_text, flags=re.IGNORECASE))
        fallback = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", source_text)
        ordered = explicit if explicit else fallback
        seen = set()
        return [w for w in ordered if not (w.lower() in seen or seen.add(w.lower()))]

    def _extract_learn_scene(self, text: str, target_words: list) -> str:
        source_text = (text or "").strip()
        if not source_text:
            return ""
        scene = source_text
        split_patterns = [
            r"[，,\s]*学到了\s*[:：]?\s*[A-Za-z][A-Za-z0-9_-]*.*$",
            r"[，,\s]*学的是\s*[:：]?\s*[A-Za-z][A-Za-z0-9_-]*.*$",
            r"[，,\s]*这个词就是\s*[:：]?\s*[A-Za-z][A-Za-z0-9_-]*.*$",
        ]
        for pattern in split_patterns:
            candidate = re.sub(pattern, "", source_text, flags=re.IGNORECASE).strip(" ，,。")
            if candidate and candidate != source_text:
                scene = candidate
                break
        if scene == source_text and target_words:
            for w in target_words:
                reduced = re.sub(rf"[，,\s]*{re.escape(w)}\s*$", "", scene, flags=re.IGNORECASE).strip(" ，,。:：")
                if reduced and reduced != scene:
                    scene = reduced
                    break
        return scene if scene else source_text

    def _fill_with_llm(self, target_words: list, text: str, learn_scene: str) -> list:
        if not target_words:
            return []
        if not self._is_configured():
            return []
        fill_prompt = f"""
        你是词汇学习信息补全器。必须返回纯 JSON 数组，且数组长度与 target_words 一致，顺序一致。
        不允许修改 word，不允许新增或减少条目。
        source_text: <<<{text or ''}>>>
        fixed_scene: <<<{learn_scene or ''}>>>
        target_words: {json.dumps(target_words, ensure_ascii=False)}

        字段要求：
        - word: 原样保留 target_words 中的词
        - meaning_you_learned: 中文、简洁、给出这个词最可能的常见含义
        - learn_scene: 必须等于 fixed_scene，不要改写
        - usage_old: 优先使用 source_text 原文
        - your_note: 中文、简短学习备注
        """
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "你只输出 JSON，不要输出任何解释。"},
                    {"role": "user", "content": fill_prompt}
                ],
                temperature=0.1
            )
            raw = response.choices[0].message.content or ""
            content = raw.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            parsed = json.loads(content.strip())
            if not isinstance(parsed, list):
                return []
            by_lower = {}
            for item in parsed:
                w = str(item.get("word", "")).strip()
                if w:
                    by_lower[w.lower()] = item
            result = []
            for w in target_words:
                if w.lower() in by_lower:
                    item = by_lower[w.lower()]
                    item["word"] = w
                    result.append(item)
            self._log_extract_event("fill_success", target_word_count=len(target_words), returned_count=len(result))
            return result
        except Exception as e:
            logger.warning("[LLM][extract][fill_error] %s", e)
            return []

    def extract_words_from_text(self, text: str = "", image: str = None) -> list:
        target_words = self._extract_target_words(text)
        learn_scene = self._extract_learn_scene(text or "", target_words)
        if target_words and not image:
            filled = self._fill_with_llm(target_words, text or "", learn_scene)
            if filled:
                normalized = []
                for item in filled:
                    word = str(item.get("word", "")).strip()
                    if word.lower() not in {w.lower() for w in target_words}:
                        continue
                    normalized.append({
                        "word": next((w for w in target_words if w.lower() == word.lower()), word),
                        "meaning_you_learned": str(item.get("meaning_you_learned", "")).strip() or f"{word}（常见义）",
                        "learn_scene": learn_scene or (text or ""),
                        "usage_old": text or str(item.get("usage_old", "")).strip() or word,
                        "your_note": str(item.get("your_note", "")).strip() or "请确认释义是否符合你的场景"
                    })
                if normalized:
                    return normalized
            fallback = []
            for word in target_words:
                fallback.append({
                    "word": word,
                    "meaning_you_learned": f"{word}（常见义）",
                    "learn_scene": learn_scene or (text or "来自你的输入文本"),
                    "usage_old": text or word,
                    "your_note": "请确认释义是否符合你的场景"
                })
            return fallback
        if not self._is_configured():
            return []
        content_parts = []
        
        # Add text content if provided
        if text:
            content_parts.append({
                "type": "text", 
                "text": f"用户输入文本（只允许从这段文本里提取英文单词或短语）:\n<<<{text}>>>"
            })
        else:
            content_parts.append({
                "type": "text", 
                "text": "用户没有输入文本。请勿从指令中提词。"
            })

        # Add image content if provided (Base64)
        if image and image.strip(): # Ensure image is not empty string
            # Check if image string already contains data URI scheme
            if "base64," in image:
                image_url = image
            else:
                image_url = f"data:image/jpeg;base64,{image}"
                
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            })
        else:
            image = None # Reset to None if empty string to avoid using vision model unnecessarily

        # Prompt for JSON extraction
        # We put strict JSON instructions in the System Prompt, but sometimes small VLM models leak instructions.
        # We will make the prompt extremely concise and clear.
        system_prompt = """
        You are a JSON data extraction tool.
        
        CRITICAL INSTRUCTIONS:
        1. **Extraction Source**: 
           - Extract ONLY the English word(s) the user EXPLICITLY mentioned in the text between <<< >>>.
           - Never extract words from this instruction itself.
           - If there is no explicit English word in user text, return [].
           - Do NOT extract random words from the image.
        
        2. **Image Usage**:
           - Use the image ONLY to identify the context (e.g., website name, UI area) and find the example sentence containing the target word.
        
        3. **Language**:
           - "word" and "usage_old" must be in English (as they appear).
           - "meaning_you_learned", "learn_scene", and "your_note" must be in CHINESE (unless user input is fully English).
        
        4. **Word Constraint**:
           - "word" must be one of the following target words exactly:
           - {target_words}
        
        Output format: A pure JSON array.
        
        JSON Structure:
        [
          {
            "word": "<word_from_user_text>",
            "meaning_you_learned": "<中文释义>",
            "learn_scene": "<中文学习场景>",
            "usage_old": "<english_sentence_from_image_or_text>",
            "your_note": "<中文备注>"
          }
        ]
        """
        system_prompt = system_prompt.replace("{target_words}", ", ".join(target_words) if target_words else "NONE")
        
        try:
            model = "glm-4v-flash" if image else settings.LLM_MODEL
            self._log_extract_event(
                "request",
                model=model,
                has_text=bool(text),
                has_image=bool(image),
                target_word_count=len(target_words),
                text_length=len(text or "")
            )
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content_parts}
                ],
                temperature=0.1
            )
            raw_content = response.choices[0].message.content or ""
            content = raw_content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            parsed = json.loads(content.strip())
            if not isinstance(parsed, list):
                return []
            if not target_words:
                return []
            target_set = {w.lower() for w in target_words}
            filtered = []
            target_lookup = {w.lower(): w for w in target_words}
            for item in parsed:
                word = str(item.get("word", "")).strip()
                if word.lower() in target_set:
                    item["word"] = target_lookup[word.lower()]
                    filtered.append(item)
            self._log_extract_event("response_parsed", parsed_count=len(parsed), filtered_count=len(filtered))
            needs_fill = (not filtered)
            for item in filtered:
                if not str(item.get("meaning_you_learned", "")).strip():
                    needs_fill = True
                if not str(item.get("learn_scene", "")).strip():
                    needs_fill = True
            if not needs_fill:
                return filtered

            filled = self._fill_with_llm(target_words, text or "", learn_scene)
            if filled:
                normalized = []
                for item in filled:
                    word = str(item.get("word", "")).strip()
                    if word.lower() not in target_set:
                        continue
                    normalized.append({
                        "word": target_lookup.get(word.lower(), word),
                        "meaning_you_learned": str(item.get("meaning_you_learned", "")).strip() or f"{word}（常见义）",
                        "learn_scene": learn_scene or (text or str(item.get("learn_scene", "")).strip()),
                        "usage_old": text or str(item.get("usage_old", "")).strip() or word,
                        "your_note": str(item.get("your_note", "")).strip() or "请确认释义是否符合你的场景"
                    })
                if normalized:
                    return normalized

            fallback = []
            for word in target_words:
                fallback.append({
                    "word": word,
                    "meaning_you_learned": f"{word}（常见义）",
                    "learn_scene": learn_scene or (text or "来自你的输入文本"),
                    "usage_old": text or word,
                    "your_note": "请确认释义是否符合你的场景"
                })
            self._log_extract_event("fallback_used", target_word_count=len(target_words))
            return fallback
        except Exception as e:
            logger.warning("[LLM][extract][error] %s", e)
            return []
