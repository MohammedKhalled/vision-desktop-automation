from src.vision.icon_grounding import IconGrounder
from src.services.posts_api import fetch_posts
from src.automation.notepad import (
    open_notepad_at,
    close_notepad,
    fallback_launch_notepad
)
from src.automation.typing import type_post
from src.utils.paths import get_desktop_project_dir, cleanup_previous_posts
from src.config import POST_LIMIT


def main():

    print("=" * 60)
    print("=== Desktop Automation with Vision-Based Icon Grounding ===")
    print("=" * 60)
    print()
    
    
    print("Step 1: Fetching posts from API...")
    posts = fetch_posts(POST_LIMIT)
    if not posts:
        print(" ERROR: No posts available. API unavailable.")
        return

    print(f" Successfully fetched {len(posts)} posts.")
    print()
    
    
    print("Step 2: Setting up save directory...")
    save_dir = get_desktop_project_dir()
    print(f" Save directory: {save_dir}")
    print()
    
    
    print("Step 3: Cleaning up previous posts...")
    cleanup_previous_posts(save_dir)
    print()

    
    print("Step 4: Initializing icon grounder...")
    grounder = IconGrounder()
    print(" Icon grounder ready")
    print()
    
    
    successful_posts = 0
    failed_posts = 0

    
    print("=" * 60)
    print("Processing Posts...")
    print("=" * 60)
    
    for i, post in enumerate(posts, 1):
        print()
        print(f"[{i}/{len(posts)}] Processing Post #{post['id']}: {post['title'][:40]}...")
        print("-" * 60)
        
        
        coords = grounder.find_notepad_icon()

        if coords:
            print(f" Notepad icon found at ({coords[0]}, {coords[1]})")
            opened = open_notepad_at(*coords)
        else:
            print(" Visual grounding failed - using fallback launcher")
            opened = fallback_launch_notepad()

        if not opened:
            print(" ERROR: Notepad failed to open. Skipping this post.")
            failed_posts += 1
            continue

        
        save_success = type_post(post, save_dir)
        
        if not save_success:
            print(" ERROR: Failed to save post")
            failed_posts += 1
        else:
            successful_posts += 1
        
        
        close_success = close_notepad()
        
        if not close_success:
            print(" WARNING: Notepad may still be open")
            
        
        print("-" * 60)
        print(f"Status: Post #{post['id']} - {' SUCCESS' if save_success else ' FAILED'}")

    
    print()
    print("=" * 60)
    print("=== Automation Complete ===")
    print("=" * 60)
    print(f"Total posts: {len(posts)}")
    print(f"Successful: {successful_posts}")
    print(f"Failed: {failed_posts}")
    print(f"Success rate: {(successful_posts/len(posts)*100):.1f}%")
    print()
    print(f"Files saved to: {save_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()