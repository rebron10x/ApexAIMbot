import onnxruntime

# 获取可用的提供程序
# available_providers = onnxruntime.get_available_providers()
# print("Available providers:", available_providers)
# all_providers = onnxruntime.get_all_providers()
# print("All providers:", all_providers)

print(onnxruntime.get_device())

print(onnxruntime.get_available_providers())