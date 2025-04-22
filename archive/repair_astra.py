"""
Script to repair Astra's conversation handling
"""
import os
import sys
import json

def backup_file(filename):
    """Create a backup of a file"""
    if os.path.exists(filename):
        backup_name = f"{filename}.bak"
        i = 1
        while os.path.exists(backup_name):
            backup_name = f"{filename}.bak{i}"
            i += 1
        
        with open(filename, 'r', encoding='utf-8') as src:
            with open(backup_name, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        print(f"Created backup: {backup_name}")
        return True
    return False

def patch_astra_chat():
    """Patch the astra_chat.py file to fix the conversation handling issue"""
    filename = "astra_chat.py"
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return False
    
    # Create a backup
    backup_file(filename)
    
    # Read the file
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The specific issue you're describing sounds like it might be related to how
    # the conversation context is handled in the generate_response method
    
    # Look for the generate_response method
    if "def generate_response(" in content:
        print("Found generate_response method in astra_chat.py")
        
        # Check if the method needs to be patched
        if "messages = [" in content and "get_relevant_context" in content:
            # This is the section where the conversation context is being formed
            # We need to modify it to ensure we're using the right context
            
            # Original code might look something like this:
            original_code = "        # Формируем сообщения для API\n        messages = [\n            {\"role\": \"system\", \"content\": system_prompt}\n        ]\n        \n        # Добавляем релевантный контекст к сообщениям\n        messages.extend(relevant_context)"
            
            # New code should include the user's message at the end to ensure Astra responds to it
            new_code = "        # Формируем сообщения для API\n        messages = [\n            {\"role\": \"system\", \"content\": system_prompt}\n        ]\n        \n        # Добавляем релевантный контекст к сообщениям\n        messages.extend(relevant_context)\n        \n        # Обязательно добавляем текущее сообщение пользователя в конец\n        messages.append({\"role\": \"user\", \"content\": user_message})"
            
            # Try to replace the code
            new_content = content.replace(original_code, new_code)
            
            # If we couldn't find the exact original code, try a more targeted approach
            if new_content == content:
                print("Could not find the exact code pattern to replace. Trying a targeted approach...")
                
                # This is a more targeted approach using string insertion
                target = "        # Формируем сообщения для API\n        messages = [\n            {\"role\": \"system\", \"content\": system_prompt}\n        ]"
                replacement = "        # Формируем сообщения для API\n        messages = [\n            {\"role\": \"system\", \"content\": system_prompt}\n        ]"
                
                target2 = "        # Добавляем релевантный контекст к сообщениям\n        messages.extend(relevant_context)"
                replacement2 = "        # Добавляем релевантный контекст к сообщениям\n        messages.extend(relevant_context)\n        \n        # Обязательно добавляем текущее сообщение пользователя в конец\n        messages.append({\"role\": \"user\", \"content\": user_message})"
                
                new_content = content.replace(target2, replacement2)
                
                if new_content == content:
                    # If we still couldn't modify it, let's try a more aggressive approach
                    print("Still couldn't find the exact pattern. Attempting a more generic fix...")
                    
                    # Look for the section where messages are extended with context
                    # and add the current user message right after it
                    lines = content.split('\n')
                    modified_lines = []
                    
                    extend_found = False
                    for line in lines:
                        modified_lines.append(line)
                        if "messages.extend" in line and "relevant_context" in line:
                            extend_found = True
                            modified_lines.append("")
                            modified_lines.append("        # Обязательно добавляем текущее сообщение пользователя в конец")
                            modified_lines.append("        messages.append({\"role\": \"user\", \"content\": user_message})")
                    
                    if extend_found:
                        new_content = '\n'.join(modified_lines)
                        print("Generic fix applied")
                    else:
                        print("Could not find a suitable location to apply the fix")
                        return False
            
            # Write the modified content back to the file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("Successfully patched astra_chat.py")
            return True
        else:
            print("Could not find the relevant code sections to patch")
    else:
        print("Could not find generate_response method in astra_chat.py")
    
    return False

def patch_conversation_manager():
    """Patch the conversation_manager.py file to fix history handling"""
    filename = "conversation_manager.py"
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return False
    
    # Create a backup
    backup_file(filename)
    
    # Read the file
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for the get_relevant_context method
    if "def get_relevant_context(" in content:
        print("Found get_relevant_context method in conversation_manager.py")
        
        # Add a safety check to ensure the current message is included in context
        # Look for the return statement in get_relevant_context
        if "return " in content and "messages" in content:
            # Find the return statement
            lines = content.split('\n')
            modified_lines = []
            
            for i, line in enumerate(lines):
                modified_lines.append(line)
                if "return " in line and "messages" in line:
                    # Insert a comment and safety check before the return
                    indent = line[:line.find("return")]
                    modified_lines[-1] = f"{indent}# Ensure the context is not empty\n{indent}if not {line.strip()[7:]}:\n{indent}    print(\"Warning: Empty context! Returning basic message list.\")\n{indent}    return []\n{indent}{line.strip()}"
            
            # Write the modified content back to the file
            new_content = '\n'.join(modified_lines)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("Successfully patched conversation_manager.py")
            return True
        else:
            print("Could not find suitable return statement to patch")
    else:
        print("Could not find get_relevant_context method in conversation_manager.py")
    
    return False

def fix_api_key():
    """Ensure the API key is properly set in all files"""
    env_api_key = os.environ.get("OPENAI_API_KEY")
    if not env_api_key:
        print("No API key found in environment variables")
        return False
    
    # Check and update API key in astra_chat.py
    chat_file = "astra_chat.py"
    if os.path.exists(chat_file):
        backup_file(chat_file)
        
        with open(chat_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if API_KEY is defined and needs updating
        if "API_KEY =" in content:
            print("Found API_KEY in astra_chat.py")
            
            # Update the API key
            lines = content.split('\n')
            modified_lines = []
            
            for line in lines:
                if "API_KEY =" in line:
                    modified_lines.append(f'API_KEY = "{env_api_key}"')
                else:
                    modified_lines.append(line)
            
            # Write the modified content back to the file
            new_content = '\n'.join(modified_lines)
            with open(chat_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("Successfully updated API key in astra_chat.py")
            return True
    
    return False

def reset_conversation_history():
    """Reset the conversation history file"""
    data_dir = "astra_data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
    
    history_file = os.path.join(data_dir, "conversation_history.jsonl")
    
    if os.path.exists(history_file):
        backup_file(history_file)
        
        # Create an empty history file
        with open(history_file, 'w', encoding='utf-8') as f:
            pass
        
        print(f"Reset conversation history: {history_file}")
        return True
    else:
        print(f"Conversation history file not found: {history_file}")
    
    return False

def main():
    print("🔧 Astra Repair Tool 🔧")
    print("This tool will attempt to fix common issues with Astra's responses.")
    
    fixed_something = False
    
    # Try to patch astra_chat.py
    if patch_astra_chat():
        fixed_something = True
    
    # Try to patch conversation_manager.py
    if patch_conversation_manager():
        fixed_something = True
    
    # Ensure API key is properly set
    if fix_api_key():
        fixed_something = True
    
    # Reset conversation history
    if reset_conversation_history():
        fixed_something = True
    
    if fixed_something:
        print("\n✅ Repairs completed. Please restart Astra and try again.")
    else:
        print("\n⚠️ No repairs were made. The issue may be more complex.")
        print("Try running the debug_astra.py script for more detailed diagnostics.")

if __name__ == "__main__":
    main()