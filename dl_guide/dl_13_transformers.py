import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# 加载预训练模型和分词器
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name, cache_dir="./models")
model = GPT2LMHeadModel.from_pretrained(model_name, cache_dir="./models")

# 输入文本
text = "Hello, this is a simple"

# 分词和编码
inputs = tokenizer(text, return_tensors="pt")

# 生成文本
with torch.no_grad():
    outputs = model.generate(inputs['input_ids'], max_length=20, do_sample=True)

# 解码输出
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"输入: {text}")
print(f"输出: {generated_text}")  # Hello, this is a simple test case of sending and receiving code. You can see this by simply
