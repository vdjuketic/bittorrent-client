def write_to_file(content, output_file):
    with open(output_file, "wb") as f:
        f.write(content)