"""
Seedream API 命令行工具
"""
import argparse
import os
import sys

from client import SeedreamClient, save_image_from_url, save_image_from_b64
import config


def main():
    parser = argparse.ArgumentParser(description="Seedream 图片生成 CLI 工具")
    parser.add_argument("--api-key", "-k", help="火山引擎 API Key", default=None)
    parser.add_argument("--prompt", "-p", help="图片描述提示词", required=True)
    parser.add_argument("--model", "-m", default=config.MODEL_SEEDREAM_5_0_LITE, help="模型 ID")
    parser.add_argument("--image", "-i", help="输入图片 URL (图生图模式)")
    parser.add_argument("--size", "-s", default="2K", help="图像尺寸")
    parser.add_argument("--output-format", "-f", default="png", choices=["png", "jpeg"], help="输出格式")
    parser.add_argument("--response-format", "-r", default="url", choices=["url", "b64_json"], help="返回格式")
    parser.add_argument("--watermark", "-w", action="store_true", help="添加水印")
    parser.add_argument("--sequential", action="store_true", help="启用组图模式")
    parser.add_argument("--max-images", type=int, default=4, help="最大生成图片数")
    parser.add_argument("--output", "-o", help="输出目录", default="./output")
    
    args = parser.parse_args()

    # 获取 API Key
    api_key = args.api_key or os.getenv("ARK_API_KEY")
    if not api_key:
        print("错误: 请通过 --api-key 参数或设置 ARK_API_KEY 环境变量提供 API Key")
        sys.exit(1)

    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)

    # 创建客户端
    client = SeedreamClient(api_key=api_key)

    # 确定模式
    if args.sequential:
        print(f"[组图模式] 正在生成最多 {args.max_images} 张图片...")
        response = client.generate_sequential(
            prompt=args.prompt,
            model=args.model,
            image=args.image,
            size=args.size,
            output_format=args.output_format,
            watermark=args.watermark,
            max_images=args.max_images
        )
    elif args.image:
        print(f"[图生图模式] 正在生成图片...")
        response = client.generate(
            prompt=args.prompt,
            model=args.model,
            image=args.image,
            size=args.size,
            output_format=args.output_format,
            response_format=args.response_format,
            watermark=args.watermark
        )
    else:
        print(f"[文生图模式] 正在生成图片...")
        response = client.text_to_image(
            prompt=args.prompt,
            model=args.model,
            size=args.size,
            output_format=args.output_format,
            watermark=args.watermark
        )

    # 处理结果
    if response.error:
        print(f"错误: {response.error.get('message', '未知错误')}")
        sys.exit(1)

    print(f"成功生成 {len(response.data)} 张图片:")
    for i, img in enumerate(response.data):
        if img.error:
            print(f"  图片 {i+1}: 生成失败 - {img.error.get('message', '未知错误')}")
            continue

        # 生成文件名
        ext = args.output_format
        filename = f"seedream_{response.created}_{i+1}.{ext}"
        filepath = os.path.join(args.output, filename)

        # 保存图片
        if args.response_format == "b64_json" and img.b64_json:
            save_image_from_b64(img.b64_json, filepath)
        elif img.url:
            save_image_from_url(img.url, filepath)
        
        print(f"  图片 {i+1}: {filepath}")
        if img.size:
            print(f"         尺寸: {img.size}")

    # 打印使用量统计
    if response.usage:
        print(f"\n使用量统计:")
        print(f"  生成图片数: {response.usage.generated_images}")
        print(f"  消耗 Token: {response.usage.output_tokens}")


if __name__ == "__main__":
    main()
