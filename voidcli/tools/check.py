from voidcli.tools.filesystem import FileSystemTool

tool = FileSystemTool()

print(
    tool.execute(
        action="write",
        path="hello.txt",
        content="Hello "
    )
)

print(
    tool.execute(
        action="read",
        path="hello.txt"
    )
)
