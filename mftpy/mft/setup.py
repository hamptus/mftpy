from cx_Freeze import setup, Executable


exe = Executable(
    script="gui.pyw",
    base="Win32GUI",)

setup(
    name="MFT Parser",
    version="1.0",
    description="An MFT record parser",
    executables = [exe])
