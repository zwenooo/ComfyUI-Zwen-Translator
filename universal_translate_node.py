import sys
import os
import json
import logging
from openai import OpenAI

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

class UniversalTranslator:
    def __init__(self):
        try:
            self.config = self._load_config()
            self.models = {}
            self._initialize_ai_clients()
            logger.info("成功初始化AI客户端")
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            raise

    @classmethod
    def INPUT_TYPES(s):
        try:
            config = s._load_config()
            languages = list(config["supported_languages"].keys())
            model_names = list(config["llm"].keys())
            
            return {
                "required": {
                    "source_language": (languages, {
                        "default": languages[0],  # 默认选择第一个语言
                        "display": "源语言"  # 显示名称
                    }),
                    "target_language": (languages, {
                        "default": languages[1] if len(languages) > 1 else languages[0],  # 默认选择第二个语言
                        "display": "目标语言"
                    }),
                    "llm": (model_names, {
                        "default": model_names[0],  # 默认选择第一个模型
                        "display": "LLM"
                    }),
                    "input_text": ("STRING", {
                        "multiline": True,
                        "default": "",
                        "placeholder": "请输入要翻译的文本",
                        "display": "输入文本"
                    }),
                    "fixed_terms": ("STRING", {
                        "multiline": True,
                        "default": "",
                        "placeholder": "输入格式：原文=译文（每行一个）",
                        "display": "固定词组"
                    }),
                }
            }
        except Exception as e:
            logger.error(f"获取输入类型失败: {str(e)}")
            return {"required": {"error": ("STRING", {"default": str(e)})}}

    RETURN_TYPES = ("STRING",)
    FUNCTION = "translate"
    CATEGORY = "zwen"
    RETURN_NAMES = ("translated_text",)

    @staticmethod
    def _load_config():
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            raise

    def _initialize_ai_clients(self):
        for model_name, model_config in self.config["llm"].items():
            try:
                self.models[model_name] = OpenAI(
                    api_key=model_config["api_key"],
                    base_url=model_config["api_base"]
                )
            except Exception as e:
                logger.error(f"初始化{model_name}客户端失败: {str(e)}")

    def _get_system_prompt(self, source_lang, target_lang):
        return f"""You are a professional translator.
Your task is to translate from {source_lang} to {target_lang} while maintaining the following principles:
1. Maintain the original meaning and tone
2. Use natural and fluent {target_lang}
3. DO NOT translate any text between [KEEP] tags. Example: [KEEP]word[/KEEP] should remain exactly as is
4. Keep any technical terms accurate
5. Preserve the formatting and punctuation where appropriate
6. Do not add or remove information

Respond with ONLY the translation, no explanations or other text."""

    def parse_fixed_terms(self, fixed_terms_str):
        fixed_terms = {}
        if fixed_terms_str.strip():
            for line in fixed_terms_str.strip().split('\n'):
                if '=' in line:
                    source, target = line.split('=', 1)
                    fixed_terms[source.strip()] = target.strip()
        return fixed_terms

    def apply_fixed_terms(self, text, fixed_terms):
        for source, target in fixed_terms.items():
            text = text.replace(source, f"[KEEP]{target}[/KEEP]")
        return text

    def restore_fixed_terms(self, text):
        import re
        pattern = r'\[KEEP\](.*?)\[/KEEP\]'
        return re.sub(pattern, r'\1', text)

    def translate_text(self, text, model_name, source_lang, target_lang):
        try:
            model_config = self.config["llm"][model_name]
            client = self.models[model_name]
            
            messages = [
                {
                    "role": "system", 
                    "content": self._get_system_prompt(source_lang, target_lang)
                },
                {"role": "user", "content": text}
            ]
            
            response = client.chat.completions.create(
                model=model_config["model"],
                messages=messages,
                temperature=model_config["temperature"],
                max_tokens=model_config["max_tokens"]
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"翻译过程出错: {str(e)}")
            return f"Translation Error: {str(e)}"

    def translate(self, source_language, target_language, llm, input_text, fixed_terms):
        try:
            # 解析固定词对
            fixed_terms_dict = self.parse_fixed_terms(fixed_terms)
            logger.info(f"固定词对: {fixed_terms_dict}")
            
            # 应用固定词替换
            text_with_fixed = self.apply_fixed_terms(input_text, fixed_terms_dict)
            logger.info(f"应用固定词替换后的文本: {text_with_fixed}")
            
            # 获取语言的英文名称
            source_lang = self.config["supported_languages"][source_language]
            target_lang = self.config["supported_languages"][target_language]
            
            # 翻译文本
            translated_text = self.translate_text(
                text_with_fixed, 
                llm,
                source_lang,
                target_lang
            )
            logger.info(f"翻译后的文本: {translated_text}")
            
            # 恢复固定词标记
            final_text = self.restore_fixed_terms(translated_text)
            logger.info(f"最终文本: {final_text}")
            
            return (final_text,)
        except Exception as e:
            logger.error(f"翻译处理过程出错: {str(e)}")
            return (f"Error: {str(e)}",)

# 注册节点
NODE_CLASS_MAPPINGS = {
    "UniversalTranslator": UniversalTranslator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UniversalTranslator": "通用翻译器"
}

# 测试代码
if __name__ == "__main__":
    logging.info("正在测试翻译节点...")
    translator = UniversalTranslator()
    result = translator.translate(
        source_language="中文",
        target_language="日语",
        llm="deepseek",
        input_text="你是大可爱吗？",
        fixed_terms="大可爱=XXX"
    )
    print(result[0])  