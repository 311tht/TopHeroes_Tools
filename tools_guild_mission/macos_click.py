import subprocess
''
def macos_click(x, y):
    """
    Click chuột ảo tại vị trí (x, y) trên macOS mà không di chuyển chuột thật.
    Yêu cầu quyền Accessibility cho Terminal/Python.
    """
    script = f'''osascript -e 'tell application "System Events" to set the mouse position to {{{x}, {y}}}\nclick (the first button of the first window whose value of attribute "AXFocused" is true)' '''
    subprocess.run(script, shell=True)
import time
import subprocess

def macos_click(x, y):
    """
    Click tại vị trí (x, y) trên macOS bằng AppleScript mà không di chuyển chuột thật.
    """
    script = f'''osascript -e 'tell application "System Events" to click at {{{x}, {y}}}' '''
    subprocess.run(script, shell=True)

if __name__ == "__main__":
    # Test click tại vị trí (100, 100)
    macos_click(100, 100)
    time.sleep(1)
    macos_click(200, 200)
