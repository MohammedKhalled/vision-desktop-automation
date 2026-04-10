import os

def type_post(post, save_dir):

   
    title = post.get('title', '')
    body = post.get('body', '')
    content = f"Title: {title}\n\n{body}"
    
    
    filename = f"post_{post['id']}.txt"
    full_path = os.path.join(save_dir, filename)
    
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"   File saved: {filename} ({file_size} bytes)")
            return True
        else:
            print(f"   ERROR: File not saved")
            return False
            
    except Exception as e:
        print(f"   ERROR saving file: {e}")
        return False