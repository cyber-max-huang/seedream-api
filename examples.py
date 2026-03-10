"""
Seedream API 使用示例
"""
from client import SeedreamClient, save_image_from_url, save_image_from_b64


# 方式一: 直接使用 (需要设置环境变量 ARK_API_KEY)
def example_basic():
    """基础用法"""
    client = SeedreamClient()
    
    # 文生图
    response = client.text_to_image(
        prompt="一只可爱的橘猫坐在窗台上，阳光透过窗帘洒在它身上",
        size="2K"
    )
    
    if response.data[0].url:
        print(f"图片 URL: {response.data[0].url}")
        # save_image_from_url(response.data[0].url, "cat.png")


# 方式二: 传入 API Key
def example_with_api_key():
    """传入 API Key"""
    client = SeedreamClient(api_key="your-api-key-here")
    
    response = client.text_to_image(
        prompt="一张科技感的城市夜景，高楼大厦，霓虹灯光",
        size="2K",
        watermark=False
    )
    print(response.data[0].url)


def example_text_to_image():
    """文生图示例"""
    client = SeedreamClient(api_key="your-api-key-here")
    
    # 使用模型别名
    response = client.text_to_image(
        prompt="充满活力的特写编辑肖像，模特眼神犀利，头戴雕塑感帽子",
        model="5.0-lite",  # 可选: 5.0-lite, 4.5, 4.0, 3.0-t2i
        size="2K",
        output_format="png",  # 仅 5.0-lite 支持 png
        watermark=False
    )
    
    print(f"生成图片数: {len(response.data)}")
    for i, img in enumerate(response.data):
        print(f"图片 {i+1}: {img.url}, 尺寸: {img.size}")


def example_image_to_image():
    """图生图示例"""
    client = SeedreamClient(api_key="your-api-key-here")
    
    response = client.image_to_image(
        prompt="将图片转为黑白素描风格",
        image="https://example.com/input_image.png",
        model="5.0-lite",
        size="2K"
    )
    
    print(f"生成图片数: {len(response.data)}")
    for i, img in enumerate(response.data):
        print(f"图片 {i+1}: {img.url}")


def example_multi_image():
    """多图融合示例"""
    client = SeedreamClient(api_key="your-api-key-here")
    
    response = client.multi_image_to_image(
        prompt="将图1的服装换为图2的服装",
        images=[
            "https://example.com/image1.png",
            "https://example.com/image2.png"
        ],
        model="5.0-lite",
        size="2K"
    )
    
    print(f"生成图片数: {len(response.data)}")
    for i, img in enumerate(response.data):
        print(f"图片 {i+1}: {img.url}")


def example_sequential():
    """组图生成示例"""
    client = SeedreamClient(api_key="your-api-key-here")
    
    # 文生组图
    response = client.generate_sequential(
        prompt="生成一组4张连贯插画，核心为同一庭院一角的四季变迁",
        model="5.0-lite",
        size="2K",
        max_images=4
    )
    
    print(f"生成图片数: {len(response.data)}")
    for i, img in enumerate(response.data):
        print(f"图片 {i+1}: {img.url}, 尺寸: {img.size}")
    
    # 打印使用量
    if response.usage:
        print(f"使用量: {response.usage.generated_images} 张图片")


def example_with_base64():
    """使用 Base64 编码输入图片"""
    client = SeedreamClient(api_key="your-api-key-here")
    
    # 读取本地图片并转为 Base64
    with open("input.png", "rb") as f:
        import base64
        b64_image = base64.b64encode(f.read()).decode("utf-8")
        # 需要符合格式: data:image/png;base64,xxx
        b64_image = f"data:image/png;base64,{b64_image}"
    
    response = client.image_to_image(
        prompt="将图片转为水彩画风格",
        image=b64_image,
        size="2K"
    )
    
    print(f"图片 URL: {response.data[0].url}")


def example_web_search():
    """联网搜索示例 (仅 Seedream 5.0 lite 支持)"""
    client = SeedreamClient(api_key="your-api-key-here")
    
    response = client.generate(
        prompt="制作一张北京今日天气预报图，现代扁平化插画风格",
        model="5.0-lite",
        size="2K",
        web_search=True  # 启用联网搜索
    )
    
    print(f"图片 URL: {response.data[0].url}")
    
    # 查看联网搜索使用次数
    if response.usage and response.usage.tool_usage_web_search > 0:
        print(f"联网搜索次数: {response.usage.tool_usage_web_search}")


def example_with_proxy():
    """使用代理示例"""
    # 如果需要使用代理
    client = SeedreamClient(
        api_key="your-api-key-here",
        proxy="http://127.0.0.1:1087"  # 代理地址
    )
    
    response = client.text_to_image(prompt="一只可爱的猫")
    print(response.data[0].url)


def example_full_params():
    """完整参数示例"""
    client = SeedreamClient(api_key="your-api-key-here")
    
    response = client.generate(
        prompt="一只可爱的柴犬在草地上奔跑",
        model="5.0-lite",
        image="https://example.com/dog.png",  # 可选
        size="2048x2048",  # 也可以用像素值
        output_format="png",
        response_format="url",
        watermark=False,
        sequential_image_generation="disabled",
        # max_images=4,  # 组图模式时使用
        # seed=42,  # 仅 3.0 支持
        # guidance_scale=5.0,  # 仅 3.0 支持
        # stream=False,  # 仅 5.0 支持
        # web_search=False,  # 仅 5.0 支持
    )
    
    print(f"响应: model={response.model}, created={response.created}")
    print(f"图片: {response.data[0].url}")


if __name__ == "__main__":
    # 运行示例
    print("=== 文生图示例 ===")
    # example_text_to_image()
