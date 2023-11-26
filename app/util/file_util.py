import logging as log


def write_to_file(content, output_file):
    try:
        with open(output_file, "wb") as f:
            f.write(content)
    except:
        log.error("Failed writing to file")
