#!/usr/bin/env python3

import pexpect
import sys
import time

def test_crash_prompt():
    """Test crash prompt detection directly."""
    print("Testing crash prompt detection...")
    
    # Start crash utility
    cmd = "crash /usr/lib/debug/lib/modules/4.18.0-553.22.1.el8_lustre.x86_64/vmlinux /var/crash/127.0.0.1-2025-09-19-15:54:12/vmcore"
    print(f"Starting: {cmd}")
    
    try:
        session = pexpect.spawn(cmd, timeout=180)
        session.logfile_read = sys.stdout.buffer  # Log everything to stdout
        
        print("\nWaiting for crash to initialize...")
        
        # Multiple prompt patterns to try
        prompts = [
            r'crash> ',           # Standard prompt with space
            r'crash>',            # Prompt without space
            r'crash>\s*',         # Prompt with optional whitespace
        ]
        
        expect_list = prompts + ['crash: .*', pexpect.TIMEOUT, pexpect.EOF]
        
        print(f"Expecting patterns: {expect_list[:len(prompts)]}")
        
        index = session.expect(expect_list, timeout=180)
        
        if index < len(prompts):
            print(f"\n✅ SUCCESS: Found crash prompt (pattern {index}: '{prompts[index]}')")
            
            # Try a simple command
            print("\nTrying 'help' command...")
            session.sendline('help')
            
            # Wait for prompt again
            index2 = session.expect(expect_list, timeout=30)
            if index2 < len(prompts):
                print(f"✅ Command completed successfully (pattern {index2})")
                output = session.before.decode('utf-8', errors='ignore')
                print(f"Output length: {len(output)} characters")
                print("First 200 chars of output:")
                print(output[:200])
            else:
                print(f"❌ Command failed, index: {index2}")
                
        elif index == len(prompts):  # Error pattern
            error_msg = session.after.decode('utf-8', errors='ignore')
            print(f"❌ Crash error: {error_msg}")
        elif index == len(prompts) + 1:  # Timeout
            print("❌ Timeout waiting for crash prompt")
        else:  # EOF
            print("❌ Crash exited unexpectedly")
            
        # Clean up
        try:
            session.sendline('quit')
            session.expect(pexpect.EOF, timeout=5)
        except:
            pass
        session.close()
        
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_crash_prompt()
