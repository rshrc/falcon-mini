def get_serial_number():
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line.startswith('Serial'):
                return line.split(':')[1].strip()
    return None


if __name__=='__main__':
    serial_number = get_serial_number()
    if serial_number:
        print(f"Serial Number: {serial_number}")
    else:
        print("Serial Number not found.")