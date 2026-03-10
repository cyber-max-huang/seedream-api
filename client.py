"""
Seedream API 客户端
基于火山引擎方舟大模型服务平台的图片生成 API
"""
import os
from typing import Optional, Union, List, Dict, Any
from dataclasses import dataclass

try:
    from volcenginesdkarkruntime import Ark
    from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions, ContentGenerationTool
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


@dataclass
class ImageResult:
    """图片生成结果"""
    url: Optional[str] = None
    b64_json: Optional[str] = None
    size: Optional[str] = None
    error: Optional[Dict[str, str]] = None


@dataclass
class GenerationUsage:
    """使用量统计"""
    generated_images: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    tool_usage_web_search: int = 0


@dataclass
class GenerationResponse:
    """图片生成响应"""
    model: str
    created: int
    data: List[ImageResult]
    usage: Optional[GenerationUsage] = None
    error: Optional[Dict[str, str]] = None


class SeedreamClient:
    """Seedream 图片生成 API 客户端"""
    
    # 支持的模型映射
    MODELS = {
        "5.0-lite": "doubao-seedream-5-0-260128",
        "4.5": "doubao-seedream-4-5-251128",
        "4.0": "doubao-seedream-4-0-250828",
        "3.0-t2i": "doubao-seedream-3-0-t2i",
        "3.0-i2i": "doubao-seededit-3-0-i2i",
    }

    def __init__(
        self, 
        api_key: str = None, 
        base_url: str = "https://ark.cn-beijing.volces.com/api/v3",
        proxy: str = None
    ):
        """
        初始化客户端
        
        Args:
            api_key: 火山引擎 API Key，默认从环境变量 ARK_API_KEY 获取
            base_url: API 基础 URL
            proxy: 代理地址，如 "http://127.0.0.1:1087" (可选，国内服务通常不需要)
        """
        if not SDK_AVAILABLE:
            raise ImportError("请安装 volcengine-python-sdk: pip install volcengine-python-sdk[ark]")
        
        self.api_key = api_key or os.getenv("ARK_API_KEY")
        if not self.api_key:
            raise ValueError("API Key 未设置，请通过参数传入或设置环境变量 ARK_API_KEY")
        
        self.base_url = base_url
        self.proxy = proxy
        
        # 创建客户端
        client_kwargs = {
            "base_url": base_url,
            "api_key": self.api_key,
        }
        
        # 添加代理配置
        if proxy:
            import httpx
            client_kwargs["http_client"] = httpx.Client(proxy=proxy)
        
        self._client = Ark(**client_kwargs)

    def _get_model_id(self, model: str) -> str:
        """获取模型 ID"""
        if model in self.MODELS:
            return self.MODELS[model]
        return model

    def generate(
        self,
        prompt: str,
        model: str = "doubao-seedream-5-0-260128",
        image: Union[str, List[str]] = None,
        size: str = "2K",
        output_format: str = None,
        response_format: str = "url",
        watermark: bool = False,
        sequential_image_generation: str = "disabled",
        max_images: int = None,
        seed: int = None,
        guidance_scale: float = None,
        stream: bool = False,
        web_search: bool = False,
        optimize_prompt_mode: str = None,
    ) -> GenerationResponse:
        """
        生成图片
        
        Args:
            prompt: 提示词
            model: 模型 ID 或别名 (5.0-lite, 4.5, 4.0, 3.0-t2i, 3.0-i2i)
            image: 输入图片 URL 或 Base64 或图片列表
            size: 图像尺寸 (如 "2K", "4K", "2048x2048")
            output_format: 输出格式 ("png" 或 "jpeg")，仅 5.0 lite 支持 png
            response_format: 返回格式 ("url" 或 "b64_json")
            watermark: 是否添加水印
            sequential_image_generation: 组图模式 ("auto" 或 "disabled")
            max_images: 最大生成图片数量 (仅当 sequential_image_generation="auto" 时有效)
            seed: 随机数种子 (仅 3.0 支持)
            guidance_scale: 文本权重 (仅 3.0 支持)
            stream: 是否流式输出 (仅 5.0 lite 支持)
            web_search: 是否启用联网搜索 (仅 5.0 lite 支持)
            optimize_prompt_mode: 提示词优化模式 (standard/fast，仅 5.0 lite 支持)
        
        Returns:
            GenerationResponse: 包含生成结果的响应对象
        """
        model = self._get_model_id(model)
        
        # 构建请求参数
        params = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "watermark": watermark,
            "sequential_image_generation": sequential_image_generation,
        }

        # 添加图片参数
        if image:
            params["image"] = image

        # 添加 output_format (仅 5.0 lite 支持)
        if output_format:
            params["output_format"] = output_format

        # 添加 response_format
        if response_format:
            params["response_format"] = response_format

        # 添加组图选项
        if sequential_image_generation == "auto" and max_images:
            params["sequential_image_generation_options"] = SequentialImageGenerationOptions(max_images=max_images)

        # 添加 seed (仅 3.0 支持)
        if seed is not None:
            params["seed"] = seed

        # 添加 guidance_scale (仅 3.0 支持)
        if guidance_scale is not None:
            params["guidance_scale"] = guidance_scale

        # 添加流式输出 (仅 5.0 lite 支持)
        if stream:
            params["stream"] = stream

        # 添加联网搜索 (仅 5.0 lite 支持)
        if web_search:
            params["tools"] = [ContentGenerationTool(type="web_search")]

        # 添加提示词优化 (仅 5.0 lite 支持)
        if optimize_prompt_mode:
            params["optimize_prompt_options"] = {"mode": optimize_prompt_mode}

        # 调用 API
        response = self._client.images.generate(**params)
        
        # 解析响应
        image_results = []
        for item in response.data:
            if hasattr(item, 'error') and item.error:
                image_results.append(ImageResult(error=item.error))
            else:
                image_results.append(ImageResult(
                    url=item.url if hasattr(item, 'url') else None,
                    b64_json=item.b64_json if hasattr(item, 'b64_json') else None,
                    size=item.size if hasattr(item, 'size') else None
                ))

        # 解析使用量
        usage = None
        if response.usage:
            usage = GenerationUsage(
                generated_images=response.usage.generated_images,
                output_tokens=response.usage.output_tokens,
                total_tokens=response.usage.total_tokens,
                tool_usage_web_search=getattr(response.usage.tool_usage, 'web_search', 0) if response.usage.tool_usage else 0
            )

        return GenerationResponse(
            model=response.model,
            created=response.created,
            data=image_results,
            usage=usage
        )

    def text_to_image(
        self,
        prompt: str,
        model: str = "5.0-lite",
        size: str = "2K",
        output_format: str = "png",
        watermark: bool = False,
    ) -> GenerationResponse:
        """
        文生图
        
        Args:
            prompt: 提示词
            model: 模型别名
            size: 图像尺寸
            output_format: 输出格式
            watermark: 是否添加水印
        
        Returns:
            GenerationResponse: 生成结果
        """
        return self.generate(
            prompt=prompt,
            model=model,
            size=size,
            output_format=output_format,
            watermark=watermark,
            sequential_image_generation="disabled"
        )

    def image_to_image(
        self,
        prompt: str,
        image: str,
        model: str = "5.0-lite",
        size: str = "2K",
        output_format: str = "png",
        watermark: bool = False,
    ) -> GenerationResponse:
        """
        图生图 (单图输入单图输出)
        
        Args:
            prompt: 提示词
            image: 输入图片 URL 或 Base64
            model: 模型别名
            size: 图像尺寸
            output_format: 输出格式
            watermark: 是否添加水印
        
        Returns:
            GenerationResponse: 生成结果
        """
        return self.generate(
            prompt=prompt,
            model=model,
            image=image,
            size=size,
            output_format=output_format,
            watermark=watermark,
            sequential_image_generation="disabled"
        )

    def multi_image_to_image(
        self,
        prompt: str,
        images: List[str],
        model: str = "5.0-lite",
        size: str = "2K",
        output_format: str = "png",
        watermark: bool = False,
    ) -> GenerationResponse:
        """
        多图融合 (多图输入单图输出)
        
        Args:
            prompt: 提示词
            images: 输入图片 URL 或 Base64 列表
            model: 模型别名
            size: 图像尺寸
            output_format: 输出格式
            watermark: 是否添加水印
        
        Returns:
            GenerationResponse: 生成结果
        """
        return self.generate(
            prompt=prompt,
            model=model,
            image=images,
            size=size,
            output_format=output_format,
            watermark=watermark,
            sequential_image_generation="disabled"
        )

    def generate_sequential(
        self,
        prompt: str,
        model: str = "5.0-lite",
        image: Union[str, List[str]] = None,
        size: str = "2K",
        output_format: str = "png",
        watermark: bool = False,
        max_images: int = 4,
    ) -> GenerationResponse:
        """
        组图生成
        
        Args:
            prompt: 提示词
            model: 模型别名
            image: 可选的输入图片
            size: 图像尺寸
            output_format: 输出格式
            watermark: 是否添加水印
            max_images: 最大生成图片数量
        
        Returns:
            GenerationResponse: 生成结果
        """
        return self.generate(
            prompt=prompt,
            model=model,
            image=image,
            size=size,
            output_format=output_format,
            watermark=watermark,
            sequential_image_generation="auto",
            max_images=max_images
        )


def save_image_from_url(url: str, output_path: str) -> None:
    """从 URL 下载图片并保存"""
    import requests
    response = requests.get(url)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)


def save_image_from_b64(b64_data: str, output_path: str) -> None:
    """从 Base64 数据保存图片"""
    import base64
    image_data = base64.b64decode(b64_data)
    with open(output_path, "wb") as f:
        f.write(image_data)
