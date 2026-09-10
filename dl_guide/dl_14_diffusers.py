import torch
from diffusers import StableDiffusionPipeline

# 加载预训练模型
model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, cache_dir="./models")
pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

# 输入文本提示
prompt = "a beautiful landscape with mountains and lake"

# 生成图像
with torch.no_grad():
    image = pipe(prompt).images[0]

# 保存图像
image.save("generated_image.png")
print(f"提示: {prompt}")
print("图像已保存为 generated_image.png")
