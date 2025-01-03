# ComfyUI 通用翻译节点

这是一个用于 ComfyUI 的通用翻译节点插件，支持多语言互译和多 LLM 模型配置。

## 功能特点

- 支持多语言互译（中文、英语、日语、韩语等）
- 支持多个 LLM 模型（DeepSeek、OpenAI 等）
- 支持自定义固定词组映射
- 完整的错误处理和日志记录

## 安装方法

1. 将此文件夹复制到 ComfyUI 的 `custom_nodes` 目录下
2. 配置 `config.json` 文件中的 API 密钥

## 使用方法

在 ComfyUI 中，你可以找到名为"通用翻译器"或"UniversalTranslator"的节点，它包含以下输入：

- 源语言：选择原文语言
- 目标语言：选择目标语言
- LLM：选择要使用的 AI 模型
- 输入文本：要翻译的文本内容
- 固定词组：需要特殊处理的词组对应关系

### 固定词组示例：

```
专有名词=Proper Noun
技术术语=Technical Term
```

## 配置说明

在 `config.json` 中配置您的 LLM 模型(允许配置多个)：

```json
{
    "llm": {
        "deepseek": {
            "api_key": "your-api-key",
            "api_base": "llm-base_url",
            "model": "model-name",
            "temperature": 1.3,
            "max_tokens": 8192
        }
    }
}
```

## 注意事项

- 使用前请确保已正确配置大模型
- 翻译服务需要网络连接
- 不同 LLM 模型可能有不同的速度和质量表现
- 固定词组的优先级高于模型翻译
- 作为翻译使用temperature各个模型中都有不同的推荐值，请参考各家的官方api文档。

## 支持的语言

- 中文 (Chinese)
- 英语 (English)
- 日语 (Japanese)
- 韩语 (Korean)
- 法语 (French)
- 德语 (German)
- 西班牙语 (Spanish)
- 俄语 (Russian)
