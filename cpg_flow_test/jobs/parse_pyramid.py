"""
simple python job, with no further imports
"""


def parse_pyramid_job(input_file: str) -> str:
    """
    This is a simple example of a job that prints the contents of a file.

    Args:
        input_file (str): the path to the file to print
    """

    with open(input_file) as f:
        contents = f.read()

    print(f'Contents of {input_file}:')
    print(contents)
    return contents
