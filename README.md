# Seedream API Python 客户端

基于火山引擎方舟大模型服务平台的 Seedream 图片生成 API Python 客户端。

## 功能特性

- ✅ 文生图 (Text to Image)
- ✅ 图生图 (Image to Image) - 单图输入
- ✅ 多图融合 (Multi-image to Image) - 多图输入
- ✅ 组图生成 (Sequential Image Generation)
- ✅ 联网搜索 (Web Search) - 仅 Seedream 5.0 lite
- ✅ 支持 Base64 编码输入输出
- ✅ 支持代理配置

## 安装

```bash
cd seedream-api
pip3 install -r requirements.txt
```

国内服务无需代理，如果需要访问海外服务：
```bash
pip3 install -r requirements.txt -i http://127.0.0.1:1087
```

## 依赖

- volcengine-python-sdk[ark]
- requests

## 快速开始

### 1. 设置 API Key

```python
# 方式一: 环境变量
import os
os.environ["ARK_API_KEY"] = "your-api-key"

# 方式二: 代码中传入
client = SeedreamClient(api_key="your-api-key")
```

### 2. 基础用法

```python
from client import SeedreamClient

client = SeedreamClient()

# 文生图
response = client.text_to_image(
    prompt="一只可爱的橘猫坐在窗台上",
    size="2K"
)
print(response.data[0].url)
```

## 使用示例

### 文生图

```python
from client import SeedreamClient

client = SeedreamClient(api_key="your-api-key")

response = client.text_to_image(
    prompt="充满活力的特写编辑肖像，模特眼神犀利，头戴雕塑感帽子",
    model="5.0-lite",  # 可选: 5.0-lite, 4.5, 4.0, 3.0-t2i
    size="2K",
    output_format="png",  # 仅 5.0-lite 支持 png
    watermark=False
)
print(response.data[0].url)
```

### 图生图

```python
response = client.image_to_image(
    prompt="将图片转为水彩画风格",
    image="https://example.com/input.png",
    size="2K"
)
```

### 多图融合

```python
response = client.multi_image_to_image(
    prompt="将图1的服装换为图2的服装",
    images=[
        "https://example.com/image1.png",
        "https://example.com/image2.png"
    ]
)
```

### 组图生成

```python
response = client.generate_sequential(
    prompt="生成一组4张连贯插画，展现四季变迁",
    model="5.0-lite",
    max_images=4
)

for i, img in enumerate(response.data):
    print(f"图片 {i+1}: {img.url}")
```

### 联网搜索

```python
response = client.generate(
    prompt="制作一张北京今日天气预报图",
    model="5.0-lite",
    web_search=True  # 启用联网搜索
)

print(f"图片: {response.data[0].url}")
print(f"搜索次数: {response.usage.tool_usage_web_search}")
```

### 使用代理

```python
# 如果需要使用代理
client = SeedreamClient(
    api_key="your-api-key",
    proxy="http://127.0.0.1:1087"
)
```

## 命令行工具

项目提供了命令行工具 `main.py`:

```bash
# 文生图
python main.py -p "一只可爱的猫" --size 2K -o ./output

# 图生图
python main.py -p "将图片转为油画风格" -i "https://example.com/input.png" -o ./output

# 组图模式
python main.py -p "生成一组4张科幻场景" --sequential --max-images 4 -o ./output

# 联网搜索
python main.py -p "北京今日天气" --web-search -o ./output
```

### 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| --api-key | -k | API Key | 环境变量 ARK_API_KEY |
| --prompt | -p | 提示词 | (必填) |
| --model | -m | 模型 (5.0-lite/4.5/4.0) | 5.0-lite |
| --image | -i | 输入图片 URL | - |
| --size | -s | 图像尺寸 | 2K |
| --output-format | -f | 输出格式 | png |
| --watermark | -w | 添加水印 | False |
| --sequential | - | 启用组图模式 | False |
| --max-images | - | 最大图片数 | 4 |
| --web-search | - | 启用联网搜索 | False |
| --output | -o | 输出目录 | ./output |
| --proxy | -x | 代理地址 | - |

## 支持的模型

| 模型 | 别名 | 支持功能 |
|------|------|----------|
| Seedream 5.0 lite | 5.0-lite | 文生图、图生图、组图、联网搜索、流式输出、png输出 |
| Seedream 4.5 | 4.5 | 文生图、图生图、组图、jpeg输出 |
| Seedream 4.0 | 4.0 | 文生图、图生图、组图、jpeg输出 |
| Seedream 3.0 T2I | 3.0-t2i | 文生图、seed参数 |
| Seededit 3.0 I2I | 3.0-i2i | 图生图、seed参数 |

## 图像尺寸

### Seedream 5.0 lite / 4.5
- 方式1: `2K`, `3K`, `4K`
- 方式2: 像素值，如 `2048x2048`, `2848x1600`

### Seedream 4.0
- 方式1: `1K`, `2K`, `4K`
- 方式2: 像素值

### Seedream 3.0
- 固定: `1024x1024`

## 注意事项

1. API Key 需要在[火山引擎控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey)获取
2. 使用前需要先开通模型服务
3. 生成的图片 URL 会在 24 小时后失效，请及时下载保存
4. 国内服务无需代理，代理仅用于海外服务

## 目录结构

```
seedream-api/
├── config.py      # 配置文件 (模型ID、常量等)
├── client.py      # API 客户端核心代码
├── main.py        # 命令行工具
├── examples.py    # 使用示例
├── requirements.txt
└── README.md
```

## 许可证

MIT License
