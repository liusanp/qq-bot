import importlib
from src.utils.config import get as get_config
    
    
def convert_to_camel_case(snake_str): 
    return ''.join(word.title() for word in snake_str.split('_'))
    
    
def ability_factory(type: str, classz):
    chat_type = get_config(f"{type}_type")
    # 指定子类模块的完整路径
    module_name = f'src.client.ability.{chat_type}_{type}'
    class_name = convert_to_camel_case(f'{chat_type}_{type}')

    try:
        # 动态导入模块
        module = importlib.import_module(module_name)
        # 从模块获取类
        chat_class = getattr(module, class_name)
        # 实例化并返回子类
        return chat_class()
    except (ImportError, AttributeError) as e:
        print(f"Failed to load {class_name}: {e}. Falling back to base class.")
        # 使用基类作为后备实现
        return classz()