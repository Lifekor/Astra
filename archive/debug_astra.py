"""
Debugging script to verify Astra's integration and functionality
"""
import os
import sys
import json

# Try to import the necessary modules
try:
    from astra_app import AstraInterface
    from astra_memory import AstraMemory
    from astra_chat import AstraChat
    print("✅ Core modules successfully imported")
except ImportError as e:
    print(f"❌ Failed to import core modules: {e}")
    sys.exit(1)

# Check if updated modules exist and can be imported
updated_modules = [
    ("intent_analyzer", "IntentAnalyzer"),
    ("memory_extractor", "MemoryExtractor"),
    ("astra_memory_update", "update_astra_memory"),
    ("conversation_manager_update", "update_conversation_manager"),
    ("astra_chat_update", "update_astra_chat"),
    ("emotional_visualizer", "EmotionalVisualizer"),
    ("astra_diary", "AstraDiary"),
    ("astra_home", "AstraHome")
]

for module_name, class_name in updated_modules:
    try:
        module = __import__(module_name)
        
        # Verify the class exists in the module
        if hasattr(module, class_name):
            print(f"✅ Module {module_name} with {class_name} found")
        else:
            print(f"⚠️ Module {module_name} found, but {class_name} is missing")
    except ImportError:
        print(f"❌ Module {module_name} could not be imported")

# Check API key configuration
api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    print(f"✅ API key found in environment: {api_key[:5]}...{api_key[-4:]}")
else:
    print("❌ API key not found in environment variables")

# Check if API key is in astra_chat.py
try:
    with open("astra_chat.py", "r", encoding="utf-8") as f:
        chat_content = f.read()
        if "API_KEY =" in chat_content:
            print("✅ API key definition found in astra_chat.py")
        else:
            print("⚠️ API key definition not found in astra_chat.py")
except:
    print("❌ Could not check astra_chat.py for API key")

# Initialize Astra and check components
print("\n--- Initializing Astra ---")
try:
    astra = AstraInterface()
    print("✅ AstraInterface initialized")
    
    # Check if memory was updated
    if hasattr(astra.memory, 'autonomous_memory'):
        print(f"✅ Memory has autonomous_memory attribute: {astra.memory.autonomous_memory}")
    else:
        print("❌ Memory does not have autonomous_memory attribute")
    
    # Check if intent analyzer was added
    if hasattr(astra.memory, 'intent_analyzer'):
        print("✅ Memory has intent_analyzer attribute")
    else:
        print("❌ Memory does not have intent_analyzer attribute")
    
    # Check conversation manager
    if hasattr(astra.chat, 'conversation_manager'):
        print("✅ Chat has conversation_manager attribute")
        
        # Check if conversation manager was updated
        if hasattr(astra.chat.conversation_manager, 'autonomous_mode'):
            print(f"✅ Conversation manager has autonomous_mode attribute: {astra.chat.conversation_manager.autonomous_mode}")
        else:
            print("❌ Conversation manager does not have autonomous_mode attribute")
    else:
        print("❌ Chat does not have conversation_manager attribute")
    
    # Check if diary was integrated
    if hasattr(astra.memory, 'diary'):
        print("✅ Memory has diary attribute")
    else:
        print("❌ Memory does not have diary attribute")
    
    # Check if home was integrated
    if hasattr(astra.memory, 'home'):
        print("✅ Memory has home attribute")
    else:
        print("❌ Memory does not have home attribute")
    
    # Check if visualizer was integrated
    if hasattr(astra, 'visualizer'):
        print("✅ Astra has visualizer attribute")
    else:
        print("❌ Astra does not have visualizer attribute")
    
    # Check for format_response_with_emotions method
    if hasattr(astra, 'format_response_with_emotions'):
        print("✅ Astra has format_response_with_emotions method")
    else:
        print("❌ Astra does not have format_response_with_emotions method")
    
    # Test a simple message (won't print the actual response)
    print("\n--- Testing message processing ---")
    try:
        response = astra.process_message("Hello, how are you today?")
        print(f"✅ Message processed successfully (response length: {len(response)})")
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        import traceback
        traceback.print_exc()
    
    # Examine memory files
    print("\n--- Checking memory files ---")
    data_dir = "astra_data"
    if os.path.exists(data_dir):
        print(f"✅ Data directory '{data_dir}' exists")
        
        for filename in [
            "astra_core_prompt.txt",
            "emotion_memory.json",
            "tone_memory.json",
            "subtone_memory.json",
            "flavor_memory.json",
            "current_state.json",
            "conversation_history.jsonl"
        ]:
            file_path = os.path.join(data_dir, filename)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"✅ File '{filename}' exists (size: {size} bytes)")
                
                # For JSON files, try to check their structure
                if filename.endswith('.json'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, dict):
                                print(f"   Keys: {', '.join(data.keys())}")
                            elif isinstance(data, list):
                                print(f"   List length: {len(data)}")
                    except:
                        print(f"   Could not parse JSON content")
            else:
                print(f"❌ File '{filename}' does not exist")
    else:
        print(f"❌ Data directory '{data_dir}' does not exist")

except Exception as e:
    print(f"❌ Error initializing Astra: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Debugging complete ---")